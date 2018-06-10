<template>
  <div class="main-content">
    <post-detail-activity v-if="selected=='activity'"></post-detail-activity>
    <div v-else>
      <div class="row">
        Master Page is here...
      </div>
      <div class="row">
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Watching...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Reading...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Listening to...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Drinking...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send" align="right">Eating...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Playing...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Traveling to...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Looking for...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Attending...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Supporting...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Celebrating...</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" icon-right="send">Meeting...</q-btn>
      </div>
    </div>
  </div>
</template>

<script>
  import PostDetailActivity from './PostDetailActivity'

  export default {
    name: 'post',
    props: ['setupContent'],
    components: {
      PostDetailActivity
    },
    created () {
      this.setupContent({
        title: 'Post'
      })
    },
    data () {
      return {
        selected: null
      }
    }
  }
</script>
