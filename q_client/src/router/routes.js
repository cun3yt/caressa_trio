console.log('routes.js is running...')
import Main from '../layouts/Main'
import Feed from '../pages/Feed'
import Post from '../pages/Post'
import Chat from '../pages/Chat'
import HealthNumbers from '../pages/HealthNumbers'
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
        path: 'feed',
        // component: () => import('pages/Feed'),
        component: Feed,
        name: 'feed'
      },
      {
        path: 'post',
        // component: () => import('pages/Post'),
        component: Post,
        name: 'post'
      },
      {
        path: 'chat',
        // component: () => import('pages/Chat'),
        component: Chat,
        name: 'chat'
      },
      {
        path: 'health-numbers',
        // component: () => import('pages/HealthNumbers'),
        component: HealthNumbers,
        name: 'health-numbers'
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
