import Main from '../layouts/Main'
import Feed from '../pages/Feed'
import Chat from '../pages/Chat'
import Settings from '../pages/Settings'
import Contact from '../pages/Contact'
import PageNotFound from '../pages/404'

export default [
  {
    path: '/',
    component: Main,
    children: [
      {
        path: '/',
        component: Feed,
        name: 'feed'
      },
      {
        path: 'chat',
        component: Chat,
        name: 'chat'
      },
      {
        path: 'settings',
        component: Settings,
        name: 'settings'
      },
      {
        path: 'contact',
        component: Contact,
        name: 'contact'
      },
      {
        path: '*',
        component: PageNotFound
      }
    ]
  },

  {
    path: '*',
    component: PageNotFound
  }
]
