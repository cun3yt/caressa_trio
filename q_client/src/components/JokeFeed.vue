<template>
    <q-card>
      <q-card-title>
        <span id="actor">{{ actor }}</span> Laughed At This Joke
      </q-card-title>
      <q-card-main class="row">
        <p>{{ joke.main }}</p>
        <p>{{ joke.punchline }}</p>
      </q-card-main>
      <q-card-separator />
      <q-card-actions>
        <q-btn flat label="That's funny!" />
        <q-btn flat label="Tell me another joke" />
      </q-card-actions>

      {{ something }}
    </q-card>
</template>

<script>
    export default {
      name: "joke-feed",
      props: ['actor', 'joke'],
      data () {
        return {
          something: 'data data...'
        }
      }
    }
</script>

<style scoped>
  #actor {
    font-weight: bold;
  }
</style>
