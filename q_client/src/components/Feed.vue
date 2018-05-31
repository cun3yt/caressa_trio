<template>
  <div class="main-content">
    <template v-for="feed in feeds">
      <q-card>
        <joke-feed :statement="feed.statement"
                   :joke="feed.action_object"
                   :reactions="feed.user_reactions"
                   :feedId="feed.id"
                   v-if="feed.action_object_type==='Joke'" />
        <regular-feed :statement="feed.statement" v-else />
        <q-card-separator />
        <comments :actionId="feed.id" :comments="feed.paginated_comments" />
      </q-card>
    </template>
  </div>
</template>

<script>
  import JokeFeed from './JokeFeed'
  import RegularFeed from './RegularFeed'
  import Comments from './Comments'

  export default {
    name: 'feed',
    props: ['setupContent'],
    components: {
      JokeFeed,
      RegularFeed,
      Comments
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

        this.$http.get(`${this.$root.$options.restHost}/act/actions/?id=${this.$root.$options.userId}&page=${this.pageNumber}`, {})
          .then(response => {
            vm.feeds = vm.feeds.concat(response.data['results'])
            // if (vm.bottomVisible()) {
            //   vm.addFeeds()
            // }
          })
      }
    },
    watch: {
      moreFeedsNeeded (moreFeedsNeeded) {
        // if (moreFeedsNeeded) {
        //   this.addFeeds()
        // }
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
