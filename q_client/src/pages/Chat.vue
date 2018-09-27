<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <div style="width: 500px; max-width: 90vw;">
        <div v-for="(msg, index) in messages" :key="`reg-${index}`">
          <q-chat-message
          v-if="msg.type == 'text'"
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
            v-else-if="msg.type == 'audio'"
            :key="`reg-${index}`"
            :label="msg.label"
            :sent="msg.sent"
            :text-color="msg.textColor"
            :bg-color="msg.bgColor"
            :name="msg.name"
            :avatar="getAvatar(msg)"
            :stamp="msg.stamp"
          >
          <q-btn round icon="play_arrow" color="brown" @click="playRecord(msg.url)">  </q-btn>
          </q-chat-message>
        </div>
        <q-chat-message
          name="Maggy"
          :avatar="avatars['1']"
        >
          <q-spinner-dots size="2rem" />
        </q-chat-message>
      </div>

      <div style="width: 500px; max-width: 90vw; padding: 20px;">
        <q-input type="textarea" name="new-comment" placeholder="Message" value="" />
        <q-btn class="action-btn" side="right" color="primary">Send Message</q-btn>
        <q-btn v-on:mousedown.native="startRecord"
        v-on:mouseleave.native="stopRecord"
        v-on:mouseup.native="stopRecord"
        v-on:touchstart.native="startRecord"
        v-on:touchend.native="stopRecord"
        v-on:touchcancel.native="stopRecord"
        side="left"
        style="margin-left: 20em"
        round
        color="info"
        icon='mic'></q-btn>
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
    },
    startRecord: function () {
      console.log('recording start')
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        this.audio.mediaRecorder = new MediaRecorder(stream)
        this.audio.mediaRecorder.start()
        let messageObj = {}
        let today = new Date()
        let dd = today.getDate()
        let mm = today.getMonth() + 1
        let yyyy = today.getFullYear()

        if (dd < 10) {
          dd = '0' + dd
        }
        if (mm < 10) {
          mm = '0' + mm
        }
        today = mm + '-' + dd + '-' + yyyy
        let randomInt = Math.floor(Math.random() * Math.floor(99999999))

        let key = today + '-' + randomInt
        messageObj.key = key
        messageObj.name = 'John'
        messageObj.sent = true
        messageObj.id = '2'
        messageObj.stamp = 'Today at 13:50'
        messageObj.type = 'audio'
        messageObj.audioChunks = []

        this.messageObj = messageObj

        this.audio.mediaRecorder.addEventListener('dataavailable', event => {
          this.messageObj.audioChunks.push(event.data)
          console.log(this.messageObj)
        })
      })
    },
    stopRecord: function () {
      if (this.audio.mediaRecorder && this.audio.mediaRecorder.state === 'recording') {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
          this.audio.mediaRecorder.addEventListener('stop', () => {
            const audioArray = this.messageObj.audioChunks
            const audioBlob = new Blob(audioArray)
            const audioUrl = URL.createObjectURL(audioBlob)
            this.messageObj.url = audioUrl
          })
          this.audio.mediaRecorder.stop()
        }).then(data => {
          this.uploadRecord()
        })
      }
    },
    playRecord: function (url) {
      const audio = new Audio(url)
      audio.play()
    },
    uploadRecord: function () {
      this.$http.post(`${this.$root.$options.hosts.rest}/generate_signed_url/`, {
        'userId': this.$root.$options.user.id,
        'audio': 'audio',
        'job-type': '1',
        'key': this.messageObj.key
      }).then(response => {
        let responseBody = response.body['fields']
        let boundary = Math.random().toString().substr(2)
        let key = responseBody['key']
        let AWSAccessKeyId = responseBody['AWSAccessKeyId']
        let policy = responseBody['policy']
        let signature = responseBody['signature']
        let headers = {
          'Content-Type': 'multipart/form-data; boundary=' + boundary
        }
        const audioArray = this.messageObj.audioChunks
        const audioBlob = new Blob(audioArray)
        let fileContent = audioBlob
        var audioFormData = new FormData()
        audioFormData.append('key', this.messageObj.key)
        audioFormData.append('AWSAccessKeyId', AWSAccessKeyId)
        audioFormData.append('policy', policy)
        audioFormData.append('signature', signature)
        audioFormData.append('file', fileContent)
        this.$http.post('https://caressa-upload.s3.amazonaws.com/', audioFormData, {headers})
          .then(response => {
            this.$http.post(`${this.$root.$options.hosts.rest}/new_message/`, {
              'userId': this.$root.$options.user.id,
              'type': 'audio',
              'key': key
            }).then(response => {
              this.showNotif('Audio')
              this.messages.push(this.messageObj)
            })
          })
      })
    },
    showNotif: function (data) {
      this.$q.notify({
        color: 'secondary',
        message: data + ' is submitted.',
        position: 'top-right',
        icon: 'check_circle_outline'
        // detail: this.toString()
      })
    }
  },
  data () {
    return {
      audio: {},
      avatars: {
        '1': this.$root.$options.user.circleCenter.profilePic,
        '2': this.$root.$options.user.profilePic
      },
      messages: [
        {
          label: 'Friday, 18th',
          type: 'text'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['How are you?'],
          stamp: 'Yesterday 13:34',
          type: 'text'
        },
        {
          name: 'John',
          id: '2',
          text: ['I\'m good, mom!', 'How is your day?'],
          sent: true,
          stamp: 'Yesterday at 13:50',
          type: 'text'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['Perfect!', 'Caressa is so cool that we can keep up with little to no effort!'],
          stamp: 'Yesterday at 13:52',
          type: 'text'
        },
        {
          name: 'John',
          id: '2',
          text: ['I know ma!', 'I love you.'],
          sent: true,
          stamp: 'Yesterday at 13:53',
          type: 'text'
        },

        {
          label: 'Sunday, 20th',
          type: 'text'
        },
        {
          name: 'John',
          id: '2',
          text: ['Nice weather here today. How is it over there?'],
          sent: true,
          stamp: 'Yesterday at 11:13',
          type: 'text'
        },
        {
          name: 'Maggy',
          id: '1',
          text: ['Pretty good.', 'By the way, my caregiver is with me now. We\'ll take a walk now'],
          stamp: 'Yesterday at 11:18',
          type: 'text'
        },
        {
          name: 'John',
          id: '2',
          text: ['That\'s great! Talk to you later mom'],
          sent: true,
          stamp: 'Yesterday at 11:19',
          type: 'text'
        }
      ]
    }
  }
}
</script>
