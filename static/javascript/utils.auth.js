import Vue from 'vue'
import VueCookies from 'vue-cookies'
import VueResource from 'vue-resource'


Vue.use(VueCookies)
Vue.use(VueResource)


let module = {
    _apiBase: null,
    _accessToken: null,
    _refreshToken: null,
    _clientId: null,
    _clientSecret: null,

    _apiUrl (path) {
        if (this._apiBase) {
            return `${this._apiBase}/${path}`
        }
        return path
    },

    setup (clientId = null, clientSecret = null, apiBase = null) {
        this._clientId = clientId
        this._clientSecret = clientSecret
        this._apiBase = apiBase
    },

    http (config = {}) {
        /**
         * Use this method to make calls requiring bearer token-based authorization header.
         * It is a wrapper for Vue.http with Authorization.
         *
         * @type {{headers: {Authorization: string}}}
         *
         */
        let configForResource = {
            headers: {
                Authorization: `Bearer ${this._accessToken}`
            }
        }

        configForResource = Object.assign(configForResource, config);
        return Vue.http(configForResource)
    },

    requireLogin (successFn = (data) => {}, loginPath = 'accounts/login/') {
        if (!this._clientId) {
            console.error(".setup function must be called at least once before `utils.auth.js` is put in use!")
        }

        this._accessToken = Vue.cookies.get('access_token')
        this._refreshToken = Vue.cookies.get('refresh_token')

        if (!this._accessToken) {
            window.location.href = this._apiUrl(loginPath)
            return
        }

        let promise = this.getUserData()

        promise.then(
            (response) => { successFn(response.data) },
            (error) => {
                let pro = this.useRefreshToken()

                pro.then((response) => {
                    this._accessToken = response.body.access_token
                    this._refreshToken = response.body.refresh_token

                    Vue.cookies.set('access_token', this._accessToken)
                    Vue.cookies.set('refresh_token', this._refreshToken)

                    this.getUserData().then(
                        (response) => { successFn(response.data) },
                        (error) => { console.error('Unexpected error', error) }
                    )
                }, (error) => {
                    Vue.cookies.remove('access_token')
                    Vue.cookies.remove('refresh_token')
                    window.location.href = this._apiUrl('accounts/login/')
                })
            })
    },

    getUserData () {
        return this.http({
            method: 'GET',
            url: this._apiUrl('api/users/me/')
        })
    },

    useRefreshToken () {
        return Vue.http({
            method: 'POST',
            url: this._apiUrl('o/token/'),
            emulateJSON: true,
            body: {
                grant_type:'refresh_token',
                refresh_token: this._refreshToken,
                client_id: this._clientId,
                client_secret: this._clientSecret,
            }
        })
    },

    logout (redirectUrl = 'accounts/login/') {
        Vue.http({
            method: 'POST',
            url: this._apiUrl('o/revoke_token/'),
            emulateJSON: true,
            body: {
                token: this._accessToken,
                client_id: this._clientId,
                client_secret: this._clientSecret
            }
        })
        Vue.cookies.remove('access_token')
        Vue.cookies.remove('refresh_token')
        window.location.href = this._apiUrl(redirectUrl);
    }
}

export default {
    install (Vue, options) {
        Vue.prototype.auth = module
    }
}
