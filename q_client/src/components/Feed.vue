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
        pageNumber: 0,
        feeds: [],
        moreFeedsNeeded: false
      }
    },
    methods: {
      bottomVisible () {
        const scrollY = window.scrollY
        const visible = document.documentElement.clientHeight
        const pageHeight = document.documentElement.scrollHeight
        const bottomOfPage = visible + scrollY >= pageHeight
        return bottomOfPage || pageHeight < visible
      },
      addFeeds () {
        let vm = this
        ++this.pageNumber

        this.$http.get(`${this.$root.$options.restHost}/act/streams/?id=${this.$root.$options.userId}&page=${this.pageNumber}`, {})
          .then(response => {
            vm.feeds = vm.feeds.concat(response.data['results'])
            if (vm.bottomVisible()) {
              vm.addFeeds()
            }
          })
      }
    },
    watch: {
      moreFeedsNeeded (moreFeedsNeeded) {
        if (moreFeedsNeeded) {
          this.addFeeds()
        }
      }
    },
    created () {
      this.setupContent({
        title: 'Feed'
      })
      window.addEventListener('scroll', () => {
        this.moreFeedsNeeded = this.bottomVisible()
      })
      this.addFeeds()
    }
  }
</script>

<style scoped>

</style>
