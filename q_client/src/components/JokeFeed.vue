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
        <p>{{ joke.main }}</p>
        <p>{{ joke.punchline }}</p>
      </blockquote>
    </q-card-main>

    <q-card-actions>
      <q-btn class="action-btn"
             outline
             round
             icon="far fa-thumbs-up"
             v-bind:color="funnyState ? 'positive' : 'neutral'"
             @click="markFunny(true)"></q-btn>
      <q-btn v-if="latestJokeId==joke.id"
             class="action-btn"
             flat
             color="secondary"
             @click="getAnotherJoke()">Tell me another joke</q-btn>
    </q-card-actions>

    <slot></slot>

    <template v-for="additionalJoke in additionalJokes">
      <q-card-separator v-bind:key="additionalJoke.id" />
      <q-card-main class="row" v-bind:key="additionalJoke.id">
        <blockquote>
          <p>{{ additionalJoke.main }}</p>
          <p>{{ additionalJoke.punchline }} </p>
        </blockquote>
      </q-card-main>

      <q-card-actions v-bind:key="additionalJoke.id">
        <q-btn class="action-btn"
               flat
               v-bind:color="additionalJoke.funny ? 'tertiary' : 'primary'"
               @click="markAdditionalJokeFunny(additionalJoke)">{{ additionaJokeStatement(additionalJoke) }}</q-btn>
        <q-btn v-if="latestJokeId===additionalJoke.id && additionalJokes.length < 3"
               class="action-btn"
               flat
               color="secondary"
               @click="getAnotherJoke()">Tell me another joke</q-btn>
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
  name: 'joke-feed',
  props: [
    'joke',
    'feed'
  ],
  data () {
    return {
      funnyState: false,
      funnyId: null,
      funnyMsg: 'That\'s funny!',
      latestJokeId: null,
      additionalJokes: []
    }
  },
  created () {
    let laughedReactions = this.feed.user_reactions.filter(obj => obj['reaction'] === 'laughed')
    this.latestJokeId = this.joke.id

    if (laughedReactions.length > 0) {
      this.markFunny(false)
      this.funnyId = laughedReactions[0].id
    }
  },
  methods: {
    additionaJokeStatement (joke) {
      if (!('funny' in joke) || !joke.funny) {
        return 'That\'s funny'
      }
      return 'You found it funny'
    },
    markFunny (apiCall) {
      this.funnyState = !this.funnyState
      this.funnyMsg = this.funnyState ? 'You found it funny' : 'That\'s funny!'

      let vm = this

      if (apiCall && this.funnyState) {
        this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.feed.id}/reactions/`, {
          'reaction': 'laughed',
          'owner': this.$root.$options.user.id,
          'content': this.feed.id
        })
          .then(response => {
            vm.funnyId = response.data['id']
            console.log('success')
          })
          .then(response => { console.log('failure') })
      }

      if (apiCall && !this.funnyState) {
        this.$http.delete(`${this.$root.$options.hosts.rest}/act/actions/${this.feed.id}/reactions/${this.funnyId}/`, {
          'reaction': 'laughed',
          'owner': this.$root.$options.user.id,
          'content': this.feed.id
        })
      }
    },
    getAnotherJoke () {
      let excludeList = [this.joke.id]
      let vm = this
      excludeList = excludeList.concat(this.additionalJokes.map(joke => joke['id']))
      let handleFn = response => {
        let joke = response.data
        joke.funny = response.data.user_actions.length > 0
        vm.$set(vm.additionalJokes, vm.additionalJokes.length, joke)
        vm.latestJokeId = joke.id
      }
      let errorFn = response => {
        console.log('error') // todo This is called no matter if it is successful or not!
      }
      this.getFeedObject('jokes', excludeList, handleFn, errorFn)
    },
    markAdditionalJokeFunny (joke) {
      joke.funny = !joke.funny

      this.$http.post(`${this.$root.$options.hosts.rest}/laugh/`, {
        'joke_id': joke.id,
        'set_to': (joke.funny ? 'true' : 'false')
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
