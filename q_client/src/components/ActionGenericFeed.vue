<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img src="~assets/musical-notes.png">
        </q-item-tile>
<!--        <q-item-tile avatar>-->
<!--          <img v-bind:src="feed.actor.profile_pic">-->
<!--        </q-item-tile>-->
      </q-item-side>
      <q-item-main v-bind:label="action.data.question" />
    </q-item>

    <q-item>
      <q-item-main>
        <q-btn-toggle
          v-model="selection"
          toggle-color="primary"
          :options="action.data.selections"
          @input="update()"
        />
      </q-item-main>
    </q-item>

    <q-item v-if="selection!==null">
      <q-item-main>Thank you!</q-item-main>
    </q-item>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'action-generic-feed',
  props: [
    'action',
    'feed'
  ],
  data () {
    return {
      selection: null
    }
  },
  methods: {
    update () {

    }
  }
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
</style>
