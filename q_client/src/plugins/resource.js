import VueResource from 'vue-resource'
import vars from '../.env'

export default ({ app, router, Vue }) => {
  Vue.use(VueResource)

  app.hosts = {
    rest: vars.API_HOST // todo this line needed change when debugging in ios build
  }

  app.user = { // todo these items need to go to `hard-coding`
    id: 2,
    profilePic: '/statics/man-avatar.png',
    circleCenter: {
      profilePic: '/statics/grandma-avatar.png'
    }
  }
  app.pusherConfig = {
    channelName: vars.PUSHER_CHANNEL,
    pusherKey: vars.PUSHER_KEY,
    pusherCluster: vars.PUSHER_CLUSTER
  }
}
