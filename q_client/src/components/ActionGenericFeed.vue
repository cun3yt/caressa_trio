<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile>
          <img src="~assets/musical-notes.png">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="action.data.question" />
    </q-item>

    <q-item>
      <q-item-main>
        <q-btn-toggle
          v-model="selection"
          toggle-color="primary"
          :options="action.data.selections"
          @input="update(selection)"
        />
      </q-item-main>
    </q-item>

    <q-item v-if="selection!==null">
      <q-item-main>Caressa will play more {{selection}}.</q-item-main>
    </q-item>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'action-generic-feed',
  props: [
    'action',
    'feed'
  ],
  data () {
    return {
      selection: null
    }
  },
  methods: {
    update (selection) {
      this.selection = selection
    }
  }
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
</style>
