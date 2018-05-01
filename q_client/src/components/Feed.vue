<template>
  <div class="main-content">
    <div v-for="feed in feeds">
      {{feed.value}}
    </div>
  </div>
</template>

<script>
  import Pusher from 'pusher-js'

  Pusher.logToConsole = true

  const pusher = new Pusher('6a4df3a29e534491839b', {
    cluster: 'us2',
    encrypted: true
  })

  const channel = pusher.subscribe('feeds')

  export default {
    name: 'feed',
    props: ['setupContent'],
    data () {
      return {
        feeds: [
          { value: 'what\'s up?' },
          { value: 'not much...' }
        ]
      }
    },
    created () {
      this.setupContent({
        title: 'Feed'
      })

      let that = this
      channel.bind('new-feed', function (data) {
        that.feeds = data.feeds
      })
    }
  }
</script>

<style scoped>

</style>
