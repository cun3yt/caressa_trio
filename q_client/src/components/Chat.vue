<template>
  <div class="main-content">
    Chat
  </div>
</template>

<script>
  export default {
    name: 'chat',
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Chat'
      })
    }
  }
</script>
