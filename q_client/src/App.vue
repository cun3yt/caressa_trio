<template>
  <div id="q-app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  beforeMount () {
    // Fetch User Info...
    this.fillUserResource()
  },
  methods: {
    fillUserResource (callbackFn = null) {
      // Fetch User Info...
      this.$auth.get(`${this.$root.$options.hosts.rest}/api/users/me/channels/`)
        .then(response => {
          this.$q.cookies.set('pusher_channel', response.data['channels'][0], {expires: 10})
          this.$root.$options.pusherConfig = response.data['channels'][0]
        }, response => {
          console.log(response, 'something failed.')
        })

      this.$auth.get(`${this.$root.$options.hosts.rest}/api/users/me/`)
        .then(res => {
          let userData = res.body
          this.$root.$options.user = {
            'id': userData.id,
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
  }
}
</script>

<style>
</style>
