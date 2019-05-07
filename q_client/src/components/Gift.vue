<template>
  <q-card class="q-ma-sm">
    <q-card-title></q-card-title>
    <q-card-main>
      <q-carousel color="white" quick-nav height="300px" >
        <q-carousel-slide v-for="(image, key) in product.images" :key="key" :img-src="image.url" />
      </q-carousel>
    </q-card-main>
    <q-card-main>
      <q-item>
        <q-item-main>
          <q-item-tile label>{{product.name}}</q-item-tile>
          <q-item-tile sublabel>{{product.details}}</q-item-tile>
        </q-item-main>
        <q-item-side color="primary">$ {{product.price}}</q-item-side>
      </q-item>
      <q-card-actions>
      <q-btn @click="purchase" color="primary">Buy as a gift to Maggie</q-btn>
      </q-card-actions>
    </q-card-main>
  </q-card>
</template>

<script>
export default {
  name: 'Gift',
  props: ['product'],
  methods: {
    purchase () {
      this.$auth.post(`${this.$root.$options.hosts.rest}/new_message/`, {
        'type': 'family_ios_text',
        'key': 'Text Message',
        'content': 'John has a surprise for you that is set to be delivered on May 10th, Friday. Caressa is excited for you!'
      }).then(response => {
        console.log('Response : ', response)
      })
    }
  }
}
</script>

<style scoped>

</style>
