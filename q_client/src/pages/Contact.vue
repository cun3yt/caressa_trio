<template>
  <q-page class="row justify-center">
    <div class="main-content">
      <q-item separator />
      <q-list>
        <q-list-header>Contact Us For Our Services</q-list-header>
        <q-item>
          <p class=" text-weight-thin">We will do our best!</p></q-item>
        <q-item class="q-pt-none">
          <q-input
            v-model="form.contactFormTitle"
            type="text"
            float-label="Enter the subject here"
            :error="$v.form.contactFormTitle.$error"
          >
          </q-input>
        </q-item>
        <q-item>
          <q-item-main>
            <q-input
              v-model="form.contactFormMain"
              type="textarea"
              float-label="Enter your message here"
              :max-height="100"
              rows="7"
              :error="$v.form.contactFormMain.$error"
            />
            <q-btn @click="submitFrom">Submit</q-btn>
          </q-item-main>
        </q-item>
      </q-list>
      <q-item separator />
      <q-list v-if="queries.length > 0">
        <q-item>
        <q-item-main>
        <q-collapsible v-for="query in queries" :key="query.id"  group="queries" multiline class="q-mb-xs shadow-1">
          <template slot="header">
            <q-icon :name="query.solved ? 'fas fa-check' : 'far fa-clock'"
                    class="q-mr-md"
                    size="1.2em"
                    :color="query.solved ? 'tertiary' : 'warning'"/>
            <q-item-main :label="query.message.title ? query.message.title : 'No Title'" :sublabel="query.solved ? 'Solved' : 'Waiting'"/>
          </template>
            <p class="text-primary">{{query.message.main}}</p>
            <p v-if="!query.solved" class="text-info text-weight-thin">We will contact you from <span class="text-weight-light">{{email}}</span></p>
        </q-collapsible>

        </q-item-main>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script>
import {Cookies} from 'quasar'
import { required } from 'vuelidate/lib/validators'

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
      this.$v.form.$touch()
      if (this.$v.form.$error) {
        this.$q.notify('Field is required')
        return
      }
      let vm = this
      vm.$auth.post(`${vm.$root.$options.hosts.rest}/act/queries/`, {
        'title': this.form.contactFormTitle,
        'main': this.form.contactFormMain
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
    },
    getScrollLocation () {
      this.$root.$options.scrollData.contact = window.scrollY
    }
  },
  activated () {
    document.addEventListener('scroll', this.getScrollLocation)
    window.scrollTo(0, this.$root.$options.scrollData.contact)
  },
  deactivated () {
    document.removeEventListener('scroll', this.getScrollLocation)
  },
  data () {
    return {
      form: {
        contactFormMain: '',
        contactFormTitle: ''
      },
      queries: [],
      email: Cookies.get('email')
    }
  },
  validations: {
    form: {
      contactFormMain: { required },
      contactFormTitle: { required }
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
