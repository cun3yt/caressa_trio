<template>
  <div>
    <q-card-title class="row">
      <q-item-side avatar="/statics/grandma-avatar.png" class="col-1" />
      <div class="col-11">{{ statement }}.</div>

    </q-card-title>
    <q-card-main class="row">
      <blockquote>
        <p>{{ joke.main }}</p>
        <p>{{ joke.punchline }} </p>
      </blockquote>
    </q-card-main>
    <q-card-separator />
    <q-card-actions>
      <q-btn class="action-btn" flat color="primary" v-on:click="markFunny()">{{funnyMsg}}</q-btn>
      <q-btn class="action-btn" flat color="secondary">Tell me another joke</q-btn>
    </q-card-actions>
  </div>
</template>

<script>
    export default {
      name: 'joke-feed',
      props: ['joke', 'statement'],
      data () {
        return {}
      },
      methods: {
        markFunny () {},
        getAnotherJoke () {
          console.log('another joke...')
        }
      }
    }
</script>

<style scoped>
  .action-btn {
    text-transform: capitalize;
    font-weight: normal;
  }
</style>
