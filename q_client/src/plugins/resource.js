import VueResource from 'vue-resource'
import vars from '../.env'
import {Cookies} from 'quasar'

export default ({ app, router, Vue }) => {
  Vue.use(VueResource)

  app.hosts = {
    rest: vars.API_HOST // todo this line needed change when debugging in ios build
  }

  app.user = {
    id: Cookies.get('id'),
    email: Cookies.get('email'),
    profilePic: '/statics/man-avatar.png', // todo these items need to go to `hard-coding`
    circleCenter: {
      profilePic: '/statics/grandma-avatar.png' // todo these items need to go to `hard-coding`
    }
  }
  app.pusherConfig = {
    channelName: Cookies.get('pusher_channel'), // todo need to handle if not exist in Cookie
    pusherKey: vars.PUSHER_KEY,
    pusherCluster: vars.PUSHER_CLUSTER
  }
}
