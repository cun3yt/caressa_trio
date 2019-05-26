import Main from '../layouts/Main'

export default [
  {
    path: '/',
    component: Main,
    children: [
      {
        path: '/',
        component: () => import('../pages/Feed'),
        name: 'feed'
      },
      {
        path: 'chat',
        component: () => import('../pages/Chat'),
        name: 'chat'
      },
      {
        path: 'settings',
        component: () => import('../pages/Settings'),
        name: 'settings'
      },
      {
        path: 'contact',
        component: () => import('../pages/Contact'),
        name: 'contact'
      },
      {
        path: 'shop',
        component: () => import('../pages/Shop'),
        name: 'shop'
      },
      {
        path: '*',
        component: () => import('../pages/404')
      }
    ]
  },

  {
    path: '*',
    component: () => import('../pages/404')
  }
]
