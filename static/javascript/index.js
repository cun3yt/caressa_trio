// Webpack Entry Point
//
// This is the entry point of webpack bundling. It has
//    - Vue common plugin installation (see the file `plugins.common.js`)
//    - Routing logic for HTML data attributes to Vue Application (see the file `router.js`)
//

import Vue from 'vue'
import router from './router.js'
import plugins from './plugins.common.js';

// Installing common Vue Plugins
for(let _index in plugins) {
  Vue.use(plugins[_index])
}

let component = {
  name: null,
  context: null
}

new Vue({
  el: '#app',
  beforeMount: function() {
    let dataset = this.$el.dataset
    component.name = dataset.component
    component.context = Object.assign({}, dataset)
  },
  render: h => h(router[component.name], {
    props: component.context
  })
})
