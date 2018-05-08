<template>
  <div class="main-content">
    <div v-for="feed in feeds">
      {{feed.value}}
    </div>
  </div>
</template>

<script>
  import JokeFeed from './JokeFeed'

  export default {
    name: 'feed',
    props: ['setupContent'],
    components: {
      JokeFeed
    },
    data () {
      return {

      }
    },
    created () {
      this.setupContent({
        title: 'Feed'
      })
    }
  }
</script>

<style scoped>

</style>
