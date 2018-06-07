<template>
  <div>
    <q-card-title class="row">
      <q-item-side v-bind:avatar="feed.actor.profile_pic" class="col-1" />
      <div class="col-11">{{ feed.statement }}.</div>
    </q-card-title>
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
