<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <div style="width: 500px; max-width: 90vw;">
        <q-chat-message
          v-for="(msg, index) in messages"
          :key="`reg-${index}`"
          :label="msg.label"
          :sent="msg.sent"
          :text-color="msg.textColor"
          :bg-color="msg.bgColor"
          :name="msg.name"
          :avatar="getAvatar(msg)"
          :text="msg.text"
          :stamp="msg.stamp"
        />
        <q-chat-message
          name="Maggy"
          :avatar="avatars['1']"
        >
          <q-spinner-dots size="2rem" />
        </q-chat-message>
      </div>

      <div style="width: 500px; max-width: 90vw; padding: 20px;">
        <q-input type="textarea" name="new-comment" placeholder="Message" value="" />
        <q-btn class="action-btn" side="right" color="primary">Send</q-btn>
      </div>
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'chat',
  props: ['setupContent'],
  created () {
    this.setupContent({
      title: 'Chat'
    })
  },
  methods: {
    getAvatar (msg) {
      if (msg && ('id' in msg)) {
        return this.avatars[msg.id]
      }
    }
  },
  data () {
    return {
      avatars: {
        '1': this.$root.$options.user.circleCenter.profilePic,
        '2': this.$root.$options.user.profilePic
      },
      messages: [
        {
          label: 'Friday, 18th'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['How are you?'],
          stamp: 'Yesterday 13:34'
        },
        {
          name: 'John',
          id: '2',
          text: ['I\'m good, mom!', 'How is your day?'],
          sent: true,
          stamp: 'Yesterday at 13:50'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['Perfect!', 'Caressa is so cool that we can keep up with little to no effort!'],
          stamp: 'Yesterday at 13:52'
        },
        {
          name: 'John',
          id: '2',
          text: ['I know ma!', 'I love you.'],
          sent: true,
          stamp: 'Yesterday at 13:53'
        },

        {
          label: 'Sunday, 20th'
        },
        {
          name: 'John',
          id: '2',
          text: ['Nice weather here today. How is it over there?'],
          sent: true,
          stamp: 'Yesterday at 11:13'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['Pretty good.', 'By the way, my caregiver is with me now. We\'ll take a walk now'],
          stamp: 'Yesterday at 11:18'
        },
        {
          name: 'John',
          id: '2',
          text: ['That\'s great! Talk to you later mom'],
          sent: true,
          stamp: 'Yesterday at 11:19'
        }
      ]
    }
  }
}
</script>
