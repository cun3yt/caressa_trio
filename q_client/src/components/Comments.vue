<template>
  <div class="main">
    <q-card-title class="row">
      Comments
    </q-card-title>
    <q-list v-if="comments.count > 0" no-border separator class="q-mt-md">
      <q-item v-for="comment in comments.results" :key="comment.id">
        <q-item-side v-bind:avatar="$root.$options.userProfilePic" />
        <q-item-main :label="comment.commenter" :sublabel="comment.comment" label-lines="1" />
        <q-item-side right :stamp="timePasted(comment)" />
      </q-item>
    </q-list>

    <q-btn v-if="comments.results.length < comments.count"
           v-on:click="loadMore()" flat color="secondary">Load More</q-btn>
    <q-item>
      <q-item-main>
        <q-input v-if="comments.count===0" v-model="new_comment" type="textarea" name="new-comment" placeholder="Be first to comment" />
        <q-input v-else v-model="new_comment" type="textarea" name="new-comment" placeholder="Write your comment" />
      </q-item-main>
    </q-item>
    <q-btn @click="post()" class="action-btn" flat color="primary">Post</q-btn>
  </div>
</template>

<script>
  import moment from 'moment'

  export default {
    name: 'Comments',
    props: ['comments', 'actionId'],
    data () {
      return {
        next_url: '',
        new_comment: ''
      }
    },
    created () {
      this.next_url = this.comments.next
    },
    methods: {
      refresh () {
        let vm = this

        this.$http.get(`${this.$root.$options.restHost}/act/actions/${this.actionId}/comments/`, {}).then(
          response => {
            vm.comments = response.data
            vm.next_url = response.data['next']
          }
        )
      },
      loadMore () {
        let vm = this

        this.$http.get(this.next_url, {})
          .then(response => {
            vm.comments.results = vm.comments.results.concat(response.data['results'])
            this.next_url = response.data['next']
          })
      },
      timePasted (comment) {
        return moment(comment.created).fromNow()
      },
      post () {
        let vm = this

        this.$http.post(`${this.$root.$options.restHost}/act/actions/${this.actionId}/comments/`, {'comment': this.new_comment})
          .then(
            response => {
              console.log('success')
              vm.new_comment = ''
              vm.refresh()
            }, response => {
              console.log('error')
            })
      }
    }
  }
</script>

<style scoped>

</style>
