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
            <q-item-tile sublabel>Change your circle profile</q-item-tile>
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
        <q-item>
          <q-item-side>
            <q-item-tile icon="fas fa-question-circle" color="primary" />
          </q-item-side>
          <q-item-main>
            <q-item-tile label>Help</q-item-tile>
            <q-item-tile sublabel>Ask us anything</q-item-tile>
          </q-item-main>
          <q-item-side>
            <q-btn
              color="primary"
              size="sm"
              icon="fas fa-phone"
            />
          </q-item-side>
        </q-item>
        <q-collapsible highlight>
          <template slot="header">
            <q-item-side icon="fas fa-exclamation-circle" color="primary" small>
            </q-item-side>
            <q-item-main label="Submit Feedback" />
          </template>
            <textarea placeholder="What went wrong?" class="full-width no-border"></textarea>
        </q-collapsible>
      </q-list><div class="q-pa-sm"></div>
      <q-list>
        <q-list-header>
         <q-item-main label="Personalize"></q-item-main>
        </q-list-header>
        <q-collapsible icon="fas fa-music" label="Music Genres">
          <q-list-header >What {{user}} would love to listen?</q-list-header>
          <q-list>
            <q-item v-for="(item, index) in genres" :key="index" tag="label">
              <q-item-side>
                <q-checkbox v-model="genres[index].checked" />
              </q-item-side>
              <q-item-main>
                <q-item-tile title>{{genres[index].genre}}</q-item-tile>
              </q-item-main>
            </q-item>
            <q-item>
                <q-item-main>
                <q-btn @click="sendInterests('genres')" label="Apply" color="primary" size="0.9rem" icon="fas fa-check"/>
              </q-item-main>
              </q-item>
      </q-list>
          </q-collapsible>
      </q-list>
      <div class="q-pa-sm"></div>
      <q-list>
        <q-list-header>
         <q-item-main label="Circle Control"></q-item-main>
        </q-list-header>
            <q-list highlight>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-envelope" color="primary"/>
                </q-item-side>
                <q-item-main>
                  <q-input value="" type="email" stack-label="New Member Mail" />
                </q-item-main>
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-clipboard-list" color="primary" />
                </q-item-side>
                <q-item-main>
                <q-btn-dropdown
                  color="primary"
                  label="Pick Role"
                >
                  <q-list link>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="fas fa-user-tie" inverted color="positive" />
                      <q-item-main>
                        <q-item-tile label>Family Member</q-item-tile>
                      </q-item-main>
                    </q-item>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="fas fa-user-tie" inverted color="positive" />
                      <q-item-main>
                        <q-item-tile label>Caregiver</q-item-tile>
                      </q-item-main>
                    </q-item>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="fas fa-building" inverted color="positive" />
                      <q-item-main>
                        <q-item-tile label>Caregiver Org.</q-item-tile>
                      </q-item-main>
                    </q-item>
                  </q-list>
                </q-btn-dropdown>
                  </q-item-main>
              </q-item>
              <q-item>
                <q-item-main>
                <q-btn
                  label="Add"
                  color="primary"
                  size="sm"
                  icon="fas fa-plus"
                />
              </q-item-main>
              </q-item>
            </q-list>
        <q-collapsible icon="fas fa-users-cog" label="Circle Members">
            <q-list highlight inset-separator>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-user" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Marie D."
                  label-lines="1"
                  sublabel="Caretaker"
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="fas fa-pencil-alt"
                />
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-user" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Andrew D."
                  label-lines="1"
                  sublabel="Family"
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="fas fa-pencil-alt"
                />
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-user" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Lisa W."
                  label-lines="1"
                  sublabel="Family"
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="fas fa-pencil-alt"
                />
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-user-tie" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Tracy S."
                  label-lines="1"
                  sublabel="Caregiver"
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="fas fa-pencil-alt"
                />
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="fas fa-building" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Longevity Corp."
                  label-lines="1"
                  sublabel="Caregiver Org."
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="fas fa-pencil-alt"
                />
              </q-item>
            </q-list>
          </q-collapsible>
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
      <q-modal v-model="profilePictureData.updateProfilePictureModal " minimized>
        <div style="padding: 10px">
          <div class="q-display-1 q-mb-md">New Profile Picture</div>
          <div v-if="profilePictureData.croppingState">
            <div class="cut">
              <vue-cropper ref="cropper" :img="profilePictureData.option.img" :output-size="profilePictureData.option.size"
                           :output-type="profilePictureData.option.outputType" :can-move="profilePictureData.option.canMove"
                           :can-move-box="profilePictureData.option.canMoveBox"
                           :fixed-box="profilePictureData.option.fixedBox" :original="profilePictureData.option.original"
                           :auto-crop="profilePictureData.option.autoCrop"
                           :auto-crop-width="profilePictureData.option.autoCropWidth"
                           :auto-crop-height="profilePictureData.option.autoCropHeight"
                           :center-box="profilePictureData.option.centerBox" @real-time="realTime"
                           :high="profilePictureData.option.high" @img-load="imgLoad"
                           :can-scale="profilePictureData.option.canScale" :info="profilePictureData.option.info"
                           :fixed="profilePictureData.option.fixed" :full="profilePictureData.option.full">
              </vue-cropper>
            </div>
          </div>
          <img v-if="profilePictureData.croppedImage" :src="profilePictureData.croppedImage">
            <div>
              <input id="file" class="inputfile" type="file" v-on:change="newFileFromInput" accept="image/*">
              <label for="file"><strong>Choose a file</strong></label>
              <q-btn label="Looks Good" @click="getCroppedFile"/>
              <q-btn label="Change Picture" @click="uploadPicture"/>
            </div>
            <q-btn color="red" v-close-overlay label="Close" />
        </div>
      </q-modal>
    </q-page-container>
  </q-page>
