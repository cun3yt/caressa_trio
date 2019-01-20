<template>
  <div class="main">
    <q-card-title class="row q-pa-none q-pl-sm q-mb-none">
      Comments
    </q-card-title>
    <q-list v-if="comments.count > 0" no-border class="row q-mt-md">
      <comment v-for="comment in comments.results" :key="comment.id" :comment="comment" :actionId="actionId"></comment>
    </q-list>
    <q-btn v-if="comments.results.length < comments.count"
           v-on:click="loadMore()" flat color="secondary">Load More</q-btn>
    <q-item>
      <q-item-main>
        <q-input v-if="comments.count===0" :max-height="25" v-model="new_comment" clearable type="textarea" name="new-comment" placeholder="Be first to comment">
          <q-item-side :color="isOverLimit ? 'negative' : 'neutral'">{{charactersLeft}} / 70</q-item-side>
        </q-input>
        <q-input v-else v-model="new_comment" :max-height="25" type="textarea" clearable name="new-comment" placeholder="Write your comment">
          <q-item-side :color="isOverLimit ? 'negative' : 'neutral'">{{charactersLeft}} / 70</q-item-side>
        </q-input>
        <q-btn :disable=isOverLimit @click="post()" class="action-btn" flat color="primary">Post</q-btn>
      </q-item-main>
    </q-item>
  </div>
</template>

<script>
import moment from 'moment'
import Comment from './Comment'

export default {
  name: 'CommentSection',
  components: {Comment},
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
        limit = 70
      return (limit - char)
    }
  },
  methods: {
    refresh () {
      let vm = this
      this.$auth.get(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {}).then(
        response => {
          vm.comments = response.data // todo this line gives error because of prop mutation inside component.
          vm.next_url = response.data['next']
        }
      )
    },
    loadMore () {
      let vm = this

      this.$auth.get(this.next_url, {})
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

      // todo: Check if this is still in use (there is a similar one in Comment.vue)
      this.$auth.post(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {'comment': new_comment})
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
