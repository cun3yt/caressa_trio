<template>
  <q-layout
    ref="layout"
    view="lHr lpr fFr"
    class="non-selectable scroll">

    <q-layout-header>
      <q-toolbar>
        <q-toolbar-title>
          {{header.title}}
        </q-toolbar-title>
        <q-btn v-if="header.cta" class="within-iframe-hide" flat @click="header.cta.clickHandler" style="margin-right: 15px">
          <q-icon name="add" />
          {{header.cta.label}}
        </q-btn>
      </q-toolbar>
    </q-layout-header>

    <q-page-container>
      <router-view :setup-content="setupContent" :log-out="logOut"></router-view>

      <q-modal v-model="signUpModal" maximized>
      <div style="padding: 2.5em; margin-top: 1.5em">
        <div class="q-display-3">
          <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
        </div>
        <div style="padding-top: 3em">
          <p class="q-display-1 text-weight-thin">Welcome,</p>
          <p class="q-display-1 text-weight-thin">Lets get started.</p>
          <div>
            <q-input v-model="signUpEmail" type="email" float-label="e-mail" color="#2FCD8C" />
            <q-input v-model="signUpPassword" type="password" float-label="password" color="#2FCD8C" />
          </div>
        </div>
      <q-btn class="navigation" @click="signUpModal = !signUpModal; noSeniorModal = !noSeniorModal" label="SIGN UP" />
     </div>
      <div style="padding: 2.5em; margin-top: 1.5em">
        <p @click="loginRedirect('signUpModal')" class="q-title text-weight-light">
          <span class="secondary-link">Have an account</span>?
        </p>
        <div @click="videoDirection('signUpModal')" class="q-title text-weight-light">
          What is <span style="color:#2FCD8C; text-decoration: underline">Caressa</span>?
        </div>
      </div>
    </q-modal>

    <q-modal v-model="loginModal" maximized>
      <div style="padding: 2.5em; margin-top: 1.5em">
        <div class="q-display-3">
          <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
        </div>
        <div style="padding-top: 3em">
          <p class="q-display-1 text-weight-thin">Welcome,</p>
          <p class="q-display-1 text-weight-thin">Enter Credentials</p>
          <div>
            <q-input v-model="loginEmail" type="email" float-label="e-mail" color="#2FCD8C" />
            <q-input v-model="loginPassword" type="password" float-label="password" color="#2FCD8C" />
          </div>
        </div>
        <q-btn class="navigation" @click=submitLogin() label="LOGIN" />
      </div>
      <div style="padding: 2.5em; margin-top: 1.5em">
        <p @click="signUpRedirect('loginModal')" class="q-title text-weight-light">
          <span style="text-decoration: underline">Sign Up</span>
        </p>
        <div @click="videoDirection('signUpModal')" class="q-title text-weight-light">
          What is <span style="color:#2FCD8C; text-decoration: underline">Caressa</span>?
        </div>
      </div>
    </q-modal>

    <q-modal v-model="noSeniorModal" maximized>
      <div style="padding: 1.5em 2.5em; margin-top: 1.5em">
        <div class="q-display-3">
          <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
        </div>
        <div style="padding-top: 3em">
          <p class="q-display-2 text-weight-thin">Oops!</p>
          <p class="q-display-1 text-weight-light">Nobody is in your list.</p>
      </div>
      <q-btn class="q-display-1 text-weight-light" style="color:#83ddba; padding: 0.2em; margin-top: 2em"
             @click="noSeniorModal = false; addSeniorModal = true" label="add your beloved elder" />
      </div>
      <div style="padding: 1.5em; margin-top: 1.5em">
        <div @click="videoDirection('noSeniorModal')" class="q-title text-weight-light">
          <p @click="loginRedirect('noSeniorModal')" class="q-title text-weight-light"><span style="text-decoration: underline">Login</span></p>
          What is <span style="color:#2FCD8C; text-decoration: underline">Caressa</span>?
        </div>
      </div>
    </q-modal>

    <q-modal v-model="videoModal" maximized>
      <div style="padding: 0.8em; margin-top: 5em">
        <div class="q-display-3">
          <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
        </div>
        <p class="q-title text-weight-thin">Connecting Seniors with their Family</p>
        <q-video
          src="https://www.youtube.com/embed/uilkmUoXoLU?rel=0&amp;showinfo=0"
          style="width: 22.2em; height: 18em"
        />
      <q-btn align="between" class="btn-fixed-width navigation go-back"
             @click="goBacktoPreviousModal" icon="fas fa-arrow-left" label="GO BACK" />
      </div>
    </q-modal>

    <q-modal v-model="addSeniorModal" maximized>
      <div style="padding: 2.5em; margin-top: 1.5em">
        <div class="q-display-3">
          <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
        </div>
        <div style="padding-top: 3em">
          <p class="q-display-1 text-weight-thin">Connect your beloved. &lt;3</p>
          <div>
          <q-input v-model="appPhoneNumber" type="number" float-label="Your Phone Number" color="#2FCD8C" style="color:#2FCD8C; margin-top: 1em" />
          <q-input v-model="seniorPhoneNumber" type="number" float-label="Elder Phone Number" color="#2FCD8C" style="color:#2FCD8C; margin-top: 1em"  />
          <q-input v-model="deviceCode" type="number" float-label="Number On Device" color="#2FCD8C" style="color:#2FCD8C; margin-top: 1em"  />
          </div>
        </div>

        <q-btn style="color:#2FCD8C; margin-top: 2em" @click="addSeniorModal = false; foundSeniorModal = true" icon="fas fa-user-plus" label="Add" />
      </div>

      <div style="padding: 2.5em; margin-top: 1.5em">
        <p @click="loginRedirect('addSeniorModal')" class="q-title text-weight-light"><span style="text-decoration: underline">Have an account</span>?</p>
        <div @click="videoDirection('signUpModal')" class="q-title text-weight-light">
          What is <span style="color:#2FCD8C; text-decoration: underline">Caressa</span>?
        </div>
      </div>
    </q-modal>

  <q-modal v-model="foundSeniorModal" maximized>
    <div style="padding: 2.5em; margin-top: 1.5em">
      <div class="q-display-3">
        <img class="logo" alt="Caressa logo" src="~assets/caressa-logo-full.png">
      </div>
      <div style="padding-top: 3em">
        <div>
          <q-icon size="5em" style="color:#2FCD8C" name="check_circle_outline" />
        </div>
        <p class="q-display-1 text-weight-thin" style="margin-top: 2em">Found Beloved &lt;3</p>
        <q-btn
        v-for="(senior, index) in seniors"
        :key="index"
        style="color:#2FCD8C; margin-top: 1em; padding:0 1em 0 1em"
        class="q-title"
        @click="foundSeniorModal = false"
        icon-right="arrow_forward_ios"
        :label="senior.name" />
        </div>
    </div>
    <div style="padding: 2.5em; margin-top: 1.5em">
      <p @click="loginRedirect('foundSeniorModal')" class="q-title text-weight-light">
        <span style="text-decoration: underline">Have an account</span>?
      </p>
      <div @click="videoDirection('signUpModal')" class="q-title text-weight-light">
        What is <span style="color:#2FCD8C; text-decoration: underline">Caressa</span>?
      </div>
    </div>
  </q-modal>

    </q-page-container>
    <q-layout-footer>
      <q-tabs>
        <q-route-tab :keep-alive="index"
                     v-for="(item, index) in pages"
                     :key="index"
                     slot="title"
                     :icon="item.icon"
                     :to="{name: item.name}"
                     replace
                     :label="item.label" />
      </q-tabs>
    </q-layout-footer>

  </q-layout>
