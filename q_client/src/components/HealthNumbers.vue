<template>
  <div class="main-content">
    Health Numbers
  </div>
</template>

<script>
  export default {
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Status'
      })
    }
  }
</script>

