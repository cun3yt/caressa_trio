<template>
  <div class="main-content">
    <div v-for="feed in feeds">
      <joke-feed :statement="feed.statement" :joke="feed.action_object"
                 v-if="feed.action_object_type=='Joke'"></joke-feed>
      <regular-feed :statement="feed.statement" v-else />
    </div>
  </div>
</template>

<script>
  import JokeFeed from './JokeFeed'
  import RegularFeed from './RegularFeed'

  export default {
    name: 'feed',
    props: ['setupContent'],
    components: {
      JokeFeed,
      RegularFeed
    },
    data () {
      return {
        feeds: []
      }
    },
    created () {
      this.setupContent({
        title: 'Feed'
      })

      this.$http.get(this.$root.$options.restHost + '/stream/?id=' + this.$root.$options.userId, {
      }).then(response => {
        this.feeds = response.data
      })
    }
  }
</script>

<style scoped>

</style>
