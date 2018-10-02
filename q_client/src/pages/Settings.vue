<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <q-list>
        <q-list-header>General</q-list-header>
        <q-item>
          <q-item-side>
            <q-item-tile icon="person outline" color="primary" />
          </q-item-side>
          <q-item-main>
            <q-item-tile label>Edit Profile</q-item-tile>
            <q-item-tile sublabel>Change your circle profile</q-item-tile>
          </q-item-main>
          <q-item-side>
            <q-btn
              color="primary"
              size="sm"
              icon="create"
            />
          </q-item-side>
        </q-item>
        <q-item>
          <q-item-side>
            <q-item-tile icon="help outline" color="primary" />
          </q-item-side>
          <q-item-main>
            <q-item-tile label>Help</q-item-tile>
            <q-item-tile sublabel>Ask us anything</q-item-tile>
          </q-item-main>
          <q-item-side>
            <q-btn
              color="primary"
              size="sm"
              icon="dialpad"
            />
          </q-item-side>
        </q-item>
        <q-collapsible highlight>
          <template slot="header">
            <q-item-side icon="feedback" color="primary" small>
            </q-item-side>
            <q-item-main label="Submit Feedback" />
          </template>
            <textarea placeholder="What went wrong?" class="full-width no-border"></textarea>
        </q-collapsible>
      </q-list><div class="q-pa-sm"></div>
      <q-list>
        <q-list-header>
         <q-item-main label="Personalize"></q-item-main>
        </q-list-header>
        <q-collapsible icon="library_music" label="Music Genres">
          <q-list-header >What {{user}} would love to listen?</q-list-header>
          <q-list>
            <q-item v-for="(item, index) in genres" :key="index" tag="label">
              <q-item-side>
                <q-checkbox v-model="genres[index].checked" />
              </q-item-side>
              <q-item-main>
                <q-item-tile title>{{genres[index].genre}}</q-item-tile>
              </q-item-main>
            </q-item>
            <q-item>
                <q-item-main>
                <q-btn @click="sendInterests('genres')" label="Apply" color="primary" size="0.9rem" icon="done_outline"/>
              </q-item-main>
              </q-item>
      </q-list>
          </q-collapsible>
      </q-list>
      <div class="q-pa-sm"></div>
      <q-list>
        <q-list-header>
         <q-item-main label="Circle Control"></q-item-main>
        </q-list-header>
            <q-list highlight>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="email" color="primary"/>
                </q-item-side>
                <q-item-main>
                  <q-input value="" type="email" stack-label="New Member Mail" />
                </q-item-main>
              </q-item>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="style" color="primary" />
                </q-item-side>
                <q-item-main>
                <q-btn-dropdown
                  color="secondary"
                  label="Pick Role"
                >
                  <q-list link>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="supervisor account" inverted color="secondary" />
                      <q-item-main>
                        <q-item-tile label>Family Member</q-item-tile>
                      </q-item-main>
                    </q-item>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="person outline" inverted color="secondary" />
                      <q-item-main>
                        <q-item-tile label>Caregiver</q-item-tile>
                      </q-item-main>
                    </q-item>
                    <q-item @click.native="handlerFunction">
                      <q-item-side icon="business" inverted color="secondary" />
                      <q-item-main>
                        <q-item-tile label>Caregiver Org.</q-item-tile>
                      </q-item-main>
                    </q-item>
                  </q-list>
                </q-btn-dropdown>
                  </q-item-main>
              </q-item>
              <q-item>
                <q-item-main>
                <q-btn
                  label="Add"
                  color="primary"
                  size="sm"
                  icon="add"
                />
              </q-item-main>
              </q-item>
            </q-list>
        <q-collapsible icon="supervised_user_circle" label="Circle Members">
            <q-list highlight inset-separator>
              <q-item>
                <q-item-side>
                  <q-item-tile icon="person" color="primary" />
                </q-item-side>
                <q-item-main
                  label="Marie D."
                  label-lines="1"
                  sublabel="Caretaker"
                  sublabel-lines="1"
                />
                <q-btn
                  color="primary"
                  size="sm"
                  icon="create"
                />
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
                <q-btn
                  color="primary"
                  size="sm"
                  icon="create"
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
                <q-btn
                  color="primary"
                  size="sm"
                  icon="create"
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
                <q-btn
                  color="primary"
                  size="sm"
                  icon="create"
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
                <q-btn
                  color="primary"
                  size="sm"
                  icon="create"
                />
              </q-item>
            </q-list>
          </q-collapsible>
      </q-list>
      <div class="q-pa-sm"></div>
      <q-list highlight>
        <q-list-header>Caressa</q-list-header>
        <q-item>
          <q-item-main>
            <q-item-tile label>About</q-item-tile>
            <q-item-tile sublabel>About Caressa</q-item-tile>
          </q-item-main>
        </q-item>
        <q-item>
          <q-item-main>
            <q-item-tile label>Version</q-item-tile>
            <q-item-tile sublabel>0.1.1</q-item-tile>
          </q-item-main>
        </q-item>
        <q-item>
          <q-item-main>
            <q-item-tile label>Reach Us</q-item-tile>
            <q-item-tile sublabel>info@caressa.ai</q-item-tile>
          </q-item-main>
        </q-item>
        <q-collapsible highlight>
          <template slot="header">
            <q-item-main label="Legal" />
          </template>
          <q-item @click.native="newPage('tos-v1')" >
            <q-item-main>
              <q-item-tile label>Terms of Service</q-item-tile>
            </q-item-main>
          </q-item>
          <q-item @click.native="newPage('open-source')" >
            <q-item-main>
              <q-item-tile label>Open Source Libraries</q-item-tile>
            </q-item-main>
          </q-item>
          <q-item @click.native="newPage('data-policy')" >
            <q-item-main>
              <q-item-tile label>Data Policy</q-item-tile>
            </q-item-main>
          </q-item>
        </q-collapsible>
      </q-list>
        <q-item>
          <q-btn style="background:white; color:red" class="full-width" label="Sign Out Caressa" />
        </q-item>
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'settings',
  props: ['setupContent'],
  created () {
    this.setupContent({
      title: this.user
    })
  },
  data () {
    return {
      user: 'Maggy',
      genres: [
        {
          'genre': 'Classical',
          'checked': false
        },
        {
          'genre': 'Jazz',
          'checked': false
        },
        {
          'genre': 'Blues',
          'checked': false
        },
        {
          'genre': 'Pop',
          'checked': false
        },
        {
          'genre': 'R&B',
          'checked': false
        }
      ],
      checked_one: true,
      checked_two: false,
      checked_three: false,
      option: 'opt1',
      select: 'fb',
      multipleSelect: ['goog', 'twtr'],
      selectOptions: [
        {
          label: 'Google',
          value: 'goog'
        },
        {
          label: 'Facebook',
          value: 'fb'
        },
        {
          label: 'Twitter',
          value: 'twtr'
        },
        {
          label: 'Apple Inc.',
          value: 'appl'
        },
        {
          label: 'Oracle',
          value: 'ora'
        }
      ],
      range: 20,
      doubleRange: {
        min: 10,
        max: 35
      }
    }
  },
  methods: {
    newPage (link) {
      const baseUrl = 'https://www.caressa.ai/'
      window.open(baseUrl + link)
    },
    sendInterests (type) {
      let checkedItems = []
      for (let i = 0; i < this[`${type}`].length; i++) {
        if (this[`${type}`][i].checked) {
          checkedItems.push(this[`${type}`][i]['genre'])
        }
      }(this.$http.post(`${this.$root.$options.hosts.rest}/personalize/`, {
        'type': type,
        'list': checkedItems
      }))
    }
  }
}
</script>

<style lang="stylus">
.main-content {
  width: 500px;
  max-width: 90vw;
}
</style>
