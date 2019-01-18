import Vue from 'vue'
import moment from 'moment'

let authModule = {
  access_token: null,
  refresh_token: null,
  expiry_date: null,
  isRefreshRequired: function () {
    let tenMinAfter = moment().add(10, 'minutes')
    return tenMinAfter.isAfter(this.expiry_date)
  },
  checkState: function () {
    let refreshState = this.isRefreshRequired()
    return !(this.access_token && this.refresh_token)
  },
  token_refresh: function () { // todo implement
    return null
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
          console.log('Auth Success')
          this.access_token = response.data.access_token
          this.refresh_token = response.data.refresh_token
          this.expiry_date = moment().add(response.data.expires_in, 'seconds')
        }, response => {
          console.log('Auth Error')
        })
    }
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
