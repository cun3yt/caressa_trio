<template>
  <q-page>
    <gift v-for="(product, index) in products" :key="index" :product="product"></gift>
  </q-page>
</template>

<script>
import Gift from '../components/Gift'

export default {
  name: 'shop',
  props: ['setupContent'],
  components: {
    Gift
  },
  created () {
    this.setupContent({
      title: 'Shop'
    })
  },
  methods: {
    getScrollLocation () {
      this.$root.$options.scrollData.shop = window.scrollY
    }
  },
  activated () {
    document.addEventListener('scroll', this.getScrollLocation)
    window.scrollTo(0, this.$root.$options.scrollData.shop)
  },
  deactivated () {
    document.removeEventListener('scroll', this.getScrollLocation)
  },
  data () {
    return {
      products: [
        {
          name: 'Pink Pearl Roses',
          images: [
            {
              name: 'Pink Pearl Roses 1',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/flower1.jpg'
            },
            {
              name: 'Pink Pearl Roses 2',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/flower2.jpg'
            },
            {
              name: 'Pink Pearl Roses 2',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/flower3.jpg'
            }
          ],
          price: '23.99',
          details: 'Lovely and luxurious, Pink Pearl Roses are the perfect gift for your loved ones!'
        },
        {
          name: 'Personalized Pillow',
          images: [
            {
              name: 'Custom Pillow 1',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/pillow1.jpg'
            },
            {
              name: 'Custom Pillow 2',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/pillow2.jpg'
            },
            {
              name: 'Custom Pillow 3',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/pillow3.jpg'
            }
          ],
          price: '13.99',
          details: 'One of a kind designs featuring the calligraphy of our own pillows. Contact us for designs!'
        },
        {
          name: 'Personalized Coffee Mugs',
          images: [
            {
              name: 'Custom Mug 1',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/mug1.jpg'
            },
            {
              name: 'Custom Mug 2',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/mug2.jpg'
            },
            {
              name: 'Custom Mug 3',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/mug3.jpg'
            }
          ],
          price: '11.99',
          details: 'One of a kind designs featuring the calligraphy of our own mugs. Contact us for designs!'
        },
        {
          name: '1000 Piece Frank Sinatra Jigsaw Puzzle',
          images: [
            {
              name: 'Frank Sinatra Puzzle',
              url: 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/demo/frank-sinatra-puzzle.jpg'
            }
          ],
          price: '49.99',
          details: 'Challenging and exciting Frank Sinatra puzzle made from recycled material.'
        }

      ]
    }
  }
}
</script>

<style scoped>

</style>
