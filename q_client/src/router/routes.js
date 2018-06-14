console.log('routes.js is running...')

export default [
  {
    path: '/main',
    component: () => import('layouts/Main'),
    children: [
      {
        path: 'feed',
        component: () => import('pages/Feed'),
        name: 'feed'
      },
      {
        path: 'post',
        component: () => import('pages/Post'),
        name: 'post'
      },
      {
        path: 'chat',
        component: () => import('pages/Chat'),
        name: 'chat'
      },
      {
        path: 'health-numbers',
        component: () => import('pages/HealthNumbers'),
        name: 'health-numbers'
      },
      {
        path: 'settings',
        component: () => import('pages/Settings'),
        name: 'settings'
      },
      {
        path: '/',
        component: () => import('pages/index')
      },
      {
        path: '*',
        component: () => import('pages/404')
      }
    ]
  },

  {
    path: '*',
    component: () => import('pages/404')
  }
]
