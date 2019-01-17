let authModule = {
  access_token: null,
  refresh_token: null,
  expiry_date: null,
  check_state: function () {
    return !(this.access_token && this.refresh_token)
  }
}
export default ({Vue}) => {
  Vue.prototype.$auth = authModule
}
