// Common Vue Plugins to Be Used Often on Pages
//
// This file is intended to export the commonly used Vue Plugins.
// If you want to add commonly used packages import it here and
// put the plugin to the exported array.
// If you want to add a plugin that it is not used often then
// import that plugin in the relevant pages/components.
// In that case the usage is similar to the following:
//
// import Vue from 'Vue'
// import VuePluginYouWant from 'vue-plugin-you-want'
//
// Vue.use(VuePluginYouWant)
//

import VueCookies from 'vue-cookies'
import VueResource from 'vue-resource'

export default [
    VueCookies,
    VueResource
]
