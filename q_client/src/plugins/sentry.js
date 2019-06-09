import Vue from 'vue'
import * as Sentry from '@sentry/browser'
import * as Integrations from '@sentry/integrations'
import vars from '../.env'

Sentry.init({
  dsn: vars.SENTRY_DSN,
  integrations: [new Integrations.Vue({Vue, attachProps: true})]
})

// leave the export, even if you don't use it
export default ({ app, router, Vue }) => {
  // something to do
}
