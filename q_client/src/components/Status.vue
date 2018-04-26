<template>
  <div class="main-content">Status</div>
</template>

<script>
  import LineChart from './LineChart'

  export default {
    components: {
      LineChart
    },
    name: 'status',
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Status'
      })
    },
    data () {
      return {
        data: {

        }
      }
    }
  }
</script>
