<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img v-bind:src="feed.actor.profile_pic">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="feed.statement" />
    </q-item>

    <q-card-main class="row">
      <blockquote>
        <p>{{ news.headline}}</p>
        <p>{{ news.content}}</p>
      </blockquote>
    </q-card-main>

    <q-card-actions>
      <q-btn class="action-btn q-mr-lg"
             style="margin-top: -0.5em"
             size="xl"
             flat
             no-ripple
             icon="far fa-thumbs-up"
             v-bind:color="interestingState ? 'positive' : 'neutral'"
             @click="markInteresting(true)">
      </q-btn>
      <q-item-side style="margin-left: -1.2em" v-for="(liker, index) in feed.user_reactions.all_likes.to_be_shown" v-bind:avatar="liker.owner_profile.profile_pic" :key="index"/>
      <q-item-tile v-if="totalMessage > 1" color="secondary" class="q-pl-sm q-pt-md" label>{{totalMessage}} likes</q-item-tile>
      <q-btn v-if="latestNewsId==news.id"
             class="action-btn"
             flat
             color="secondary"
             @click="getAnotherNews()">Next Story</q-btn>
    </q-card-actions>

    <slot></slot>

    <template v-for="additionalNews in additionalNewsList">
      <q-card-separator v-bind:key="additionalNews.id" />
      <q-card-main class="row" v-bind:key="additionalNews.id">
        <blockquote>
          <p>{{ additionalNews.headline }}</p>
          <p>{{ additionalNews.content}}</p>
        </blockquote>
      </q-card-main>

      <q-card-actions v-bind:key="additionalNews.id">
        <q-btn class="action-btn"
               flat
               v-bind:color="additionalNews.interesting ? 'tertiary' : 'primary'"
               @click="markAdditionalNewsInteresting(additionalNews)">{{ additionalNewsStatement(additionalNews)}}</q-btn>
        <q-btn v-if="latestNewsId===additionalNews.id && additionalNewsList.length < 3"
               class="action-btn"
               flat
               color="secondary"
               @click="getAnotherNews()">Next Story</q-btn>
      </q-card-actions>
    </template>
  </div>
</template>

<script>
import share from '../share.js'

export default {
  mounted: function () {
    this.getFeedObject = share.getFeedObject
  },
  name: 'news-feed',
  props: [
    'news',
    'feed'
  ],
  data () {
    return {
      interestingState: false,
      interestingId: null,
      interestingMsg: 'Really Interesting!',
      latestNewsId: null,
      additionalNewsList: [],
      totalMessage: null
    }
  },
  created () {
    let likedReactions = this.feed.user_reactions
    this.latestNewsId = this.news.id

    if (likedReactions.user_like_state.did_user_like) {
      this.markInteresting(false)
      this.interestingId = likedReactions.user_like_state.reaction_id
    }
    this.totalMessage = likedReactions.all_likes.total
  },
  methods: {
    additionalNewsStatement (news) {
      if (!('interesting' in news) || !news.funny) {
        return 'Really Interesting'
      }
      return 'You found it interesting'
    },
    markInteresting (apiCall) {
      this.interestingState = !this.interestingState
      this.interestingMsg = this.interestingState ? 'You found it interesting' : 'Really Interesting'

      let vm = this

      if (apiCall && this.interestingState) {
        this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.feed.id}/reactions/`, {
          'reaction': 'liked',
          'owner': this.$root.$options.user.id,
          'content': this.feed.id
        })
          .then(response => {
            vm.interestingId = response.data['id']
            console.log('success')
          })
          .then(response => { console.log('failure') })
      }

      if (apiCall && !this.interestingState) {
        this.$http.delete(`${this.$root.$options.hosts.rest}/act/actions/${this.feed.id}/reactions/${this.interestingId}/`, {
          'reaction': 'liked',
          'owner': this.$root.$options.user.id,
          'content': this.feed.id
        })
      }
    },
    getAnotherNews () {
      let excludeList = [this.news.id]
      let vm = this
      excludeList = excludeList.concat(this.additionalNewsList.map(news => news['id']))
      let handleFn = response => {
        let news = response.data
        news.interesting = response.data.user_actions.length > 0
        vm.$set(vm.additionalNewsList, vm.additionalNewsList.length, news)
        vm.latestNewsId = news.id
      }
      let errorFn = response => {
        console.log('error') // todo same with /JokeFeed.vue ln 132
      }
      this.getFeedObject('news', excludeList, handleFn, errorFn)
    },
    markAdditionalNewsInteresting (news) {
      news.interesting = !news.interesting

      this.$http.post(`${this.$root.$options.hosts.rest}/like_news/`, {
        'news_id': news.id,
        'set_to': (news.interesting ? 'true' : 'false')
      }).then(response => {
        console.log('success!')
      })
    }
  }
}
</script>

<style scoped>
  .action-btn {
    text-transform: capitalize;
    font-weight: normal;
  }
  .header {
    padding-top: 20px;
  }
</style>
