<template>
  <div>
    <q-item class="header">
      <q-item-side>
        <q-item-tile avatar>
          <img src="~assets/photo-gallery.png">
        </q-item-tile>
      </q-item-side>
      <q-item-main v-bind:label="action.data.question" />
    </q-item>

    <q-item>
      <q-item-main>
        <q-carousel color="white" arrows height="300px">
          <q-carousel-slide v-for="photo in action.data.selections"
                            v-bind:key="photo.img"
                            :img-src="photo.img">
<!--            <img :src="photo.img" style="width: 100%; ">-->
          </q-carousel-slide>
        </q-carousel>
      </q-item-main>
    </q-item>

    <q-item v-if="selection!==null">
      <q-item-main>Thank you for your answer!</q-item-main>
    </q-item>

    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'photo-gallery-feed',
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
    update () {

    }
  }
}
</script>

<style scoped>
  .header {
    padding-top: 20px;
  }
</style>
