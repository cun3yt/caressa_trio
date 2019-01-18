import Vue from 'vue'
import moment from 'moment'
import vars from '../.env'
import { Cookies } from 'quasar'

let authModule = {
  access_token: Cookies.get('access_token'),
  refresh_token: Cookies.get('refresh_token'),
  expiry_date: Cookies.get('expiry_date'),
  isRefreshRequired: function () {
    let tenMinutesAfter = moment().add(10, 'minutes')
    return tenMinutesAfter.isAfter(this.expiry_date)
  },
  checkState: function () {
    if (this.isRefreshRequired()) {
      this.token_refresh()
    }
    return !(this.access_token && this.refresh_token)
  },
  token_refresh: function () { // todo implement
    let data = `grant_type=refresh_token&client_id=${vars.CLIENT_ID}&client_secret=${vars.CLIENT_SECRET}&refresh_token=${this.refresh_token}`
    let url = `${vars.API_HOST}/o/token/`
    this.post(url, data, 'refresh')
  },
  get: function (url) {
    return Vue.http.get(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': `Bearer ${this.access_token}`
      }
    })
  },
  post: function (url, data, type) {
    if (type !== 'login') {
      return Vue.http.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'Authorization': `Bearer ${this.access_token}`
        }
      })
    } else {
      return Vue.http.post(url, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
      }).then(
        response => {
          Cookies.set('access_token', response.data.access_token, {expires: 10})
          Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
          Cookies.set('expiry_date', moment().add(response.data.expires_in, 'seconds'), {expires: 10})
          this.access_token = Cookies.get('access_token')
          this.refresh_token = Cookies.get('refresh_token')
          this.expiry_date = Cookies.get('expiry_date')
        }, response => {
          console.log('Auth Get Error', response)
          console.log('Auth Error')
        })
    }
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
