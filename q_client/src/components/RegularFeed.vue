<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img v-bind:src="feed.actor.profile_pic">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="feed.statement" />
    </q-item>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'regular-feed',
  props: ['feed'],
  data () {
    return {}
  }
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
</style>
