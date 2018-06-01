<template>
  <div class="main-content">
    <!--<q-page padding class="row justify-center">-->
      <div style="width: 500px; max-width: 90vw;">
        <q-chat-message
          v-for="(msg, index) in messages"
          :key="`reg-${index}`"
          :label="msg.label"
          :sent="msg.sent"
          :text-color="msg.textColor"
          :bg-color="msg.bgColor"
          :name="msg.name"
          :avatar="msg.avatar"
          :text="msg.text"
          :stamp="msg.stamp"
        />
        <q-chat-message
          name="Maggy"
          avatar="statics/grandma-avatar.png"
        >
          <q-spinner-dots size="2rem" />
        </q-chat-message>
      </div>

      <div style="width: 500px; max-width: 90vw; padding: 20px;">
        <q-input type="textarea" name="new-comment" placeholder="Message" />
        <q-btn class="action-btn" side="right" color="primary">Send</q-btn>
      </div>
    <!--</q-page>-->
  </div>
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
    data () {
      return {
        message: '',
        messages: [
          {
            label: 'Friday, 18th'
          },
          {
            name: 'Maggy',
            text: ['How are you?'],
            avatar: 'statics/grandma-avatar.png',
            stamp: 'Yesterday 13:34'
          },
          {
            name: 'John',
            text: ['I\'m good, mom!', 'How is your day?'],
            sent: true,
            avatar: 'statics/man-avatar.png',
            stamp: 'Yesterday at 13:50'
          },
          {
            name: 'Maggy',
            text: ['Perfect!', 'Caressa is so cool that we can keep up with little to no effort!'],
            avatar: 'statics/grandma-avatar.png',
            stamp: 'Yesterday at 13:52'
          },
          {
            name: 'John',
            text: ['I know ma!', 'I love you.'],
            sent: true,
            avatar: 'statics/man-avatar.png',
            stamp: 'Yesterday at 13:53'
          },

          {
            label: 'Sunday, 20th'
          },
          {
            name: 'John',
            text: ['Nice weather here today. How is it over there?'],
            sent: true,
            avatar: 'statics/man-avatar.png',
            stamp: 'Yesterday at 11:13'
          },
          {
            name: '',
            text: ['Pretty good.', 'By the way, my caregiver is with me now. We\'ll take a walk now'],
            avatar: 'statics/grandma-avatar.png',
            stamp: 'Yesterday at 11:18'
          },
          {
            name: 'John',
            text: ['That\'s great! Talk to you later mom'],
            sent: true,
            avatar: 'statics/man-avatar.png',
            stamp: 'Yesterday at 11:19'
          }
        ]
      }
    }
  }
</script>
