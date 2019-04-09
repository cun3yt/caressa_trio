<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <div>
        <div class="text-weight-light q-mb-md">
          Maggie is in wonder: What are you doing?
        </div>

        <div v-if="displayLogic.selectedPostItem >= 0" class="doc-container row">
          <q-scroll-area class="col-6 scroll-limits">
            <q-btn v-for="(postItem, itemIndex) in postItems"
                   v-if="!selectedCategories.includes(postItem.category)"
                   :key="itemIndex"
                   outline
                   class="full-width col-5 q-py-none q-px-sm"
                   align="left"
                   :color="displayLogic.selectedPostItem===itemIndex ? 'secondary' : 'primary'"
                   @click="displayLogic.selectedPostItem=itemIndex"
                   :icon="postItem.icon"
                   :label="`${postItem.label}...`"></q-btn>
          </q-scroll-area>

          <q-scroll-area class="col q-pr-sm q-pl-sm scroll-limits">
            <div v-if="postItems[displayLogic.selectedPostItem]"
                 v-for="(subItem, subItemIndex) in postItems[displayLogic.selectedPostItem].subItems"
                 :key="subItemIndex">
              <q-btn outline
                     class="full-width col-5 q-py-none q-px-sm row"
                     align="left"
                     color="primary"
                     no-ripple
                     @click="addSelectedItem(displayLogic.selectedPostItem,
                                             subItemIndex,
                                             postItems[displayLogic.selectedPostItem].category,
                                             postItems[displayLogic.selectedPostItem].label.toLowerCase(),
                                             subItem.name)">
                <img class="creative col-1 q-mr-sm q-my-none q-py-none"
                     :src="`/statics/creatives/${postItems[displayLogic.selectedPostItem].creativeDir}/${subItem.creative}`">
                <div class="col" align="left">
                  {{subItem.name}}
                </div>
              </q-btn>
            </div>
          </q-scroll-area>
        </div>

        <q-item-separator></q-item-separator>

        <div v-if="displayLogic.selectedItems.length > 0" class="row bg q-pa-xs full-width">
          <span>
            I'm
            <template v-for="(item, index) in displayLogic.selectedItems">
              <span v-if="index > 0 && index === (displayLogic.selectedItems.length - 1)" :key="index + '-span'"> and </span>
              <span v-else-if="index > 0" :key="index + '-span'">, </span>

              <q-chip :key="index" color="secondary" closable @hide="remove(index)" class="q-mb-xs">
                {{ postItems[item[0]]['label'].toLowerCase() }} {{ postItems[item[0]]['subItems'][item[1]]['name'] }}
              </q-chip>
            </template>
          </span>
        </div>
        <div class="row justify-end">
          <q-btn :loading="displayLogic.loaderForPosting"
                 class="col-2"
                 color="primary"
                 :disabled="displayLogic.selectedItems.length===0"
                 label="Post"
                 @click="post()"></q-btn>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
  import PostItems from 'components/PostCategories'
  export default {
    name: 'post',
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Post'
      })
    },
    computed: {
      selectedCategories () { // returns the selected category names
        return this.displayLogic.selectedItems.map(lst => lst[2])
      }
    },
    methods: {
      firstUnselectedCategory () {
        let itemsSelectedMapping = this.postItems.map(obj => this.selectedCategories.includes(obj.category))
        return itemsSelectedMapping.indexOf(false)
      },
      addSelectedItem (itemId, subItemId, category, verbLabel, target) {
        let obj = { // object to be sent to the API endpoint
          'verb': verbLabel,
          'target': target
        }
        this.displayLogic.selectedItems.push([itemId, subItemId, category, obj])
        this.displayLogic.selectedPostItem = this.firstUnselectedCategory()
      },
      remove (index) {
        this.displayLogic.selectedPostItem = this.displayLogic.selectedItems[index][0]
        this.displayLogic.selectedItems.splice(index, 1)
      },
      post () {
        let selections, vm
        this.displayLogic.loaderForPosting = true
        selections = this.displayLogic.selectedItems.map(item => item[3])
        vm = this
        this.showNotif()
        this.$auth.post(`${this.$root.$options.hosts.rest}/post/`, {
          'userId': this.$root.$options.user.id,
          'selections': selections
        }).then(response => {
          vm.displayLogic.loaderForPosting = false
          vm.$router.push('feed')
        }).then(response => {
          vm.displayLogic.loaderForPosting = false
          console.log('failure')
        })
      },
      showNotif () {
        this.$q.notify({
          color: 'secondary',
          message: 'You post is submitted.',
          position: 'top-right',
          icon: 'far fa-check-circle',
          detail: this.toString()
        })
      },
      toString () {
        if (this.displayLogic.selectedItems.length === 0) {
          return ''
        }
        let items = this.displayLogic.selectedItems.map(item => `${item[3].verb} ${item[3].target}`)
        let count = items.length
        return `I'm ${items.slice(0, count - 1).join(', ')} and ${items[count - 1]}.`
      }
    },
    data () {
      return {
        displayLogic: {
          selectedPostItem: 0,
          selectedItems: [],
          loaderForPosting: false
        },
        postItems: PostItems.postItems
      }
    }
  }
</script>

<style scoped lang="stylus">
  primary = red
  img.creative
    height: auto
    width: auto
    display:block
    max-height: 32px
    max-width: 32px
  .scroll-limits
    width: 300px
    height: 350px
</style>
