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
        Today & Upcoming
        <span slot="subtitle">Tasks</span>
      </q-toolbar-title>

      <q-btn v-if="newCTA"
             class="within-iframe-hide"
             flat
             @click="newCTA.clickHandler"
             style="margin-right: 15px">
        <q-icon name="add" />
        {{newCTA.label}}
      </q-btn>

    </q-toolbar>

    <div class="layout-padding docs-btn row justify-center">
      <router-view :new-cta-url="setNewCTA" />
    </div>

    <q-tabs slot="footer" v-if="!layoutStore.hideTabs" style="text-align:center;">
      <q-route-tab slot="title" icon="date_range" :to="{ name: 'today' }" replace label="Tasks" />
      <q-route-tab slot="title" icon="people" :to="{ name: 'care-circle' }" replace label="Circle" />
      <q-route-tab slot="title" icon="show_chart" :to="{ name: 'health-numbers' }" replace label="Health" />
      <q-route-tab slot="title" icon="settings" :to="{ name: 'settings' }" replace label="Settings" />
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
        newCTA: null,
        layoutStore
      }
    },
    methods: {
      setNewCTA (newCTA) {
        this.newCTA = newCTA
      }
    },
    watch: {
      '$route' (to, from) {
        this.newCTA = null
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
