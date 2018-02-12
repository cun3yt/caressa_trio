<template>
  <div class="main-content">

    <p class="caption">Today's Tasks</p>

    <div v-for="(todo, id) in todayList" class="todo-wrapper" :key="todo.id">
      <q-checkbox color="secondary"
                  :label="todo.label"
                  :value="!!todo.doneTime"
                  @input="toggle(id, $event)">
      </q-checkbox>
    </div>

    <p class="caption">Upcoming Tasks</p>

    <!--<slot name="header_cto">-->
      <!--<q-btn class="within-iframe-hide" flat @click="$router.replace('/showcase')" style="margin-right: 15px">-->
        <!--<q-icon name="add" />-->
        <!--New Task-->
      <!--</q-btn>-->
    <!--</slot>-->

  </div>
</template>

<script>
  import {
    QBtn,
    QCheckbox,
    QIcon,
    QSpinnerRadio
  } from 'quasar'

  export default {
    components: {
      QBtn,
      QCheckbox,
      QIcon,
      QSpinnerRadio
    },
    props: ['setupContent'],
    data () {
      return {
        zzz: false,
        todayList: [
          {
            id: '1',
            label: 'Blood Pressure Medicine',
            doneTime: null,
            assignedTo: null
          },
          {
            id: '2',
            label: 'Walking Exercise',
            doneTime: null,
            assignedTo: 'Caregiver Org.'
          }
        ],
        upcomingList: [
          {
            id: '1',
            label: 'Blood Pressure Medicine',
            time: 'Daily, A.M.'
          }
        ]
      }
    },
    methods: {
      toggle (id, checkValue) {
        if (!checkValue) {
          this.todayList[id].doneTime = null
          return
        }
        this.todayList[id].doneTime = (new Date()).toUTCString()
      }
    },
    created () {
      console.log('click handler is called')

      this.setupContent({
        title: 'Tasks',
        cta: {
          label: 'New Task',
          clickHandler () {
            console.log('cta is called...')
            this.router.replace('/showcase')
          }
        }
      })
    }
  }
</script>

<style lang="stylus" scoped>
  .todo-wrapper
    margin-bottom: 10px
</style>
