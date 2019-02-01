<template>
  <q-page class="row justify-center">
    <div class="main-content">
      <q-item separator />
      <q-list>
        <q-list-header>Contact Us</q-list-header>
        <q-item>
          <q-input
            v-model="contactFormTitle"
            type="text"
            float-label="Enter the subject here"
          >
          </q-input>
        </q-item>
        <q-item>
          <q-item-main>
            <q-input
              v-model="contactFormMain"
              type="textarea"
              float-label="Enter your message here"
              :max-height="100"
              rows="7"
            />
            <q-btn @click="submitFrom">Submit</q-btn>
          </q-item-main>
        </q-item>
      </q-list>
      <q-item separator />
      <q-list >
        <q-item>
        <q-item-main>
        <q-collapsible
          v-if="queries.length > 0"
          v-for="query in queries"
          :key="query.id"
          group="queries"
          multiline
          :class="query.solve_date ? 'bg-tertiary text-primary' : 'bg-warning text-primary'"
          :icon="query.solve_date ? 'fas fa-check' : 'far fa-clock'"
          :label="query.message.title ? query.message.title : 'No Title'"
          :sublabel="query.solve_date ? 'Solved' : 'Waiting'"
          >
          <p class="text-primary">{{query.message.main}}</p>
        </q-collapsible>
        </q-item-main>
        </q-item>
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
  methods: {
    submitFrom: function () {
      let vm = this
      vm.$auth.post(`${vm.$root.$options.hosts.rest}/act/queries/`, {
        'title': this.contactFormTitle,
        'main': this.contactFormMain
      }).then(response => {
        console.log(response, 'contact form submit success')
      }, response => {
        console.log(response, 'contact form submit error')
      })
    },
    loadQueries: function () {
      let vm = this
      vm.$auth.get(`${vm.$root.$options.hosts.rest}/act/queries/`)
        .then(response => {
          console.log(response.data.results, 'get form response')
          this.queries = response.data['results']
          console.log(this.queries)
        })
    }
  },
  data () {
    return {
      contactFormMain: '',
      contactFormTitle: '',
      queries: []
    }
  },
  mounted () {
    this.loadQueries()
  }
}
</script>
<style lang="stylus">
  .main-content {
    width: 500px;
    max-width: 90vw;
  }
</style>
