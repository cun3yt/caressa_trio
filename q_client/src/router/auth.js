import {Cookies} from 'quasar'
import vars from '../.env'
import Vue from 'vue'

export default {
  url: function (path) {
    return `${vars.API_HOST}${path}`
  },
  login: function (data) {
    let vm = this
    return Vue.http({
      method: 'POST',
      url: vm.url('/o/token/'),
      emulateJSON: true,
      body: {
        grant_type: 'password',
        username: data.username,
        password: data.password,
        client_id: vars.CLIENT_ID,
        client_secret: vars.CLIENT_SECRET
      }
    }).then(response => {
      console.log(response, 'login success')
      Cookies.set('access_token', response.data.access_token, {expires: 10})
      Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
      this.access_token = Cookies.get('access_token')
      this.refresh_token = Cookies.get('refresh_token')
    }, response => {
      console.log(response, 'login fail')
    })
  },
  isLoggedIn: function () {
    let accessToken = Cookies.get('access_token')
    return !!accessToken
  },
  refreshToken: function () {
    console.log('token refresh processing')
    let refreshToken = Cookies.get('refresh_token')
    let vm = this
    if (refreshToken) {
      let promise = Vue.http({
        method: 'POST',
        url: vm.url('/o/token/'),
        emulateJSON: true,
        body: {
          grant_type: 'refresh_token',
          refresh_token: Cookies.get('refresh_token'),
          client_id: vars.CLIENT_ID,
          client_secret: vars.CLIENT_SECRET
        }
      }).then(response => {
        console.log(response, 'refresh success')
        Cookies.set('access_token', response.data.access_token, {expires: 10})
        Cookies.set('refresh_token', response.data.refresh_token, {expires: 100})
        this.access_token = Cookies.get('access_token')
        this.refresh_token = Cookies.get('refresh_token')
        return true
      }, response => {
        console.log(response, 'refresh error')
        Cookies.remove('access_token')
        Cookies.remove('access_token')
        this.access_token = Cookies.get('access_token')
        this.refresh_token = Cookies.get('refresh_token')
        return false
      })
      return new Promise((resolve, reject) => {
        if (promise) {
          return resolve
        } else {
          return reject
        }
      })
    }
    console.log('no refresh token found!')
  },
  logOut (cb) {
    Cookies.remove('access_token')
    if (cb) cb()
    this.onChange(false)
  },
  onChange () {}
}
