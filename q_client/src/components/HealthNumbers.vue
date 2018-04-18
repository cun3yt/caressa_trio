<template>
  <div class="main-content">
    Health Numbers
    <div class="layout-view">
      <something :data="data"></something>
    </div>
  </div>
</template>

<script>
  import Something from './Something'
  export default {
    components: {
      Something
    },
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Status'
      })
    },
    data () {
      return {
        labels: ['a', 'b', 'c'],
        datasets: [{
          label: ['one', 'two', 'three'],
          backgroundColor: '#ff00ee',
          data: [10, 20, 16]
        }],
        option: {
          height: 100
        }
      }
    }
  }
</script>

