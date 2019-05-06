<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img src="~assets/hand-heart.png">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="action.data.question" />
    </q-item>

    <q-item v-bind:key="product.value"
            v-for="product in action.data.selections"
            v-bind:class="{ 'selected' : product.value===selection }"
            v-on:click.native="select(product.value)">
      <q-item-side :image="product.img" />
      <q-item-main>
        <q-item-tile label>{{product.label}}</q-item-tile>
        <q-item-tile sublabel>${{product.price}}</q-item-tile>
      </q-item-main>
    </q-item>

    <q-item v-if="selection!==null">
      <q-item-main>Thank you for your order. Your payment method under file will be charged.
        You can update or cancel until the end of the day.</q-item-main>
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
    select (id) {
      if (this.selection === id) {
        this.selection = null
        return
      }
      this.selection = id
    }
  }
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
  .selected {
    border: 1px dashed #333;
  }
</style>
