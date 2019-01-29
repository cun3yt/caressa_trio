<template>
  <q-page padding class="row justify-center">
    <div class="main-content">

      <q-card class="q-ma-sm" v-for="feed in feeds" v-bind:key="feed.id">
        <template v-if="feed.action_object_type==='Joke'">
          <joke-feed :feed="feed"
                     :joke="feed.action_object"
                     >
            <comment-section :actionId="feed.id" :comments="feed.paginated_comments" />
          </joke-feed>
        </template>
        <template v-else-if="feed.action_object_type==='News'">
          <news-feed :feed="feed"
                     :news="feed.action_object"
                     >
            <comment-section :actionId="feed.id" :comments="feed.paginated_comments" />
          </news-feed>
        </template>
        <template v-else-if="feed.action_object_type==='UserPost'">
          <user-post-feed :feed="feed">
            <comment-section :actionId="feed.id" :comments="feed.paginated_comments" />
          </user-post-feed>
        </template>
        <template v-else>
          <regular-feed :feed="feed">
            <comment-section :actionId="feed.id" :comments="feed.paginated_comments" />
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
import CommentSection from 'components/CommentSection'
import Pusher from 'pusher-js'
import {bus} from '../plugins/auth.js'

// Pusher.logToConsole = true // for logging purpose

export default {
  name: 'feed',
  props: ['setupContent'],
  components: {
    UserPostFeed,
    JokeFeed,
    NewsFeed,
    RegularFeed,
    CommentSection
  },
  data () {
    return {
      pageNumber: 0,
      feeds: [],
      moreFeedsNeeded: false,
      feedPushed: false
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
      this.$auth.get(`${this.$root.$options.hosts.rest}/act/actions/?id=${this.$root.$options.user.id}&page=${this.pageNumber}`)
        .then(response => {
          vm.feeds = vm.feeds.concat(response.data['results'])
          if (vm.bottomVisible()) {
            vm.addFeeds()
          }
        })
    },
    pushFeeds () {
      const pusher = new Pusher(this.$root.$options.pusherConfig.pusherKey, {cluster: this.$root.$options.pusherConfig.pusherCluster})
      const channel = pusher.subscribe(this.$root.$options.pusherConfig.channelName)
      let vm = this
      channel.bind('feeds', function (data) {
        vm.feeds.unshift(data)
        vm.pushNotif()
      })
    },
    pushNotif () {
      this.$q.notify({
        color: 'positive',
        position: 'bottom-left',
        actions: [
          {
            label: 'One New Feed Arrived',
            icon: 'fas fa-arrow-up',
            handler: () => {
              window.scrollTo({
                top: 0,
                behavior: 'smooth'
              })
            }
          }
        ]
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
  mounted () {
    bus.$on('addFeeds', this.addFeeds)
  },
  created () {
    this.addFeeds()
    this.setupContent({
      title: 'Maggy'
    })
    window.addEventListener('scroll', () => {
      this.moreFeedsNeeded = this.bottomVisible()
    })
    this.pushFeeds()
  }
}
</script>

<style scoped>

</style>
