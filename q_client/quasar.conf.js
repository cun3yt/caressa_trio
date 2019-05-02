// Configuration for your app

module.exports = function (ctx) {
  return {
    // app plugins (/src/plugins)
    plugins: [
      'resource',
      'auth',
      'vuelidate',
    ],
    css: [
      'app.styl'
    ],
    extras: [
      ctx.theme.mat ? 'roboto-font' : null,
      'fontawesome'
    ],
    supportIE: false,
    build: {
      scopeHoisting: true,
      vueRouterMode: 'history', // 'hash',
      // vueCompiler: true,
      // gzip: true,
      // analyze: true,
      // extractCSS: false,
      extendWebpack (cfg) {
        cfg.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules|quasar)/
        })
      }
    },
    devServer: {
      // https: true,
      // port: 8080,
      open: true // opens browser window automatically
    },
    frameworkDev: 'all', // --- includes everything; for dev only!
    framework: {  // todo activate this for production
      components: [
        'QCard',
        'QCardTitle',
        'QCardMain',
        'QCardSeparator',
        'QLayout',
        'QLayoutHeader',
        'QLayoutFooter',
        'QLayoutDrawer',
        'QModal',
        'QPageContainer',
        'QPage',
        'QToolbar',
        'QToolbarTitle',
        'QBtn',
        'QIcon',
        'QList',
        'QListHeader',
        'QItem',
        'QItemMain',
        'QItemSeparator',
        'QItemSide',
        'QTabs',
        'QRouteTab',
        'QItemTile',
        'QCheckbox',
        'QRadio',
        'QToggle',
        'QRange',
        'QSelect',
        'QPageSticky',
        'QChatMessage',
        'QInput',
        'QSpinnerDots',
        'QSpinnerBars',
        'QSlider',
        'QCardActions',
        'QChip',
        'QScrollArea',
        'QBtnGroup',
        'QBtnDropdown',
        'QVideo',
        'QCollapsible',
        'QPopover',
        'QUploader',
      ],
      directives: [
        'Ripple',
        'CloseOverlay'
      ],
      // Quasar plugins
      plugins: [
        'Cookies',
        'Notify'
      ],
      iconSet: 'fontawesome'
      // i18n: 'de' // Quasar language
    },
    // animations: 'all' --- includes all animations
    animations: [
    ],
    cordova: {
      // id: 'org.cordova.quasar.app'
    }
  }
}
