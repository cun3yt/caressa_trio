<template>
  <div class="main-content">
    Care Circle
  </div>
</template>

<script>
  export default {
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Care Circle'
      })
    }
  }
</script>
