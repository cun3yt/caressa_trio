<template>
  <div class="q-ma-xs">
    <q-btn-group rounded flat>
      <q-btn
        size="sm"
        outline
        rounded
        color="primary"
        @click="toggleCommentBacking(comment.comment)">
        <q-item-side
          left
          style="margin-left: -1.3em"
          v-for="(backer, index) in comment.comment_backers.all_backers"
          v-bind:avatar="backer.profile_pic"
          :key="index"/>
        <q-item-tile class="q-ml-md" label>{{comment.comment}}</q-item-tile>
      </q-btn>
      <q-btn outline rounded @click="toggle()" icon="far fa-comment-dots"></q-btn>
    </q-btn-group>
    <q-collapsible group="response-accordion" header-class="hidden" flat collapse-icon='far fa-comment-dots' v-model="isOpen">
      <responses :responses="comment.responses" :comment_id="comment.id"></responses>
    </q-collapsible>
  </div>
</template>

<script>

import Responses from './Responses'

export default {
  name: 'Comment',
  components: {Responses},
  props: ['comment', 'actionId'],
  data () {
    return {
      next_url: '',
      new_comment: '',
      didUserBacked: this.comment.comment_backers.did_user_backed,
      isOpen: false
    }
  },
  created () {
    this.next_url = this.comment.next
  },
  methods: {
    toggle () {
      this.isOpen = !this.isOpen
    },
    post (newComment) {
      this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {'comment': newComment})
        .then(
          response => {
            console.log('success')
          }, response => {
            console.log('error')
          })
    },
    toggleCommentBacking (comment) {
      console.log(this.comment.comment_backers.did_user_backed)
      let vm = this
      if (comment && !this.didUserBacked) {
        this.$http.post(`${this.$root.$options.hosts.rest}/act/actions/${this.actionId}/comments/`, {'comment': comment})
          .then(
            response => {
              console.log('success')
              vm.$parent.$parent.refresh()
              vm.didUserBacked = true
              // todo This is a cheap solution to me for a problem occurs after mutation of a prop directly.
              // Refer: CommentSection.vue line: 57/67
            }, response => {
              console.log('error')
            })
      }
      if (comment && this.didUserBacked) {
        this.$http.delete(`${this.$root.$options.hosts.rest}/comment_backing_delete/`, {body: {'comment_id': this.comment.id}})
          .then(
            response => {
              console.log('success')
              vm.$parent.$parent.refresh()
              vm.didUserBacked = false
            }, response => {
              console.log('error')
            })
      }
    }
  }
}
</script>

<style scoped>

</style>
