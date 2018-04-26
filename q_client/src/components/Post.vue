<template>
  <div class="main-content">
    Post
  </div>
</template>

<script>
  export default {
    name: 'post',
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Post'
      })
    }
  }
</script>
