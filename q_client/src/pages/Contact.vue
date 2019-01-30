<template>
  <q-page class="row justify-center">
    <div class="main-content">
      <q-list>
        <q-list-header>Contact Us</q-list-header>
          <q-input
            v-model="area"
            type="textarea"
            float-label="Textarea"
            :max-height="100"
            rows="7"
          />
        <q-btn>Submit</q-btn>
      </q-list>
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'contact',
  props: ['setupContent'],
  created () {
    this.setupContent({
      title: 'Reach Us'
    })
  },
  data () {
    return {
    }
  }
}
</script>
<style lang="stylus">
  .main-content {
    width: 500px;
    max-width: 90vw;
  }
</style>
