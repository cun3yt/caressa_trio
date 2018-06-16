<template>
  <q-layout
    ref="layout"
    view="lHr lpr fFr"
    class="non-selectable scroll">

    <q-layout-header>
      <q-toolbar>
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
    </q-layout-header>

    <q-page-container>
      <router-view :setup-content="setupContent" />
    </q-page-container>

    <q-layout-footer>
      <q-tabs>
        <q-route-tab slot="title" icon="date_range" :to="{ name: 'feed' }" replace label="Feed" />
        <q-route-tab slot="title" icon="show_chart" :to="{ name: 'health-numbers' }" replace label="Status" />
        <q-route-tab slot="title" icon="add_box" :to="{ name: 'post' }" replace label="Post" />
        <q-route-tab slot="title" icon="forum" :to="{ name: 'chat' }" replace label="Chat" />
        <q-route-tab slot="title" icon="settings" :to="{ name: 'settings' }" replace label="Settings" />
      </q-tabs>
    </q-layout-footer>

  </q-layout>
</template>

<script>
export default {
  data () {
    return {
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
/*.main-content1*/
  /*width: 500px*/
  /*max-width: 90vw*/
/*.docs-btn .q-btn*/
  /*margin 5px*/
</style>
