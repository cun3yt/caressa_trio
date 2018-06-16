<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <post-detail-activity v-if="selected=='activity'"></post-detail-activity>
      <div v-else>
        <div class="row bg q-pa-xl full-height">
          Master Page is here...
        </div>

        <div class="doc-container row">
          <div class="col-6">
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
          <div class="col bg q-pt-md q-pr-sm">
            <div class="row q-mt-md q-mr-sm">something</div>
            <div class="row q-mt-md q-mr-sm">something else</div>
          </div>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import PostDetailActivity from 'components/PostDetailActivity'

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

<style scoped lang="stylus">
  primary = red

  .bg
    background-color: blanchedalmond
    border: 1px solid black

</style>
