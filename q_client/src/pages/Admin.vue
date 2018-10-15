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
      </div>

      <div style="width: 500px; max-width: 90vw; padding: 20px;">
        <q-input type="textarea" ref="newMessage" name="newMessage" placeholder="Message" v-model="messageText" value=""/>
        <q-btn class="action-btn" @click="sendMessage" side="right" color="primary">Send Message</q-btn>
        <q-btn class="action-btn" @click="uploadRecord" side="right" color="primary">Send the record</q-btn>
        <q-btn v-on:mousedown.native="startRecord"
               v-on:touchstart.native="startRecord"
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
      title: 'Maggy'
    })
  },
  methods: {
    getAvatar (msg) {
      if (msg && ('id' in msg)) {
        return this.avatars[msg.id]
      }
    },
    sendMessage: function () {
      console.log('sending message')
      console.log(this.$refs.newMessage.value)
      let textMessageObj = {}
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
      textMessageObj.key = key
      textMessageObj.name = 'John'
      textMessageObj.sent = true
      textMessageObj.id = '2'
      textMessageObj.stamp = 'Today at 13:50'
      textMessageObj.type = 'text'
      textMessageObj.text = []

      this.textMessageObj = textMessageObj

      if (this.messageText !== '') {
        this.textMessageObj.text.push(this.messageText)
      }(this.messages.push(this.textMessageObj))
      this.$http.post(`${this.$root.$options.hosts.rest}/new_message/`, {
        'userId': textMessageObj.id,
        'type': 'text',
        'key': key,
        'content': this.textMessageObj
      }).then(response => {
        this.messageText = ''
      })
    },
    startRecord: function () {
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
      this.audioMessageObj.key = key
      let newRecord = key + '.wav'

      let src = 'documents://' + newRecord
      let mediaRec = new window.Media(src,
        function () {
          console.log('recordAudio():Audio Success')
          console.log('cordova.file.documentsDirectory : ' + cordova.file.documentsDirectory)
        },
        function (err) {
          console.log('recordAudio():Audio Error: ')
          console.log(err)
        })
      mediaRec.startRecord()

      setTimeout(function () {
        mediaRec.stopRecord()
      }, 2000)
    },
    stopRecord: function () {
      // TODO: need to be implemented.
      console.log('No Effect')
    },
    playRecord: function () {
      let myMedia = new window.Media(this.audioMessageObj.url)
      myMedia.play()
    },
    uploadRecord: function () {
      this.$http.post(`${this.$root.$options.hosts.rest}/generate_signed_url/`, {
        'userId': this.$root.$options.user.id,
        'audio': 'audio',
        'job-type': '1',
        'key': this.audioMessageObj.key,
        'content-type': 'audio/wav',
        'client-method': 'put_object',
        'request-type': 'PUT'
      }).then(response => {
        console.log('response :' + response.body)

        let vm = this
        let ft = new window.FileTransfer()
        var options = new window.FileUploadOptions()
        options.fileKey = this.audioMessageObj.key
        console.log('OPTIONS FILE KEY:' + this.audioMessageObj.key)
        options.chunkedMode = false
        options.httpMethod = 'PUT'
        options.mimeType = 'audio/wav'
        options.headers = {
          'Content-Type': 'audio/wav'
        }
        window.resolveLocalFileSystemURL(cordova.file.documentsDirectory, function (dir) {
          console.log('got main dir', dir)
          dir.getFile(vm.audioMessageObj.key + '.wav', {create: true}, function (file) {
            console.log('file itself', file)
            ft.upload(file.nativeURL, response.body,
              function (res) {
                console.log('response : ' + res)
                vm.$http.post(`${vm.$root.$options.hosts.rest}/new_message/`, {
                  'userId': vm.$root.$options.user.id,
                  'type': 'ios-audio',
                  'key': vm.audioMessageObj.key
                }).then(response => {
                  console.log(response)
                })
              },
              function (error) {
                debugger
                console.log(error)
              },
              options)
            console.log('got the file')
            // console.log(audioFormData)
          }, function (err) { console.log(err) })
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
      formData1: [],
      audio: {},
      avatars: {
        '1': this.$root.$options.user.circleCenter.profilePic,
        '2': this.$root.$options.user.profilePic
      },
      messageText: '',
      textMessageObj: {},
      audioMessageObj: {},
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
