import Vue from 'vue'
import moment from 'moment'
import vars from '../.env'
import {Cookies} from 'quasar'
export const bus = new Vue()

let authModule = {
  access_token: Cookies.get('access_token'),
  refresh_token: Cookies.get('refresh_token'),
  expiry_date: Cookies.get('expiry_date'),
  isRefreshRequired: function () {
    let tenMinutesAfter = moment().add(10, 'minutes')
    return tenMinutesAfter.isAfter(this.expiry_date)
  },
  isLoggedOut: function () {
    console.log(this.expiry_date)
    console.log('is Refresh Req? ', this.isRefreshRequired())
    if (this.isRefreshRequired()) {
      this.tokenRefresh()
    }
    return !(this.access_token && this.refresh_token)
  },
  tokenRefresh: function () {
    let data = `grant_type=refresh_token&client_id=${vars.CLIENT_ID}&client_secret=${vars.CLIENT_SECRET}&refresh_token=${this.refresh_token}`
    let url = `${vars.API_HOST}/o/token/`
    this.post(url, data, 'refresh')
  },
  tokenRevoke: function () {
    let data = `client_id=${vars.CLIENT_ID}&client_secret=${vars.CLIENT_SECRET}&token=${this.access_token}`
    let url = `${vars.API_HOST}/o/revoke_token/`
    this.post(url, data, 'revoke').then(response => {
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
      Cookies.remove('expiry_date')
      this.access_token = Cookies.get('access_token')
      this.refresh_token = Cookies.get('refresh_token')
      this.expiry_date = Cookies.get('expiry_date')
    })
  },
  get: function (url) {
    return Vue.http.get(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': `Bearer ${this.access_token}`
      }
    })
  },
  post: function (url, data, type = 'update') {
    if (type === 'update') {
      return Vue.http.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'Authorization': `Bearer ${this.access_token}`
        }
      }).then(
        response => {
          console.log('Auth Success')
        }, response => {
          console.log('Auth Error')
        })
    } else if (type === 'refresh') {
      return Vue.http.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      }).then(
        response => {
          console.log('Refresh Token Auth Success')
          console.log(response)
          Cookies.set('access_token', response.data.access_token, {expires: 10})
          Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
          Cookies.set('expiry_date', moment().add(response.data.expires_in, 'seconds'), {expires: 10})
          this.access_token = Cookies.get('access_token')
          this.refresh_token = Cookies.get('refresh_token')
          this.expiry_date = Cookies.get('expiry_date')
        }, response => {
          console.log('Refresh Token Auth Error')
        })
    } else if (type === 'login') {
      return Vue.http.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      }).then(
        response => {
          console.log(response)
          Cookies.set('access_token', response.data.access_token, {expires: 10})
          Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
          Cookies.set('expiry_date', moment().add(response.data.expires_in, 'seconds'), {expires: 10})
          this.access_token = Cookies.get('access_token')
          this.refresh_token = Cookies.get('refresh_token')
          this.expiry_date = Cookies.get('expiry_date')
        }, response => {
          console.log('Auth Error')
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
    })
    // return Vue.http.delete(url, data)
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
