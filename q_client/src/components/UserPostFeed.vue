<template>
  <div class="q-pt-sm">
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img v-bind:src="feed.actor.profile_pic">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="feed.statement" />
    </q-item>

    <q-card-main class="row">
      "{{ feed.action_object.content }}"
    </q-card-main>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'user-post-feed',
  props: [
    'feed'
  ]
}
</script>
