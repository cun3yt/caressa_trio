<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <q-list>
        <q-list-header>General</q-list-header>
        <q-item>
          <q-item-side>
            <q-item-tile icon="fas fa-user" color="primary" />
          </q-item-side>
          <q-item-main>
            <q-item-tile label>Edit Profile</q-item-tile>
            <q-item-tile sublabel>Change your profile picture</q-item-tile>
          </q-item-main>
          <q-item-side>
            <q-btn
              @click="toggleNewProfilePictureModal"
              color="primary"
              size="sm"
              icon="fas fa-pencil-alt"
            />
          </q-item-side>
        </q-item>
      </q-list><div class="q-pa-sm"></div>
      <q-list>
        <q-list-header>
         <q-item-main label="Music"></q-item-main>
        </q-list-header>
        <q-collapsible icon="fas fa-music" label="Genres"
                       :sublabel="musicSelectionStatus ? '' : `Please help us personalize music for ${senior.firstName}`">
          <q-list-header >What {{senior.firstName}} would love to listen?</q-list-header>
          <q-list v-if="genres.settings">
            <q-item v-for="(item, index) in genres.settings.genres" :key="`genre-${index}`" tag="label">
              <q-item-side>
                <q-checkbox v-model="item.is_selected" />
              </q-item-side>
              <q-item-main>
                <q-item-tile title>{{item.label}}</q-item-tile>
              </q-item-main>
            </q-item>
            <q-item>
                <q-item-main>
                <q-btn @click="sendInterests()" label="Apply" color="primary" size="0.9rem" icon="fas fa-check"/>
              </q-item-main>
              </q-item>
      </q-list>
          </q-collapsible>
      </q-list>
      <div class="q-pa-sm"></div>
      <q-list inset-separator>
        <q-list-header>
         <q-item-main label="Family"></q-item-main>
        </q-list-header>
        <q-item v-for="(member, index) in circleMembership.members" :key="`member-${index}`">
          <q-item-side>
            <q-item-tile icon="fas fa-user" color="primary" />
          </q-item-side>
            <q-item-main
              :label="`${member.first_name} ${member.last_name}`"
              label-lines="1"
              :sublabel="member.is_admin ? 'Admin' : ''"
              sublabel-lines="1"
            />
            <q-btn
              v-if="isAdmin"
              color="primary"
              size="sm"
              icon="fas fa-pencil-alt"
            />
        </q-item>
        <q-item v-for="(pendingMember, index) in circleMembership.pendings" :key="`pending_member-${index}`">
          <q-item-side>
            <q-item-tile icon="fas fa-user-clock" color="secondary" />
          </q-item-side>
          <q-item-main
            :label="pendingMember.email"
            sublabel="Pending"
            label-lines="1"
            sublabel-lines="1"
          />
          <q-btn
            color="secondary"
            size="sm"
            icon="fas fa-redo-alt"
            @click.native="reInviteMember(pendingMember.invitation_code, pendingMember.email)"
          />
        </q-item>
        <q-item v-if="isAdmin">
          <q-item-side>
            <q-item-tile icon="far fa-user" color="secondary"/>
          </q-item-side>
          <q-item-main label="Add Member">
            <q-input v-model="newMemberEmail" type="email" placeholder="email">
              <q-btn
                color="secondary"
                size="sm"
                icon="fas fa-plus"
                @click.native="newCircleMember"
              />
            </q-input>
          </q-item-main>
        </q-item>
      </q-list>
      <div class="q-pa-sm"></div>
      <q-list highlight>
        <q-list-header>Caressa</q-list-header>
        <q-item>
          <q-item-main>
            <q-item-tile label>About</q-item-tile>
            <q-item-tile sublabel>About Caressa</q-item-tile>
          </q-item-main>
        </q-item>
        <q-item>
          <q-item-main>
            <q-item-tile label>Version</q-item-tile>
            <q-item-tile sublabel>0.1.1</q-item-tile>
          </q-item-main>
        </q-item>
        <q-item>
          <q-item-main>
            <q-item-tile label>Reach Us</q-item-tile>
            <q-item-tile sublabel>info@caressa.ai</q-item-tile>
          </q-item-main>
        </q-item>
        <q-collapsible highlight>
          <template slot="header">
            <q-item-main label="Legal" />
          </template>
          <q-item @click.native="newPage('tos-v1')" >
            <q-item-main>
              <q-item-tile label>Terms of Service</q-item-tile>
            </q-item-main>
          </q-item>
          <q-item @click.native="newPage('open-source')" >
            <q-item-main>
              <q-item-tile label>Open Source Libraries</q-item-tile>
            </q-item-main>
          </q-item>
          <q-item @click.native="newPage('data-policy')" >
            <q-item-main>
              <q-item-tile label>Data Policy</q-item-tile>
            </q-item-main>
          </q-item>
        </q-collapsible>
      </q-list>
        <q-item>
          <q-btn
            style="background:white; color:#de5866"
            class="full-width"
            label="Sign Out Caressa"
            @click="signOut"
          />
        </q-item>
    </div>
    <q-page-container>
      <q-modal v-model="profilePictureData.updateProfilePictureModal" minimized content-css="padding: 8px" @hide="clearImage">
          <div class="q-display-1 q-mb-md">
            <span class="q-title">New Profile Picture</span>
            <q-btn color="red" style="float: right" v-close-overlay icon="fas fa-times" @click="clearImage"/>
          </div>
        <div v-if="profilePictureData.isLoading">
          <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
        </div>
        <div v-else>
          <div v-if="profilePictureData.croppingState">
            <div class="cut">
              <vue-cropper ref="cropper" :img="profilePictureData.option.img" :output-size="profilePictureData.option.size"
                           :output-type="profilePictureData.option.outputType" :can-move="profilePictureData.option.canMove"
                           :can-move-box="profilePictureData.option.canMoveBox"
                           :fixed-box="profilePictureData.option.fixedBox" :original="profilePictureData.option.original"
                           :auto-crop="profilePictureData.option.autoCrop"
                           :auto-crop-width="profilePictureData.option.autoCropWidth"
                           :auto-crop-height="profilePictureData.option.autoCropHeight"
                           :center-box="profilePictureData.option.centerBox" :high="profilePictureData.option.high"
                           :can-scale="profilePictureData.option.canScale" :info="profilePictureData.option.info"
                           :fixed="profilePictureData.option.fixed" :full="profilePictureData.option.full">
              </vue-cropper>
            </div>
            <q-btn v-if="!this.profilePictureData.signedUrl" color="tertiary" label="Looks Good!" @click="getCroppedFile"/>
          </div>
          <div v-if="!profilePictureData.croppingState">
            <div class="profile-pic">
              <img v-if="profilePictureData.file" class="image-container" :src="profilePictureData.option.img">
              <img v-else class="image-container" :src="profilePictureData.userProfilePic">
            </div>
            <span v-if="profilePictureData.option.img">
                <q-btn v-if="this.profilePictureData.signedUrl"
                       color="primary"
                       stlye="border-radius: 5px;"
                       label="Save Picture" @click="uploadPicture"/>
              </span>
            <span v-if="!profilePictureData.croppingState && !this.profilePictureData.signedUrl">
              <input id="file" class="inputfile" type="file" v-on:change="newFileFromInput" accept="image/*">
            <label for="file"><strong>Choose a file</strong></label>
            </span>
          </div>
          </div>
      </q-modal>
    </q-page-container>
  </q-page>
