import VueResource from 'vue-resource'

export default ({ app, router, Vue }) => {
  Vue.use(VueResource)

  app.hosts = {
    rest: 'http://127.0.0.1:9900' // todo this line needed change when debugging in ios build
  }

  app.user = { // todo these items need to go to `hard-coding`
    id: 2,
    profilePic: '/statics/man-avatar.png',
    circleCenter: {
      profilePic: '/statics/grandma-avatar.png'
    }
  }
}
