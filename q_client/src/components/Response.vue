<template>
  <q-btn-dropdown v-if="1 > 0" size="sm" outline rounded color="primary" icon="far fa-comment-dots">
    <q-list link>
      <q-item>
        <q-input :max-height="25" v-model="new_conversation" clearable type="textarea" name="new-comment-conv" placeholder="New comment">
          <q-item-side :color="isOverLimit ? 'negative' : 'neutral'">{{charactersLeft}} / 70</q-item-side>
        </q-input>
        <q-btn :disable=isOverLimit @click="post()" class="action-btn" flat color="primary">Post</q-btn>
      </q-item>
      <q-item-separator inset />
    </q-list>
  </q-btn-dropdown>
</template>

<script>
export default {
  name: 'response',
  props: [],
  data () {
    return {
      new_conversation: ''
    }
  },
  computed: {
    isOverLimit () {
      return this.charactersLeft < 0
    },
    charactersLeft () {
      let char = this.new_conversation.length,
        limit = 70
      return (limit - char)
    }
  }
}
</script>
