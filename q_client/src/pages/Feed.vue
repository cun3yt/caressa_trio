<template>
  <q-page padding class="row justify-center">
    <div class="main-content">

      <div v-if="isLoading">
        <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
      </div>
      <div v-else-if="error && feeds.length===0">
        There is a connection problem, please try again later.
      </div>

      <q-card class="q-ma-sm" v-for="feed in feeds" v-bind:key="feed.id">
        <template v-if="feed.action_object_type==='ActionGeneric' && feed.action_object.data.type==='genre'">
          <action-generic-feed :feed="feed" :action="feed.action_object">
          </action-generic-feed>
        </template>

        <template v-else-if="feed.action_object_type==='ActionGeneric' && feed.action_object.data.type==='e-commerce'">
          <e-commerce-feed :feed="feed" :action="feed.action_object">
          </e-commerce-feed>
        </template>

        <template v-else-if="feed.action_object_type==='ActionGeneric' && feed.action_object.data.type==='news'">
          <generic-news-feed :feed="feed" :action="feed.action_object">
          </generic-news-feed>
        </template>

        <template v-else-if="feed.action_object_type==='ActionGeneric' && feed.action_object.data.type==='event'">
          <event-feed :feed="feed" :action="feed.action_object">
          </event-feed>
        </template>

        <template v-else-if="feed.action_object_type==='ActionGeneric' && feed.action_object.data.type==='photo-gallery'">
          <photo-gallery-feed :feed="feed" :action="feed.action_object">
          </photo-gallery-feed>
        </template>

        <template v-else-if="feed.action_object_type==='Joke'">
          <joke-feed :feed="feed"
                     :joke="feed.action_object">
            <comment-section :actionId="feed.id" :comments="feed.paginated_comments" />
          </joke-feed>
        </template>

        <template v-else-if="feed.action_object_type==='News'">
          <news-feed :feed="feed"
                     :news="feed.action_object">
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
import ActionGenericFeed from 'components/ActionGenericFeed'
import ECommerceFeed from 'components/ECommerceFeed'
import GenericNewsFeed from 'components/GenericNewsFeed'
import EventFeed from 'components/EventFeed'
import PhotoGalleryFeed from 'components/PhotoGalleryFeed'
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
    CommentSection,
    ActionGenericFeed,
    ECommerceFeed,
    GenericNewsFeed,
    EventFeed,
    PhotoGalleryFeed
  },
  data () {
    return {
      pageNumber: 0,
      feeds: [],
      moreFeedsNeeded: false,
      feedPushed: false,
      isLoading: true,
      error: false
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
    addFeeds (successCallback, errorCallback) {
      let vm = this
      ++this.pageNumber
      this.$auth.get(`${this.$root.$options.hosts.rest}/act/actions/?id=${this.$root.$options.user.id}&page=${this.pageNumber}`)
        .then(response => {
          vm.feeds = vm.feeds.concat(response.data['results'])
          if (vm.bottomVisible()) {
            vm.addFeeds()
          }
          vm.isLoading = false
        }, response => {
          vm.isLoading = false
          if (response.status !== 404) {
            vm.error = true
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
    addMoreFeeds () {
      this.moreFeedsNeeded = this.bottomVisible()
    },
    getScrollLocation () {
      this.$root.$options.scrollData.feed = window.scrollY
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
      title: 'Latest'
    })
    this.pushFeeds()
  },
  activated () {
    document.addEventListener('scroll', this.addMoreFeeds)
    document.addEventListener('scroll', this.getScrollLocation)
    window.scrollTo(0, this.$root.$options.scrollData.feed)
  },
  deactivated () {
    document.removeEventListener('scroll', this.addMoreFeeds)
    document.removeEventListener('scroll', this.getScrollLocation)
  }
}
</script>

<style scoped>

</style>
