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
        <q-btn v-if="header.cta"
               class="within-iframe-hide"
               flat
               @click="header.cta.clickHandler"
               style="margin-right: 15px">
          <q-icon name="add" />
          {{header.cta.label}}
        </q-btn>
      </q-toolbar>
    </q-layout-header>

    <q-page-container>
      <router-view :setup-content="setupContent"></router-view>
    </q-page-container>
    <q-layout-footer>
      <q-tabs>
        <q-route-tab v-for="(item, index) in pages"
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
    },
    fillUserResource (callbackFn = null) {
      // Fetch User Info...
      this.$http.get(`${this.$root.$options.hosts.rest}/api/users/me/channels/`)
        .then(response => {
          this.$q.cookies.set('pusher_channel', response.data['channels'][0], {expires: 10})
          this.$root.$options.pusherConfig = response.data['channels'][0]
        }, response => {
          console.log(response, 'something failed.')
        })

      this.$http.get(`${this.$root.$options.hosts.rest}/api/users/me/`)
        .then(res => {
          let userData = res.body

          this.$root.$options.user = {
            'id': userData.pk,
            'firstName': userData.first_name,
            'lastName': userData.last_name,
            'email': userData.email,
            'userType': userData.user_type,
            'profilePic': userData.profile_pic_url
          }

          // todo check cookies' necessity
          this.$q.cookies.set('user_id', userData.id, {expires: 10})
          this.$q.cookies.set('email', userData.email, {expires: 10})
          this.$q.cookies.set('profile_pic', userData.profile_pic_url, {expires: 10})

          this.$root.$options.senior = {}

          if (userData.senior) {
            this.$root.$options.senior = {
              'id': userData.senior.id,
              'firstName': userData.senior.first_name,
              'lastName': userData.senior.last_name,
              'profilePic': userData.senior.profile_pic_url
            }
          }

          if (callbackFn) {
            callbackFn()
          }
        })
    }
  },
  beforeMount () {
    console.log('Main before mount fill user data')
    this.fillUserResource()
  },
  mounted () {
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
/*.main-content1*/
  /*width: 500px*/
  /*max-width: 90vw*/
/*.docs-btn .q-btn*/
  /*margin 5px*/
</style>
