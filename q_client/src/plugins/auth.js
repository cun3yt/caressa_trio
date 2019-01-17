import Vue from 'vue'
let authModule = {
  access_token: null,
  refresh_token: null,
  expiry_date: null,
  check_state: function () {
    return !(this.access_token && this.refresh_token)
  },
  get: function (url) {
    let response = Vue.http.get(url, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': `Bearer ${this.access_token}`
      }
    })
    return response
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
