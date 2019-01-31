import Vue from 'vue'
import vars from '../.env'
import {Cookies} from 'quasar'
export const bus = new Vue()

let authModule = {
  access_token: Cookies.get('access_token'),
  refresh_token: Cookies.get('refresh_token'),
  isLoggedOut: function () {
    return !(this.access_token && this.refresh_token)
  },
  url: function (path) {
    let base = `${vars.API_HOST}`
    return base + path
  },
  login: function (data) {
    let vm = this
    return Vue.http({
      method: 'POST',
      url: vm.url('/o/token/'),
      emulateJSON: true,
      body: {
        grant_type: 'password',
        username: data.username,
        password: data.password
      },
      headers: {
        Authorization: 'Basic ' + `${vars.CLIENT_ID}` + ':' + `${vars.CLIENT_SECRET}`
      }
    }).then(response => {
      Cookies.set('access_token', response.data.access_token, {expires: 10})
      Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
    }, response => {
      console.log(response, 'Auth Error')
    })
  },
  refreshToken: function () {
    console.log('token refresh processing')
    let vm = this
    return Vue.http({
      method: 'POST',
      url: vm.url('o/token/'),
      emulateJSON: true,
      body: {
        grant_type: 'refresh_token',
        refresh_token: Cookies.get('refresh_token'),
        client_id: `${vars.CLIENT_ID}`,
        client_secret: `${vars.CLIENT_SECRET}`
      }
    }).then(response => {
      console.log(response, 'refresh success')
    }, response => {
      console.log(response, 'refresh error')
      Cookies.remove('access_token')
      Cookies.remove('access_token')
      this.access_token = Cookies.get('access_token')
      this.refresh_token = Cookies.get('refresh_token')
      bus.$emit('loginRedirect')
    })
  },
  tokenRevoke: function () {
    let vm = this
    return Vue.http({
      method: 'POST',
      url: vm.url('/o/revoke_token/'),
      emulateJSON: true,
      body: {
        token: this.access_token,
        client_id: `${vars.CLIENT_ID}`,
        client_secret: `${vars.CLIENT_SECRET}`
      }
    }).then(response => {
      console.log(response, 'Logged Out')
      Cookies.remove('access_token')
      Cookies.remove('access_token')
      this.access_token = Cookies.get('access_token')
      this.refresh_token = Cookies.get('refresh_token')
    }, response => {
      console.log(response, 'revoke error')
    })
  },
  get: function (url) {
    return Vue.http.get(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': `Bearer ${this.access_token}`
      }
    }).then(response => {
      console.log(response, 'get success')
    }, response => {
      console.log(response, 'get error')
      this.refresh_token()
      return this.get(url)
    })
  },
  post: function (url, data, type = 'update') {
    if (type === 'update') {
      return Vue.http({
        method: 'POST',
        url: url,
        emulateJSON: true,
        body: data,
        headers: {'Authorization': `Bearer ${this.access_token}`}
      }).then(response => {
        console.log(response, 'post success')
      }, response => {
        console.log(response, 'post error')
        this.refresh_token()
        return this.post(url, data)
      })
    }
  },
  delete: function (url, data) {
    return Vue.http({
      method: 'DELETE',
      url: url,
      emulateJSON: true,
      body: data,
      headers: {'Authorization': `Bearer ${this.access_token}`}
    }).then(response => {
      console.log(response, 'deletesuccess')
    }, response => {
      console.log(response, 'delete error')
      this.refresh_token()
      return this.delete(url, data)
    })
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
