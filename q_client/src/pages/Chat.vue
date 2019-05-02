<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <div v-if="isLoading">
        <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
      </div>
      <div v-else-if="error">
        Could not connect to the server for device status.
      </div>
      <div v-else>
        <div :class="isOnline ? 'online' : 'offline'"><i class="fas fa-circle"></i> {{ deviceStatus }}</div>
      </div>
      <div style="width: 500px; max-width: 90vw;">
        <div v-for="(msg, index) in messages" :key="`reg-${index}`">
          <q-chat-message
            v-if="msg.type === 'family_ios_text'"
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
            v-else-if="msg.type === 'audio'"
            :key="`reg-${index}`"
            :label="msg.label"
            :sent="msg.sent"
            :text-color="msg.textColor"
            :bg-color="msg.bgColor"
            :name="msg.name"
            :avatar="getAvatar(msg)"
            :stamp="msg.stamp"
          >
            <q-btn round icon="fas fa-play" color="brown" @click="playRecord">  </q-btn>
          </q-chat-message>
        </div>
      </div>

      <q-page-sticky position="bottom" :offset="[10, 10]">
      <div style="width: 500px; max-width: 90vw; padding: 20px;">
        <q-input type="textarea" ref="newMessage" name="newMessage" placeholder="Message" v-model="messageText" value=""/>
        <q-btn :disable="recording!=null" class="action-btn" @click="sendMessage" side="right" color="primary">Send Message</q-btn>
      </div>

      <div class="doc-container with-bg">
        <div class="row justify-center">
          <q-spinner-bars class="col-2" v-if="recordingState" color="negative" :size="60" />
          <q-spinner-bars class="col-2" v-if="recordingState" color="negative" :size="60" />
        </div>
        </div>
      <div class="row justify-start">
        <div class="col-2" style="padding-top: 3em; padding-left: 3em">
          <q-btn v-if="audioMessageObj.key && audioMessageObj.sent === false" v-on:mousedown.native="deleteRecord"
                 v-on:touchstart.native="deleteRecord"
                 side="left"
                 size="20px"
                 round
                 color="negative"
                 icon="fas fa-trash"></q-btn>
        </div>
        <div class="col-2"></div>
        <q-btn v-if="audioMessageObj.key && audioMessageObj.sent === false"
               class="col-4" v-on:mousedown.native="uploadRecord"
               v-on:touchstart.native="uploadRecord"
               side="left"
               size="40px"
               style="padding-right: 0.2em"
               round
               color="positive"
               icon="fas fa-paper-plane"
        ></q-btn>
        <q-btn v-else class="col-4" v-on:mousedown.native="toggleRecord"
               v-on:touchstart.native="toggleRecord"
               side="left"
               size="40px"
               round
               :outline="recordingState"
               :color="recordingState ? 'negative' : 'primary' "
               :icon="recordingState ? 'fas fa-stop' : 'fas fa-microphone'"></q-btn>
        <div class="col-2" style="padding-top: 3em; padding-left: 1em">
          <q-btn v-if="audioMessageObj.key && audioMessageObj.sent === false" v-on:mousedown.native="playRecord"
                 v-on:touchstart.native="playRecord"
                 side="left"
                 size="20px"
                 style="padding-left: 0.3em"
                 round
                 color="info"
                 icon="fas fa-play"></q-btn>
        </div>

      </div>
      </q-page-sticky>
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
      let key = 'Text Message'
      textMessageObj.key = key
      textMessageObj.sent = true
      textMessageObj.stamp = 'Today at 13:50'
      textMessageObj.type = 'family_ios_text'
      textMessageObj.text = []

      this.textMessageObj = textMessageObj

      if (this.messageText !== '') {
        this.textMessageObj.text.push(this.messageText)
      }(this.messages.push(this.textMessageObj))
      this.$auth.post(`${this.$root.$options.hosts.rest}/new_message/`, {
        'type': 'family_ios_text',
        'key': key,
        'content': this.messageText
      }).then(response => {
        console.log('Response : ', response)
        this.messageText = ''
      })
    },
    toggleRecord: function () {
      if (!this.recordingState) {
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
        this.audioMessageObj.url = src
        this.recording = new window.Media(src,
          function () {
            console.log('recordAudio():Audio Success')
            console.log('cordova.file.documentsDirectory : ' + cordova.file.documentsDirectory)
          },
          function (err) {
            console.log('recordAudio():Audio Error: ')
            console.log(err)
          })
        this.recording.startRecord()
        this.recordingState = true
      } else {
        this.recording.stopRecord()
        this.recordingState = false
        this.audioMessageObj.sent = false
      }
    },
    deleteRecord: function () {
      this.audioMessageObj = {}
      this.recording = null
      this.showNotif('Record Deleted')
    },
    playRecord: function () {
      let vm = this
      let myMedia = new window.Media(vm.audioMessageObj.url,
        function () {
          console.log('playAudio():Audio Success')
          console.log(vm.audioMessageObj.url)
        },
        // error callback
        function (err) {
          console.log('playAudio():Audio Error: ')
          console.dir(err)
        })
      myMedia.play()
    },
    uploadRecord: function () {
      this.$auth.post(`${this.$root.$options.hosts.rest}/generate-signed-url/`, [{
        'key': this.audioMessageObj.key,
        'content-type': 'audio/wav',
        'client-method': 'put_object',
        'request-type': 'PUT'
      }]).then(response => {
        console.log('response :' + response.body)

        let vm = this
        let ft = new window.FileTransfer()
        let options = new window.FileUploadOptions()
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
              function (response) {
                console.log(response)
                vm.$auth.post(`${vm.$root.$options.hosts.rest}/new_message/`, {
                  'userId': vm.$root.$options.user.id,
                  'type': 'family_ios_audio',
                  'key': vm.audioMessageObj.key
                }).then(response => {
                  console.log('Response: ', response)
                  vm.showNotif('Audio Submitted')
                  vm.audioMessageObj.name = 'John' // todo move to `hard-coding`
                  vm.audioMessageObj.sent = true
                  vm.audioMessageObj.id = '2'
                  vm.audioMessageObj.stamp = 'Today at 13:50'
                  vm.audioMessageObj.type = 'audio'
                  vm.messages.push(vm.audioMessageObj)
                  vm.recording = null
                })
              },
              function (error) {
                console.log(error)
              },
              options)

            console.log('got the file')
          }, function (err) { console.log(err) })
        })
      })
    },
    showNotif: function (data) {
      this.$q.notify({
        color: 'secondary',
        message: data,
        position: 'top-right',
        icon: 'far fa-check-circle'
        // detail: this.toString()
      })
    }
  },
  data () {
    return {
      isLoading: true,
      error: null,
      senior: null,
      formData1: [],
      audio: {},
      avatars: {
        '1': this.$root.$options.senior.profilePic,
        '2': this.$root.$options.user.profilePic
      },
      messageText: '',
      textMessageObj: {},
      audioMessageObj: {},
      recordingState: false,
      recording: null,
      messages: [
        {
          label: 'Mon, 22th', // todo move to `hard-coding`
          type: 'text'
        }
      ]
    }
  },
  mounted () {
    let deviceCheckFn = () => {
      this.$auth.get(`${this.$root.$options.hosts.rest}/api/users/me/circles/`)
        .then(response => {
          this.isLoading = false
          this.senior = response.body.senior
          setTimeout(deviceCheckFn, 300000)
        }, error => {
          this.isLoading = false
          this.error = error
          setTimeout(deviceCheckFn, 300000)
        })
    }

    deviceCheckFn()
  },
  computed: {
    deviceStatus () {
      if (!this.senior.device_status) {
        return 'Device Not Found'
      }
      if (this.senior.device_status.is_online) {
        return 'Online'
      }
      return 'Offline'
    },
    isOnline: function () {
      return this.senior.device_status && this.senior.device_status.is_online
    }
  }
}
</script>
<style scoped>
  .online {
    color: #4caba5
  }
  .offline {
    color: #ef4b63
  }
</style>
