// === DEFAULT / CUSTOM STYLE ===
// WARNING! always comment out ONE of the two require() calls below.
// 1. use next line to activate CUSTOM STYLE (./src/themes)
// require(`./themes/app.${__THEME}.styl`)
// 2. or, use next line to activate DEFAULT QUASAR STYLE
require(`quasar/dist/quasar.${__THEME}.css`)
// ==============================

// Uncomment the following lines if you need IE11/Edge support
// require(`quasar/dist/quasar.ie`)
// require(`quasar/dist/quasar.ie.${__THEME}.css`)

import Vue from 'vue'
import router from './router'

// todo Don't use this in production
import Quasar, * as All from 'quasar'
import VueResource from 'vue-resource'

Vue.config.productionTip = false

Vue.use(Quasar, {
  components: All, // todo don't use in production
  directives: All // todo don't use in production
})

Vue.use(VueResource)

if (__THEME === 'mat') {
  require('quasar-extras/roboto-font')
}
import 'quasar-extras/material-icons'
// import 'quasar-extras/ionicons'
// import 'quasar-extras/fontawesome'
// import 'quasar-extras/animate'

Quasar.start(() => {
  /* eslint-disable no-new */
  new Vue({
    el: '#q-app',
    apiHost: 'http://127.0.0.1:3000',
    restHost: 'http://127.0.0.1:9900',
    userId: 2,
    router,
    render: h => h(require('./App').default)
  })
})