</template>

<script>
import {bus} from '../plugins/auth.js'

export default {
  data () {
    return {
      signUpEmail: '',
      signUpPassword: '',
      loginEmail: '',
      loginPassword: '',
      loginModal: this.$auth.isLoggedOut(),
      signUpModal: false,
      noSeniorModal: false,
      videoModal: false,
      addSeniorModal: false,
      foundSeniorModal: false,
      seniorPhoneNumber: '',
      deviceCode: '',
      appPhoneNumber: '',
      lastPosition: '',
      types: [
        {
          label: 'Always Maximized',
          show: () => { this.maximizedModal = true }
        }
      ],
      header: {
        cta: null,
        title: '',
        subtitle: '..'
      },
      seniors: [], // not in use, can be used in future.
      user: {
        name: '',
        id: '',
        state: false
      },
      pages: [
        {
          name: 'feed',
          label: 'Feed',
          icon: 'far fa-newspaper'
        },
        {
          name: 'chat',
          label: 'Messages',
          icon: 'fas fa-comments'
        },
        {
          name: 'settings',
          label: 'Settings',
          icon: 'fas fa-cog'
        },
        {
          name: 'contact',
          label: 'Contact',
          icon: 'fas fa-hand-holding-heart' // todo find a better icon e.g. headset
        }
      ]
    }
  },
  methods: {
    setupContent ({cta = null, title = '', subtitle = ''} = {}) {
      this.header.cta = cta
      this.header.title = title
      this.header.subtitle = subtitle
    },
    signUpRedirect: function (currentModal) {
      this.signUpModal = true
      this[currentModal] = false
    },
    logOut: function () {
      this.$auth.tokenRevoke()
      this.loginModal = true
    },
    resetLoginForm: function () {
      this.loginEmail = 'john@caressa.ai' // todo change for production
      this.loginPassword = 'qwer1234'
    },
    submitLogin: function () {
      let data = {
        'username': this.loginEmail,
        'password': this.loginPassword
      }
      this.$auth.login(data).then(
        response => {
          console.log(response, 'success')
          this.resetLoginForm()
          this.loginModal = false
          bus.$emit('addFeeds')
        }, response => {
          console.log(response, 'error')
          this.loginModal = true
        })
    },
    loginSuccessRedirect: function () {
      let vm = this
      this.$root.fillUserResource(() => { vm.loginModal = false })
      this.$router.push('feed')
    },
    loginRedirect: function (currentModal = null) {
      this.loginModal = true
      if (this[currentModal]) {
        this[currentModal] = false
      }
    },
    videoDirection: function (calledFrom) {
      this.lastPosition = calledFrom
      this.videoModal = true
      this[`${calledFrom}`] = false
    },
    goBacktoPreviousModal: function () {
      this.videoModal = false
      const lastModal = this.lastPosition
      this[`${lastModal}`] = true
    }
  },
  mounted () {
    this.resetLoginForm()
    bus.$on('loginRedirect', this.loginRedirect)
    bus.$on('loginSuccessRedirect', this.loginSuccessRedirect)
  },
  watch: {
    '$route' (to, from) {
      this.setupContent()
    }
  },
  name: 'layout'
}
</script>

<style lang="stylus">
.q-toolbar-title
  text-align: center
.q-tabs-scroller
  margin: 0 auto
img.logo
  width: 200px
.secondary-link
  text-decoration: underline
.navigation
  color: #2FCD8C
  margin-top: 2em
.go-back
  padding: 1em
</style>
