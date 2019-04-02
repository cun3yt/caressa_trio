console.log('routes.js is running...')
// import Main from '../layouts/Main'
// import Feed from '../pages/Feed'
// import Chat from '../pages/Chat'
// import Settings from '../pages/Settings'
// import Contact from '../pages/Contact'
// import Index from '../pages/index'
// import PageNotFound from '../pages/404'
import auth from './auth.js'

function requireAuth (to, from, next) {
  if (!auth.isLoggedIn()) {
    console.log('auth required')
    next({
      path: '/login',
      query: { redirect: '/' }
    })
  } else {
    console.log('auth not required')
    next()
  }
}

export default [
  {
    path: '/login',
    component: () => import('layouts/Login')
  },
  {
    path: '/logout',
    beforeEnter (to, from, next) {
      auth.logOut()
      next('/')
    }
  },
  {
    path: '/',
    component: () => import('layouts/Main'),
    beforeEnter: requireAuth,
    children: [
      { path: 'feed', component: () => import('pages/Feed'), name: 'feed', beforeEnter: requireAuth },
      { path: 'chat', component: () => import('pages/Chat'), name: 'chat', beforeEnter: requireAuth }, // component: () => import('pages/Chat'),
      { path: 'settings', component: () => import('pages/Settings'), name: 'settings', beforeEnter: requireAuth }, // component: () => import('pages/Settings'),
      { path: 'contact', component: () => import('pages/Contact'), name: 'contact', beforeEnter: requireAuth },
      { path: '/', component: () => import('pages/Feed'), beforeEnter: requireAuth }, // component: () => import('pages/index')
      { path: '*', component: () => import('pages/404') }
    ]
  },

  {
    path: '*',
    component: () => import('pages/404')
  }
]
