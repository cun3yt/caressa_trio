<template>
  <q-card-title class="row">
    {{ statement }}.
  </q-card-title>
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
