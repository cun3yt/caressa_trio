<template>
  <div>
    <q-card-title class="row">
      {{ statement }}.
    </q-card-title>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'regular-feed',
  props: ['statement'],
  data () {
    return {}
  }
}
</script>
