<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <q-card class="q-ma-sm" v-for="feed in feeds" v-bind:key="feed.id">
        <template v-if="feed.action_object_type==='Joke'">
          <joke-feed :feed="feed"
                     :joke="feed.action_object"
                     >
            <comments :actionId="feed.id" :comments="feed.paginated_comments" />
          </joke-feed>
        </template>
        <template v-else-if="feed.action_object_type==='News'">
          <news-feed :feed="feed"
                     :news="feed.action_object"
                     >
            <comments :actionId="feed.id" :comment="feed.paginated_comments" />
          </news-feed>
        </template>
        <template v-else>
          <regular-feed :feed="feed">
            <comments :actionId="feed.id" :comments="feed.paginated_comments" />
          </regular-feed>
        </template>
        <q-card-separator />
      </q-card>
    </div>
  </q-page>
</template>

<script>
import JokeFeed from 'components/JokeFeed'
import NewsFeed from 'components/NewsFeed'
import RegularFeed from 'components/RegularFeed'
import Comments from 'components/Comments'

export default {
  name: 'feed',
  props: ['setupContent'],
  components: {
    JokeFeed,
    NewsFeed,
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

      this.$http.get(`${this.$root.$options.hosts.rest}/act/actions/?id=${this.$root.$options.user.id}&page=${this.pageNumber}`, {})
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
