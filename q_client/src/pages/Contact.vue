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
            multiline
            class="bg-tertiary text-primary"
            icon="fas fa-check"
            label="Message sending problem"
            sublabel="Solved"
          >
            <p class="text-primary">I cannot send message to my mom!</p>
          </q-collapsible>
          <q-collapsible
            multiline
            class="bg-warning text-primary"
            icon="far fa-clock"
            label="Message recieving problem"
            sublabel="Working"
          >
            <p class="text-primary">I cannot send message to my mom!</p>
          </q-collapsible>
        <q-collapsible
          v-for="ticket in tickets"
          :key="ticket.id"
          group="oldInquiries"
          :icon="ticket.isSolved ? 'fas fa-check' : 'far fa-clock'"
          class="bg-positive"
        >
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
      return null // todo implement
    },
    loadOldInquiries: function () {
      return null // todo implement
    }
  },
  data () {
    return {
      contactFormMain: '',
      contactFormTitle: '',
      oldTickets: []
    }
  },
  mounted () {
    this.loadOldInquiries()
  }
}
</script>
<style lang="stylus">
  .main-content {
    width: 500px;
    max-width: 90vw;
  }
</style>
