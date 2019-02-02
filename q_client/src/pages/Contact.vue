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
      <q-list v-if="queries.length > 0">
        <q-item>
        <q-item-main>
        <q-collapsible v-for="query in queries" :key="query.id"  group="queries" multiline>
          <template slot="header">
            <q-icon :name="query.solve_date ? 'fas fa-check' : 'far fa-clock'"
                    class="q-mr-md"
                    size="1.2em"
                    :color="query.solve_date ? 'tertiary' : 'warning'"/>
            <q-item-main :label="query.message.title ? query.message.title : 'No Title'" :sublabel="query.solve_date ? 'Solved' : 'Waiting'"/>
          </template>
            <p class="text-primary">{{query.message.main}}</p>
            <p>We will contact you from {{email}}</p>
        </q-collapsible>
        </q-item-main>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script>
import {Cookies} from 'quasar'
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
        console.log('contact form submit success', response)
        this.submitNotify()
      }, error => {
        console.log('error from Contact', error)
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
    },
    submitNotify: function () {
      this.$q.notify({
        message: 'Form Submitted',
        color: 'tertiary',
        icon: 'fas fa-check',
        timout: '3000',
        position: 'top-right',
        detail: `We will reach you from ${this.email}`
      })
    }
  },
  data () {
    return {
      contactFormMain: '',
      contactFormTitle: '',
      queries: [],
      email: Cookies.get('email')
    }
  },
  mounted () {
    this.loadQueries()
    this.setupContent({
      title: 'Reach Us'
    })
  }
}
</script>
<style lang="stylus">
  .main-content {
    width: 500px;
    max-width: 90vw;
  }
</style>
