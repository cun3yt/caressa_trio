<template>
  <q-card-main class="row">{{ statement }}</q-card-main>
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
