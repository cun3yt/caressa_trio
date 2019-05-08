<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile>
          <img src="~assets/news.png">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="action.data.update" />
    </q-item>

    <q-item>
      <q-item-main v-bind:label="action.data.label" v-bind:sublabel="action.data.sublabel">
      </q-item-main>
    </q-item>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'generic-news-feed',
  props: [
    'action',
    'feed'
  ]
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
</style>