</template>

<script>
import { VueCropper } from 'vue-cropper'
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
        croppingState: false,
        option: {
          canScale: false,
          info: false,
          centerBox: true,
          fixed: false,
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
        previews: {},
        cropperLabels: {
          submit: 'Looks Good!',
          cancel: 'Cancel'
        },
        croppedImage: null,
        updateProfilePictureModal: false,
        generatadPreSignedUrl: '',
        fileName: '',
        fileType: '',
        file: null,
        signedUrl: null
      },
      user: 'Maggy',
      genres: [
        {
          'genre': 'Classical',
          'checked': false
        },
        {
          'genre': 'Jazz',
          'checked': false
        },
        {
          'genre': 'Blues',
          'checked': false
        },
        {
          'genre': 'Pop',
          'checked': false
        },
        {
          'genre': 'R&B',
          'checked': false
        }
      ],
      checked_one: true,
      checked_two: false,
      checked_three: false,
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
    getCroppedFile () {
      let vm = this
      let file
      this.$refs.cropper.getCropBlob((data) => {
        file = new File([data], vm.profilePictureData.fileName, {type: data.type})
        vm.getSignedUrl(file)
        vm.profilePictureData.file = file
        vm.profilePictureData.croppingState = false
      })
    },
    realTime (data) {
      this.profilePictureData.previews = data
      console.log(data)
    },
    imgLoad (msg) {
      console.log(msg)
    },
    cropSubmit () {
      console.log(this.profilePictureData)
      this.profilePictureData.croppedImage = this.profilePictureData.file
    },
    uploadPicture () {
      this.$http({
        method: 'PUT',
        url: this.profilePictureData.signedUrl,
        body: this.profilePictureData.file,
        headers: {
          'Content-Type': this.profilePictureData.file.type
        }
      }).then(response => {
        console.log(response)
        this.newProfilePicture()
      }).catch(err => {
        console.log(err)
      })
    },
    clearImage () {
      // todo implement
    },
    newFileFromInput (inputFile) {
      const files = inputFile.target.files || inputFile.dataTransfer.files
      console.log(files[0])
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
    sendInterests (type) {
      let checkedItems = []
      for (let i = 0; i < this[`${type}`].length; i++) {
        if (this[`${type}`][i].checked) {
          checkedItems.push(this[`${type}`][i]['genre'])
        }
      }
      this.$auth.post(`${this.$root.$options.hosts.rest}/new_message/`, {
        'userId': 2,
        'type': type,
        'key': checkedItems
      })
    },
    signOut: function () {
      this.logOut()
    },
    getPresignedUrl (fileName, contentType) {
      return this.$auth.post(`${this.$root.$options.hosts.rest}/generate_signed_url/`, {
        'key': fileName,
        'content-type': contentType,
        'client-method': 'put_object',
        'request-type': 'PUT'
      })
    },
    newProfilePicture () {
      this.$auth.post(`${this.$root.$options.hosts.rest}/new_profile_picture/`, {
        'file_name': this.profilePictureData.fileName
      })
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

.inputfile {
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
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
  padding: 1rem 50px;
  position: relative;
  transition: all 0.3s;
  vertical-align: middle;
}
</style>
