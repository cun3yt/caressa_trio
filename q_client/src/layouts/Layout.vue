<template>
  <q-layout
    ref="layout"
    :view="layoutStore.view"
    :left-breakpoint="layoutStore.leftBreakpoint"
    :right-breakpoint="layoutStore.rightBreakpoint"
    :reveal="layoutStore.reveal"
    class="non-selectable scroll">

    <q-toolbar slot="header">
        <q-toolbar-title>
          {{header.title}}

          <span slot="subtitle">{{header.subtitle}}</span>
        </q-toolbar-title>

      <q-btn v-if="header.cta"
             class="within-iframe-hide"
             flat
             @click="header.cta.clickHandler"
             style="margin-right: 15px">
        <q-icon name="add" />
        {{header.cta.label}}
      </q-btn>

    </q-toolbar>

    <div class="layout-padding docs-btn row justify-center">
      <router-view :setup-content="setupContent" />
    </div>

    <q-tabs slot="footer" v-if="!layoutStore.hideTabs" style="text-align:center;">
      <q-route-tab slot="title" icon="fas fa-calendar-alt" :to="{ name: 'feed' }" replace label="Feed" />
      <q-route-tab slot="title" icon="fas fa-chart-line" :to="{ name: 'health-numbers' }" replace label="Status" />
      <q-route-tab slot="title" icon="fas fa-plus-square" :to="{ name: 'post' }" replace label="Post" />
      <q-route-tab slot="title" icon="fas fa-comments" :to="{ name: 'chat' }" replace label="Chat" />
      <q-route-tab slot="title" icon="fas fa-cog" :to="{ name: 'settings' }" replace label="Settings" />
      <q-route-tab slot="title" icon="fas fa-hand-holding-heart" :to="{ name: 'contact' }" replace label="Contact" />
      <!--<q-route-tab slot="title" icon="date_range" :to="{ name: 'today' }" replace label="Tasks" />-->
      <!--<q-route-tab slot="title" icon="people" :to="{ name: 'care-circle' }" replace label="Circle" />-->
    </q-tabs>

  </q-layout>
</template>

<script>
import {
  QBtn,
  QIcon,
  QLayout,
  QTabs,
  QToolbar,
  QToolbarTitle,
  QRouteTab
} from 'quasar'

export const layoutStore = {
  view: 'lHr lpr fFr',
  reveal: false,
  leftScroll: true,
  rightScroll: true,
  leftBreakpoint: 996,
  rightBreakpoint: 1200,
  hideTabs: false
}

export default {
  components: {
    QBtn,
    QIcon,
    QLayout,
    QTabs,
    QToolbar,
    QToolbarTitle,
    QRouteTab
  },
  data () {
    return {
      layoutStore,
      header: {
        cta: null,
        title: '',
        subtitle: ''
      }
    }
  },
  methods: {
    setupContent ({cta = null, title = '', subtitle = ''} = {}) {
      this.header.cta = cta
      this.header.title = title
      this.header.subtitle = subtitle
    }
  },
  watch: {
    '$route' (to, from) {
      this.setupContent()
      }
    },
    name: 'layout'
  }
</script>

<style lang="stylus">
  .q-toolbar-title
    text-align: center
  .q-tabs-scroller
    margin: 0 auto
  .main-content
    width: 500px
    max-width: 90vw
  .docs-btn .q-btn
    margin 5px
</style>
