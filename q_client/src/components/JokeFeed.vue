<template>
  <div>
    <q-card-title class="row">
      <q-item-side avatar="/statics/grandma-avatar.png" class="col-1" />
      <div class="col-11">{{ statement }}.</div>

    </q-card-title>
    <q-card-main class="row">
      <blockquote>
        <p>{{ joke.main }}</p>
        <p>{{ joke.punchline }} </p>
      </blockquote>
    </q-card-main>
    <q-card-separator />
    <q-card-actions>
      <q-btn class="action-btn" flat v-bind:color="funnyState ? 'tertiary' : 'primary'" @click="markFunny(true)">{{funnyMsg}}</q-btn>
      <q-btn class="action-btn" flat color="secondary" @click="getAnotherJoke()">Tell me another joke</q-btn>
    </q-card-actions>
  </div>
</template>

<script>
    export default {
      name: 'joke-feed',
      props: ['joke', 'statement', 'reactions', 'feedId'],
      data () {
        return {
          funnyState: false,
          funnyId: null,
          funnyMsg: 'That\'s funny!'
        }
      },
      created () {
        let laughedReactions = this.reactions.filter(obj => obj['reaction'] === 'laughed')

        if (laughedReactions.length > 0) {
          this.markFunny(false)
          this.funnyId = laughedReactions[0].id
        }
      },
      methods: {
        markFunny (apiCall) {
          this.funnyState = !this.funnyState
          this.funnyMsg = this.funnyState ? 'You found it funny' : 'That\'s funny!'

          let vm = this

          if (apiCall && this.funnyState) {
            this.$http.post(`${this.$root.$options.restHost}/act/actions/${this.feedId}/reactions/`, {
              'reaction': 'laughed',
              'owner': this.$root.$options.userId,
              'content': this.feedId
            })
              .then(response => {
                vm.funnyId = response.data['id']
                console.log('success')
              })
              .then(response => { console.log('failure') })
          }

          if (apiCall && !this.funnyState) {
            this.$http.delete(`${this.$root.$options.restHost}/act/actions/${this.feedId}/reactions/${this.funnyId}/`, {
              'reaction': 'laughed',
              'owner': this.$root.$options.userId,
              'content': this.feedId
            })
          }
        },
        getAnotherJoke () {
          console.log('another joke...')
        }
      }
    }
</script>

<style scoped>
  .action-btn {
    text-transform: capitalize;
    font-weight: normal;
  }
</style>
