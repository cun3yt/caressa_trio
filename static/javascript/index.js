import Vue from 'Vue';
import router from './router.js';

let component_name = null
let context = null

new Vue({
  el: '#app',
  beforeMount: function() {
    let dataset = this.$el.dataset
    component_name = dataset.component
    context = Object.assign({}, dataset)
  },
  render: h => h(router[component_name], {
    props: context
  })
})
