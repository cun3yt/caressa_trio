<template>
  <div class="main">
    <q-card-title class="row">
      Comments
    </q-card-title>
    <q-list v-if="comments.count > 0" no-border separator class="q-mt-md">
        <q-btn class="q-pa-xs q-ma-xs q-pl-sm" v-for="comment in comments.results" :key="comment.id" outline rounded color="primary" :label="comment.comment" @click="post(comment.comment)">
          <q-item-side class="q-ml-md" v-for="(backer, index) in comment.comment_backers" v-bind:avatar="backer.profile_pic" :key="index"/>
        </q-btn>
    </q-list>

    <q-btn v-if="comments.results.length < comments.count"
           v-on:click="loadMore()" flat color="secondary">Load More</q-btn>
    <q-item>
      <q-item-main>
        <q-input v-if="comments.count===0" v-model="new_comment" type="textarea" name="new-comment" placeholder="Be first to comment" />
        <q-input v-else v-model="new_comment" type="textarea" name="new-comment" placeholder="Write your comment" />
        <q-item-side :disabled="isOverLimit" :style="{color: isOverLimit}">{{charactersLeft}}</q-item-side>
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
  computed: {
    isOverLimit () {
      return this.charactersLeft < 0
    },
    charactersLeft () {
      let char = this.new_comment.length,
        limit = 140
      return (limit - char)
    }
  },
  methods: {
    refresh () {
      let vm = this
      this.$http.get(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {}).then(
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
          // todo 1. Fix the warning: Avoid mutating a prop directly since the value will be overwritten whenever
          // the parent component re-renders. Instead, use a data or computed property based on the prop's value.
          // Prop being mutated: "comments"
          // todo 2. Add loader for loading more.
          vm.comments.results = vm.comments.results.concat(response.data['results'])
          this.next_url = response.data['next']
        })
    },
    timePasted (comment) {
      return moment(comment.created).fromNow()
    },
    post (new_comment = this.new_comment) {
      let vm = this

      this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {'comment': new_comment})
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
