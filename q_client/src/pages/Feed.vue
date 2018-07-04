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
        <template v-else-if="feed.action_object_type==='UserPost'">
          <user-post-feed :feed="feed">
            <comments :actionId="feed.id" :comments="feed.paginated_comments" />
          </user-post-feed>
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
import UserPostFeed from 'components/UserPostFeed'
import RegularFeed from 'components/RegularFeed'
import Comments from 'components/Comments'
import Pusher from 'pusher-js'

// Pusher.logToConsole = true // for logging purpose

export default {
  name: 'feed',
  props: ['setupContent'],
  components: {
    UserPostFeed,
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
    },
    pushFeeds () {
      const pusher = new Pusher('PUSHER_KEY', {cluster: 'PUSHER_CLUSSTER'}) // todo this needs to be an env var
      const channel = pusher.subscribe('carenv-development')
      let vm = this
      channel.bind('feeds', function (data) {
        vm.feeds.unshift(data)
        console.log(vm.feeds)
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
    this.pushFeeds()
  }
}
</script>

<style scoped>

</style>
