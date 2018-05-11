<template>
  <q-card>
    <q-card-main class="row">{{ statement }}</q-card-main>
  </q-card>
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
