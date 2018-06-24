export default {
  getFeedObject: function getFeedObject (resource, excludeList, handleFn, errorFn) {
    let excludeStr = ''
    excludeStr = `?exclude=${excludeList.join(',')}`
    this.$http.get(`${this.$root.$options.hosts.rest}/flat-api/${resource}/0/${excludeStr}`, {})
      .then(handleFn)
      .then(errorFn)
  }
}
