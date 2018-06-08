<template>
  <div class="main-content">
    <post-detail-activity v-if="selected=='activity'"></post-detail-activity>
    <div v-else>
      <div class="row">
        Master Page is here...
      </div>
      <div class="row">
        <q-btn outline color="primary col-5" @click="selected='activity'" label="Activity">Activity</q-btn>
        <q-btn outline color="primary col-5" @click="selected='activity'" label="Something Else">Something Else</q-btn>
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
