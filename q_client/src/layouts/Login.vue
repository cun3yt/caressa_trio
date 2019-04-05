<template>
  <div>
    <h2>Login</h2>
    <p v-if="$route.query.redirect">
      You need to login first.
    </p>
    <form @submit.prevent="loginButton">
      <label><input v-model="email" placeholder="email"></label>
      <label><input v-model="pass" placeholder="password" type="password"></label> (hint: password1)<br>
      <button type="submit">login</button>
      <p v-if="error" class="error">Bad login information</p>
    </form>
  </div>
</template>

<script>
import auth from '../router/auth'
export default {
  data () {
    return {
      email: '',
      pass: '',
      error: false
    }
  },
  methods: {
    loginButton: function () {
      let data = {
        username: this.email,
        password: this.pass
      }
      let vm = this
      auth.login(data)
        .then(_ => {
          vm.$router.replace(vm.$route.query.redirect || '/')
        }, _ => {
          vm.error = true
        })
    }
  }
}
</script>

<style>
  .error {
    color: red;
  }
</style>
