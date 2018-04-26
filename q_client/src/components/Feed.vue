<template>
  <div class="main-content">
    Feed
  </div>
</template>

<script>
  export default {
    name: 'feed',
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Feed'
      })
    }
  }
</script>

<style scoped>

</style>
