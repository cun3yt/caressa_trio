<template>
      <q-list flat>

        <q-item v-for="(response, key) in responses" :key="key">
          <q-item-side><img class="fit profile-pic" :src="response.profile_pic" alt="image"> </q-item-side>
          <q-item-side class="q-caption">{{response.response}}</q-item-side>
          <q-item-side>
            <q-btn flat @click="deleteResponse(response.id)" icon="fas fa-times"></q-btn>
          </q-item-side>
        </q-item>

        <q-item>
          <q-input :max-height="25" v-model="new_response" clearable type="textarea" name="new-response"
                   class="new-response" placeholder="New Response">
            <q-item-side :color="isOverLimit ? 'negative' : 'neutral'">{{charactersLeft}} / 70</q-item-side>
          </q-input>
          <q-btn :disable=isOverLimit @click="post()" class="action-btn" flat color="primary"
                 icon="fas fa-greater-than"></q-btn>
        </q-item>
        <q-item-separator inset />

      </q-list>
</template>

<script>
export default {
  name: 'responses',
  props: ['responses', 'comment_id'],
  data () {
    return {
      new_response: ''
    }
  },
  computed: {
    isOverLimit () {
      return this.charactersLeft < 0
    },
    charactersLeft () {
      let char = this.new_response.length,
        limit = 70
      return (limit - char)
    }
  },
  methods: {
    post (new_response = this.new_response) {
      let vm = this
      this.$auth.post(`${this.$root.$options.hosts.rest}/comment_response/`, {
        'comment_id': this.comment_id,
        'response': new_response
      }).then(response => {
        vm.new_response = ''
        vm.$options.parent.$parent.$parent.$options.parent.$parent.$parent.refresh()
        console.log('success!')
      })
    },
    deleteResponse (responseId) {
      let vm = this
      this.$auth.delete(`${this.$root.$options.hosts.rest}/comment_response_delete/`, {
        'comment_id': this.comment_id,
        'response': responseId
      }).then(response => {
        vm.new_response = ''
        vm.$options.parent.$parent.$parent.$options.parent.$parent.$parent.refresh()
        console.log('success!')
      })
    }
  }
}
</script>

<style scoped lang="stylus">
.new-response
  margin-top 20px
.profile-pic
  max-width: 2em
</style>
