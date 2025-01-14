export default {
  getFeedObject (resource, excludeList, handleFn, errorFn) {
    let excludeStr = ''
    excludeStr = `?exclude=${excludeList.join(',')}`
    this.$auth
      .get(
        `${
          this.$root.$options.hosts.rest
        }/flat-api/${resource}/0/${excludeStr}`,
        {}
      )
      .then(handleFn)
      .then(errorFn)
  }
}
