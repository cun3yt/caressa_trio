<template>
  <q-page>
    <gift v-for="(product, index) in products" :key="index" :product="product"></gift>
  </q-page>
</template>

<script>
import Gift from '../components/Gift'

export default {
  name: 'Shop',
  components: {
    Gift
  },
  data () {
    return {
      products: [
        {
          name: 'Product1',
          images: [
            {
              name: 'Product 1 First Image',
              url: 'http://dummyimage.com/242x185.bmp/ff4444/ffffff'
            },
            {
              name: 'Product 1 Second Image',
              url: 'http://dummyimage.com/186x138.bmp/cc0000/ffffff'
            },
            {
              name: 'Product 1 Third Image',
              url: 'http://dummyimage.com/126x182.png/5fa2dd/ffffff'
            }
          ],
          price: '23.99',
          details: 'Lorem ipsum dolor sit amet consectetur, adipisicing elit. Natus, ratione eum minus fuga.'
        },
        {
          name: 'Product2',
          images: [
            {
              name: 'Product 2 First Image',
              url: 'http://dummyimage.com/225x210.png/ff4444/ffffff'
            },
            {
              name: 'Product 2 Second Image',
              url: 'http://dummyimage.com/154x208.png/cc0000/ffffff'
            },
            {
              name: 'Product 2 Third Image',
              url: 'http://dummyimage.com/112x194.png/5fa2dd/ffffff'
            }
          ],
          price: '13.99',
          details: 'Adipisicing elit. Natus, ratione eum minus fuga. Lorem ipsum dolor sit amet consectetur.'
        }
      ]
    }
  }
}
</script>

<style scoped>

</style>
