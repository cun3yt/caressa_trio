<template>
  <div class="main-content">

    <q-list :highlight="todayList.length > 0">
      <q-list-header class="primary">Today's Tasks</q-list-header>

      <q-item v-if="todayList.length === 0">
        <q-item-side></q-item-side>
        <q-item-main>
          <q-item-tile label>Nothing for today</q-item-tile>
          <q-item-tile sublabel>Hint: Use "New Task" button at the top right to add a task</q-item-tile>
        </q-item-main>
      </q-item>

      <q-item v-for="(todo, id) in todayList" tag="label" :key="todo.id">
        <q-item-side>
          <q-checkbox color="secondary"
                      :value="!!todo.done_time"
                      @input="toggle(id, todo.id, $event)" />
        </q-item-side>
        <q-item-main>
          <q-item-tile label>{{ todo.title }}</q-item-tile>
          <q-item-tile v-if="!!todo.details" sublabel>{{ todo.details }}</q-item-tile>
          <q-item-tile v-if="!!todo.assignedTo" sublabel>{{ todo.assignedTo }}</q-item-tile>
        </q-item-main>
      </q-item>
    </q-list>

    <q-list :highlight="todayList.length > 0">
      <q-list-header>Upcoming Tasks</q-list-header>

      <q-item v-if="upcomingList.length === 0">
        <q-item-side></q-item-side>
        <q-item-main>
          <q-item-tile label>Nothing upcoming</q-item-tile>
          <q-item-tile sublabel>Hint: Use "New Task" button at the top right to add a task</q-item-tile>
        </q-item-main>
      </q-item>

      <q-item v-for="(todo, id) in upcomingList" :key="todo.id">
        <q-item-side>
          <q-item-tile icon="label_outline" color="primary" />
        </q-item-side>
        <q-item-main>
          <q-item-tile label>{{ todo.title }}</q-item-tile>
          <q-item-tile sublabel>{{ todo.details }}</q-item-tile>
          <q-item-tile sublabel>{{ todo.time }}</q-item-tile>
        </q-item-main>
      </q-item>

    </q-list>

<!--<q-btn class="within-iframe-hide" flat @click="$router.replace('/showcase')" style="margin-right: 15px">-->
  <!--<q-icon name="add" />-->
  <!--New Task-->
<!--</q-btn>-->

  </div>
</template>

<script>
  import {
    QList,
    QListHeader,
    QItem,
    QItemSide,
    QItemMain,
    QItemTile,
    QBtn,
    QCheckbox,
    QIcon,
    QSpinnerRadio
  } from 'quasar'

  export default {
    components: {
      QList,
      QListHeader,
      QItem,
      QItemSide,
      QItemMain,
      QItemTile,
      QBtn,
      QCheckbox,
      QIcon,
      QSpinnerRadio
    },
    props: ['setupContent'],
    data () {
      return {
        todayList: [],
        upcomingList: [
          {
            id: '1',
            title: 'Grocery Shopping',
            time: 'Tomorrow, A.M.'
          },
          {
            id: '2',
            title: 'Blood Pressure Medicine',
            time: 'Daily, A.M.'
          }
        ]
      }
    },
    methods: {
      toggle (listId, resourceId, checkValue) {
        if (!checkValue) {
          this.$options.task_resource.patch({id: resourceId}, { done: false })
          this.todayList[listId].done_time = null
          return
        }
        this.$options.task_resource.patch({id: resourceId}, { done: true })
        this.todayList[listId].done_time = (new Date()).toUTCString()
      }
    },
    created () {
      const url = this.$root.$options.apiHost + '/tasks{/id}/'
      this.$options.task_resource = this.$resource(url,
        {}, {
          patch: { method: 'PATCH', url: url }
        })

      this.setupContent({
        title: 'Tasks',
        cta: {
          label: 'New Task',
          clickHandler () {
            this.router.replace('/showcase')
          }
        }
      })

      this.$http.get(this.$root.$options.apiHost + '/tasks/', {
        time: 'today'
      }).then(response => {
        this.todayList = response.data
      })
    }
  }
</script>

<style lang="stylus" scoped>
  .todo-wrapper
    margin-bottom: 10px
</style>
