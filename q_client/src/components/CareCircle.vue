<template>
  <div class="main-content">
    <q-list highlight inset-separator>
      <q-item>
        <q-item-side>
          <q-item-tile icon="person" color="primary" />
        </q-item-side>
        <q-item-main
          label="Marie D."
          label-lines="1"
          sublabel="Caretaker"
          sublabel-lines="1" />
      </q-item>
      <q-item>
        <q-item-side>
          <q-item-tile icon="supervisor account" color="primary" />
        </q-item-side>
        <q-item-main
          label="Andrew D."
          label-lines="1"
          sublabel="Family"
          sublabel-lines="1"
        />
      </q-item>
      <q-item>
        <q-item-side>
          <q-item-tile icon="supervisor account" color="primary" />
        </q-item-side>
        <q-item-main
          label="Lisa W."
          label-lines="1"
          sublabel="Family"
          sublabel-lines="1"
        />
      </q-item>
      <q-item>
        <q-item-side>
          <q-item-tile icon="person outline" color="primary" />
        </q-item-side>
        <q-item-main
          label="Tracy S."
          label-lines="1"
          sublabel="Caregiver"
          sublabel-lines="1"
        />
      </q-item>
      <q-item>
        <q-item-side>
          <q-item-tile icon="business" color="primary" />
        </q-item-side>
        <q-item-main
          label="Longevity Corp."
          label-lines="1"
          sublabel="Caregiver Org."
          sublabel-lines="1"
        />
      </q-item>
    </q-list>
  </div>
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

  export default {
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Care Circle'
      })
    },
    components: {
      QBtn,
      QIcon,
      QLayout,
      QTabs,
      QToolbar,
      QToolbarTitle,
      QRouteTab
    }
  }
</script>
