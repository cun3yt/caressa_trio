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
      <q-btn class="action-btn"
             flat
             v-bind:color="interestingState ? 'tertiary' : 'primary'"
             @click="markInteresting(true)">{{interestingMsg}}</q-btn>
      <q-btn v-if="latestNewsId==news.id"
             class="action-btn"
             flat
             color="secondary"
             @click="getAnotherNews()">Next Story</q-btn>
    </q-card-actions>

    <slot></slot>

    <template v-for="additionalNews in additionalNews">
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
               @click="markAdditionalNewsFunny(additionalNews)">{{ additionalNewsStatement(additionalNews)}}</q-btn>
        <q-btn v-if="latestNewsId===additionalNews.id && additionalNews.length < 3"
               class="action-btn"
               flat
               color="secondary"
               @click="getAnotherNews()">Next Story</q-btn>
      </q-card-actions>
    </template>
  </div>
</template>

<script>
export default {
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
      additionalNews: ['']
    }
  },
  created () {
    let foundInterestingReactions = this.feed.user_reactions.filter(obj => obj['reaction'] === 'interesting')
    this.latestNewsId = this.news.id

    if (foundInterestingReactions.length > 0) {
      this.markInteresting(false)
      this.interestingId = foundInterestingReactions[0].id
    }
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

      if (apiCall && this.interestingState){
        this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.feed.id}/reactions/`, {
          'reaction': 'interesting',
          'owner': this.$root.$options.userId,
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
          'reaction': 'interesting',
          'owner': this.$root.$options.userId,
          'content' : this.feed.id
        })
      }
    },
    getAnotherNews () {
      let excludeStr = ''
      let excludeList = [this.news.id]
      let vm = this

      excludeList = excludeList.concat(this.additionalNews.map(news => joke['id']))
      excludeStr = `?exclude=${excludeList.join(',')}`

      this.$http.get(`${this.$root.$options.hosts.rest}/flat-api/news`)
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
