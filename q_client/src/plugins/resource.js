import VueResource from 'vue-resource'
import vars from '../.env'
import {Cookies} from 'quasar'
import auth from '../router/auth'

export default ({ app, router, Vue }) => {
  Vue.use(VueResource)
  let accessToken = Cookies.get('access_token')
  Vue.http.interceptors.push((request, next) => {
    request.headers.set('Authorization', `Bearer ${accessToken}`)
    next(res => {
      if (res.status === 401) {
        return auth.refreshToken().then(_ => Vue.http(request))
      }
    })
  })

  app.hosts = {
    rest: vars.API_HOST
  }

  app.user = {
    id: Cookies.get('id'),
    email: Cookies.get('email'),
    profilePic: Cookies.get('profile_pic'),
    senior: {
      userId: null,
      profilePic: null
    }
  }
  app.pusherConfig = {
    channelName: Cookies.get('pusher_channel'), // todo need to handle if not exist in Cookie
    pusherKey: vars.PUSHER_KEY,
    pusherCluster: vars.PUSHER_CLUSTER
  }
}