</template>

<script>
import { VueCropper } from 'vue-cropper'
import {bus} from '../plugins/auth.js'

export default {
  name: 'settings',
  components: {VueCropper},
  props: ['setupContent', 'logOut'],
  created () {
    this.setupContent({
      title: this.user
    })
  },
  data () {
    return {
      profilePictureData: {
        userProfilePic: this.$root.$options.user.profilePic,
        croppingState: false,
        option: {
          canScale: false,
          info: false,
          centerBox: true,
          fixed: true,
          img: '',
          size: 1,
          full: true,
          outputType: 'png',
          canMove: true,
          fixedBox: false,
          original: false,
          canMoveBox: true,
          autoCrop: true,
          autoCropWidth: 150,
          autoCropHeight: 150,
          high: true
        },
        updateProfilePictureModal: false,
        fileName: '',
        fileType: '',
        file: null,
        signedUrl: null,
        isLoading: false
      },
      senior: {},
      genres: [],
      circleMembership: {},
      isAdmin: false,
      newMemberEmail: '',
      circleId: null,
      option: 'opt1',
      select: 'fb',
      multipleSelect: ['goog', 'twtr'],
      selectOptions: [
        {
          label: 'Google',
          value: 'goog'
        },
        {
          label: 'Facebook',
          value: 'fb'
        },
        {
          label: 'Twitter',
          value: 'twtr'
        },
        {
          label: 'Apple Inc.',
          value: 'appl'
        },
        {
          label: 'Oracle',
          value: 'ora'
        }
      ],
      range: 20,
      doubleRange: {
        min: 10,
        max: 35
      }
    }
  },
  methods: {
    cordovaReadFile (fileEntry) {
      fileEntry.file(function (file) {
        let reader = new FileReader()
        reader.onloadend = function () {
          console.log('Successful file read:' + this.result)
        }
        reader.readAsText(file)
      })
    },
    cordovaSaveFile (fileData, fileName) {
      let vm = this
      window.resolveLocalFileSystemURL(cordova.file.documentsDirectory, function (dir) {
        dir.getFile(fileName, {create: true, exclusive: false}, function (fileEntry) {
          vm.cordovaWriteFile(fileEntry, fileData)
        })
      }, function (err) { console.log(err) })
    },
    cordovaWriteFile (fileEntry, dataObj, isAppend) {
      let vm = this
      fileEntry.createWriter(function (fileWriter) {
        fileWriter.onwriteend = function () {
          console.log('Successful file write...')
          if (dataObj.type === 'image/png') {
            vm.cordovaReadBinaryFile(fileEntry)
          } else {
            vm.cordovaReadFile(fileEntry)
          }
        }
        fileWriter.onerror = function (e) {
          console.log('Failed file write: ' + e.toString())
        }

        fileWriter.write(dataObj)
      })
    },
    cordovaReadBinaryFile (fileEntry) {
      let vm = this
      fileEntry.file(function (file) {
        let reader = new FileReader()

        reader.onloadend = function () {
          let blob = new Blob([new Uint8Array(this.result)], { type: 'image/png' })
          vm.profilePictureData.option.img = window.URL.createObjectURL(blob)
          vm.profilePictureData.file = blob
        }

        reader.readAsArrayBuffer(file)
      })
    },
    getCroppedFile () {
      let vm = this
      let file
      this.$refs.cropper.getCropBlob((data) => {
        file = new File([data], vm.profilePictureData.fileName, data.type)
        this.cordovaSaveFile(data, this.profilePictureData.fileName)
        // this.profilePictureData.option.img = window.URL.createObjectURL(file)
        // todo line above add junction point that decides environment and executes e.g. browser/ios/android.
        vm.getSignedUrl(file)
        vm.profilePictureData.file = file
        vm.profilePictureData.croppingState = false
      })
    },
    uploadPicture () {
      this.profilePictureData.isLoading = true
      this.$http({
        method: 'PUT',
        url: this.profilePictureData.signedUrl,
        body: this.profilePictureData.file,
        headers: {
          'Content-Type': this.profilePictureData.file.type
        }
      }).then(response => {
        this.toggleNewProfilePictureModal()
        this.showNotif({message: 'Success', icon: 'far fa-check-circle', color: 'tertiary'})
        console.log(response)
        this.newProfilePicture()
      }).catch(err => {
        this.profilePictureData.isLoading = false
        console.log(err)
        this.showNotif({message: 'Failed', icon: 'fas fa-times', color: 'negative'})
      })
    },
    clearImage () {
      this.profilePictureData.croppingState = false
      this.profilePictureData.option.img = ''
      this.profilePictureData.isLoading = false
      this.profilePictureData.updateProfilePictureModal = false
      this.profilePictureData.fileName = ''
      this.profilePictureData.fileType = ''
      this.profilePictureData.file = null
      this.profilePictureData.signedUrl = null
    },
    newFileFromInput (inputFile) {
      const files = inputFile.target.files || inputFile.dataTransfer.files
      this.profilePictureData.option.img = window.URL.createObjectURL(files[0])
      this.profilePictureData.fileName = this.randomFileName()
      this.profilePictureData.croppingState = true
    },
    randomFileName () {
      const randomInt = Math.random().toString(36).substring(2, 15)
      return `new_profile_pic_${randomInt}`
    },
    async getSignedUrl (file) {
      const contentType = file.type // To send the correct Content-Type
      const fileName = this.profilePictureData.fileName // If you want to use this value to calculate the S3 Key.
      const response = await this.getPresignedUrl(fileName, contentType) // Your api call to a sever that calculates the signed url.
      this.profilePictureData.signedUrl = response.body
    },
    newPage (link) {
      const baseUrl = 'https://www.caressa.ai/'
      window.open(baseUrl + link)
    },
    toggleNewProfilePictureModal () {
      this.profilePictureData.updateProfilePictureModal = !this.profilePictureData.updateProfilePictureModal
    },
    sendInterests () {
      this.$auth.patch(`${this.$root.$options.hosts.rest}/api/users/${this.senior.id}/settings/`, this.genres)
        .then(res => {
          console.log(res.body)
        })
    },
    signOut: function () {
      this.logOut()
    },
    getPresignedUrl (fileName, contentType) {
      this.profilePictureData.isLoading = true
      return this.$auth.post(`${this.$root.$options.hosts.rest}/generate_signed_url/`, {
        'key': fileName,
        'content-type': contentType,
        'client-method': 'put_object',
        'request-type': 'PUT'
      }).then(success => {
        this.profilePictureData.isLoading = false
        return success
      }, error => {
        this.showNotif({message: 'Something is Wrong', icon: 'fas fa-times', color: 'negative'})
        this.clearImage()
        return error
      })
    },
    newProfilePicture () {
      this.$auth.post(`${this.$root.$options.hosts.rest}/new_profile_picture/`, {
        'file_name': this.profilePictureData.fileName
      }).then(res => {
        this.profilePictureData.isLoading = false
      })
    },
    showNotif (data) {
      this.$q.notify({
        color: data.color,
        message: data.message,
        position: 'top-right',
        icon: data.icon
      })
    },
    setInitialData () {
      this.senior = this.$root.$options.senior

      if (!this.senior || !this.senior.id) { return }

      let vm = this
      this.$auth.get(`${this.$root.$options.hosts.rest}/api/users/${this.senior.id}/settings/`)
        .then(function (res) {
          vm.genres = res.body
          vm.genres.settings.genres.sort((item1, item2) => { return item1.label < item2.label ? -1 : 1 })
        })

      this.$auth.get(`${this.$root.$options.hosts.rest}/api/users/me/circles/`)
        .then(res => {
          this.circleId = res.body.pk
          this.circleMembership = {
            'members': res.body.members,
            'pendings': res.body.pending_invitations
          }
          let userInCircleArray = res.body.members.filter((member) => { return vm.$root.$options.user.id === member.pk })
          if (userInCircleArray.length > 0) {
            vm.isAdmin = userInCircleArray[0].is_admin
          }
        })
    },
    newCircleMember () {
      this.$auth.post(`${this.$root.$options.hosts.rest}/api/circles/${this.circleId}/members/invite/`, {'email': this.newMemberEmail})
        .then(res => {
          this.showNotif({message: `An email was sent to ${this.newMemberEmail}`, icon: 'far fa-check-circle', color: 'tertiary'})
          this.circleMembers.push({first_name: this.newMemberEmail, last_name: '(pending)', is_admin: false})
          this.newMemberEmail = ''
        }, err => {
          this.showNotif({message: 'Something went wrong, please try again.', icon: 'fas fa-times', color: 'negative'})
          console.error(err)
        })
    },
    reInviteMember (invitationCode, contact) {
      let data = {
        'invitation_code': invitationCode
      }
      this.$auth.post(
        `${this.$root.$options.hosts.rest}/api/circles/${this.circleId}/members/reinvite/`, data)
        .then(res => {
          this.showNotif({message: `Invitation was re-sent to ${contact}`, icon: 'far fa-check-circle', color: 'tertiary'})
        }, err => {
          this.showNotif({message: 'Something went wrong, please try again.', icon: 'fas fa-times', color: 'negative'})
          console.error(err)
        })
    }
  },
  mounted () {
    this.setInitialData()
    bus.$on('loginSuccessRedirect', this.setInitialData)
  },
  computed: {
    musicSelectionStatus () {
      if (this.genres.length === 0) {
        return false
      }
      return this.genres.settings.genres.filter((genre) => { return genre.is_selected }).length > 0
    }
  }
}
</script>

<style scoped lang="stylus">
.main-content {
  width: 500px;
  max-width: 90vw;
}

.cut {
  width: 225px;
  height: 225px;
  margin: 5px auto;
}

.profile-pic {
  width: 225px;
  height: 225px;
  margin: 5px auto;
}

.inputfile {
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
}

.image-container {
  max-width: 100%
}

.inputfile + label {
  background: #f15d22;
  border: none;
  border-radius: 5px;
  color: #fff;
  cursor: pointer;
  display: inline-block;
  font-family: 'Poppins', sans-serif;
  font-size: inherit;
  font-weight: 600;
  margin-bottom: 1rem;
  outline: none;
  padding: 1rem 30px;
  position: relative;
  transition: all 0.3s;
  vertical-align: middle;
}
</style>
