console.log('routes.js is running...')
import Main from '../layouts/Main'
import Admin from '../pages/Admin'
import Feed from '../pages/Feed'
import Chat from '../pages/Chat'
import Settings from '../pages/Settings'
import Index from '../pages/index'
import PageNotFound from '../pages/404'

export default [
  {
    path: '/',
    // component: () => import('layouts/Main'),
    component: Main,
    children: [
      {
        path: 'admin',
        // component: () => import('pages/Feed'),
        component: Admin,
        name: 'admin'
      },
      {
        path: 'feed',
        component: Feed,
        name: 'feed'
      },
      {
        path: 'chat',
        // component: () => import('pages/Chat'),
        component: Chat,
        name: 'chat'
      },
      {
        path: 'settings',
        // component: () => import('pages/Settings'),
        component: Settings,
        name: 'settings'
      },
      {
        path: '/',
        // component: () => import('pages/index')
        component: Index
      },
      {
        path: '*',
        // component: () => import('pages/404')
        component: PageNotFound
      }
    ]
  },

  {
    path: '*',
    // component: () => import('pages/404')
    component: PageNotFound
  }
]
