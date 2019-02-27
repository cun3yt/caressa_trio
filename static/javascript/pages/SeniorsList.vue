<template>
    <div>
        <edit-modal v-if="modalOperationData.editModal.show" :errors="editErrors" :edit-submit="editSubmit"
                    @close="modalOperationData.editModal.show = false">
            <form slot="header">
                <h3>Senior Personal Information</h3>
                <div>
                    <label>First Name:</label>
                    <input name="first_name" v-model="editForm.first_name">
                </div>
                <div>
                    <label>Last Name:</label>
                    <input name="last_name" v-model="editForm.last_name">
                </div>
                <div>
                    <label>Room Number:</label>
                    <input name="room_no" v-model="editForm.room_no">
                </div>
                <hr>
                <div :class="{disabled : !modalOperationData.editModal.isContactEditable}">
                    <h3>Primary Contact <span v-if="!modalOperationData.editModal.isContactEditable">(Verified)</span></h3>
                    <div>
                        <label>Name:</label>
                        <input :disabled="!modalOperationData.editModal.isContactEditable"
                               v-model="editForm['contact.name']">
                    </div>
                    <div>
                        <label>Email:</label>
                        <input :disabled="!modalOperationData.editModal.isContactEditable"
                               v-model="editForm['contact.email']">
                    </div>
                    <div>
                        <label>Phone Number:</label>
                        <input :disabled="!modalOperationData.editModal.isContactEditable"
                               v-model="editForm['contact.phone_number']">
                    </div>
                </div>
            </form>
        </edit-modal>
        <div v-if="loading">
            <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
        </div>
        <div v-else>
            <fixed-header :user="user" :logout="logout"></fixed-header>
            <public-address-modal v-if="modalOperationData.publicAddressModal.show"
                                  @close="modalOperationData.publicAddressModal.show = false"
                                  :user="user"
                                  :access-token="this.accessToken"
                                  :api-base="apiBase">
            </public-address-modal>
            <div class="senior-list" id="seniors">

                <tabular-data :data="gridData" :columns="gridColumns"
                              :filter-key="searchQuery" :edit-entry="editEntry"
                              :delete-entry="deleteEntry" :on-submit="onSubmit"></tabular-data>
            </div>

            <div v-if="errors.length > 0" class="errors">
                <ul>
                    <li v-for="error in errors">{{error}}</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
    import Vue from 'vue'
    import TabularData from '../components/TabularData.vue'
    import EditModal from '../components/EditModal.vue'
    import FixedHeader from '../components/FixedHeader.vue'
    import PublicAddressModal from '../components/PublicAddressModal.vue'
    import bus from '../utils.communication.js'

    export default {
        name: "SeniorsList",
        components: {TabularData, EditModal, FixedHeader, PublicAddressModal},
        props: {
            clientId: String,
            clientSecret: String,
            apiBase: String
        },
        mounted: function () {
            this.accessToken = this.$cookies.get('access_token')
            this.refreshToken = this.$cookies.get('refresh_token')

            // todo: make this one as a function as `requireLogin()`
            if (!this.accessToken) {
                window.location.href = this.api_url('accounts/login/');
            }
            // Get User Detail
            let that = this
            let promise = this.getAdminData()
            promise.then(
                function(response){
                    this.user = response.data
                    this.list()
                    this.loading = false
                }, function(error) {
                    let pro = that.useRefreshToken()
                    pro.then(function(response) {
                        that.accessToken = response.body.access_token
                        that.refreshToken = response.body.refresh_token
                        that.$cookies.set('access_token', that.accessToken)
                        that.$cookies.set('refresh_token', that.refreshToken)

                        that.getAdminData().then(function (response) {
                            that.user = response.data
                            that.list()
                            that.loading = false
                        }, function (error) {
                            console.error('Unexpected error', error)
                        })
                    }, function(error) {
                        that.$cookies.remove('access_token')
                        that.$cookies.remove('refresh_token')
                        window.location.href = that.api_url('accounts/login/')
                    })
                })

            bus.$on('searchKey', (searchKey) => {
                this.searchQuery = searchKey
            })
            bus.$on('broadcast', this.newBroadcast)
        },
        data () {
            return {
                loading: true,
                formData: {},
                user: {},
                accessToken: '',
                refreshToken: '',
                searchQuery: '',
                gridColumns: [
                    {field: 'first_name', label: 'First Name', sortable: true},
                    {field: 'last_name', label: 'Last Name', sortable: true},
                    {field: 'room_no', label: 'Room Number', sortable: true},
                    {field: 'device_status', label: 'Device Status', sortable: false},
                    {field: 'primary_contact', label: 'Primary Contact', sortable: false},
                ],
                gridData: [],
                errors: [],
                modalOperationData: {
                    editModal:{
                        show: false,
                        pk: null,
                        isContactEditable: false
                    },
                    publicAddressModal:{
                        show: false,
                        channels: {}
                    }
                },
                editForm: {},
                editErrors: [],
            }
        },
        methods: {
            newBroadcast () {
                this.modalOperationData.publicAddressModal.show = true
            },
            api_url(path) {
                return `${this.apiBase}/${path}`
            },
            useRefreshToken: function() {
                return this.$http({
                    method: 'POST',
                    url: this.api_url('o/token/'),
                    emulateJSON: true,
                    body: {
                        grant_type:'refresh_token',
                        refresh_token: this.refreshToken,
                        client_id: this.clientId,
                        client_secret: this.clientSecret,
                    }
                })
            },
            getAdminData: function() {
                return this.$http.get(this.api_url('api/users/me/'), {
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    }
                })
            },
            list: function () {
                this.$http.get(this.api_url('api/seniors/'), {
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    }
                }).then(function (response) {
                    let rawData = response.data.results
                    let that = this

                    this.gridData = rawData.map(function (row) {
                        row.is_contact_editable = true  // if no contact (default case): contact editable

                        for (var col of that.gridColumns) {
                            if (col.field == 'device_status') {
                                if ( !row[col.field] ) {
                                    row[col.field] = [ null ]
                                    continue
                                }
                                row[col.field] = [ row[col.field].is_online ]
                                continue
                            }

                            if (col.field == 'primary_contact') {
                                if (!row[col.field]) {
                                    row[col.field] = ['']
                                    continue
                                }
                                let contact = row[col.field]
                                row[col.field] = [
                                    {
                                        key: 'name',
                                        label: 'Name',
                                        value: `${contact.first_name} ${contact.last_name}`
                                    },
                                    {
                                        key: 'email',
                                        label: 'Email',
                                        value: contact.email
                                    },
                                    {
                                        key: 'phone number',
                                        label: 'Phone Number',
                                        value: contact.phone_number
                                    }
                                ]
                                row.is_contact_editable = contact.is_temporary
                                continue
                            }

                            row[col.field] = [row[col.field]]
                        }
                        return row
                    })
                }, function (error) {
                    console.error(error)
                })
            },
            deleteEntry: function (pk) {
                let deletedEntryList = this.gridData.filter(function (data) {
                    return data.pk == pk
                })

                let confirmation = confirm(`Are you sure deleting '${deletedEntryList[0].first_name}'?`)
                if (!confirmation) {
                    return
                }

                this.gridData = this.gridData.filter(function (data) {
                    return data.pk != pk
                })

                let that = this
                this.$http({
                    method: 'DELETE',
                    url: this.api_url(`api/seniors/${pk}/`),
                    emulateJSON: true,
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    }
                }).then(function () {
                    console.log('successful deletion')
                }, function (error) {
                    alert(`Something went wrong! We cannot delete entry now: '${deletedEntryList[0].first_name}'`);
                    that.gridData = deletedEntryList.concat(that.gridData)
                })
            },
            editEntry: function (senior) {
                this.modalOperationData.editModal.show = true
                this.modalOperationData.editModal.pk = senior.pk
                this.modalOperationData.editModal.isContactEditable = senior.is_contact_editable

                let contact = {
                    name: (senior.primary_contact.length > 0 && senior.primary_contact[0].value) || '',
                    email: (senior.primary_contact.length > 1 && senior.primary_contact[1].value) || '',
                    phone_number: (senior.primary_contact.length > 2 && senior.primary_contact[2].value) || ''
                }

                this.editForm = {
                    first_name: senior.first_name[0],
                    last_name: senior.last_name[0],
                    room_no: senior.room_no[0]
                }
                this.editForm['contact.name'] = contact.name
                this.editForm['contact.email'] = contact.email
                this.editForm['contact.phone_number'] = contact.phone_number
            },
            logout: function () {
                this.$http({
                    method: 'POST',
                    url: this.api_url('o/revoke_token/'),
                    emulateJSON: true,
                    body: {
                        token: this.accessToken,
                        client_id: this.clientId,
                        client_secret: this.clientSecret
                    }
                })
                this.$cookies.remove('access_token')
                this.$cookies.remove('refresh_token')
                window.location.href = this.api_url('accounts/login/');
            },
            onSubmit: function () {
                this.$http({
                    method: 'POST',
                    url: this.api_url('api/seniors/'),
                    emulateHTTP: true,
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    },
                    body: this.formData
                }).then(function (response) {
                    bus.$emit('clearForm')
                    this.list()
                    this.errors = []
                }, function (error) {
                    this.errors = error.data.errors
                })
            },
            editSubmit: function (pk) {
                this.editErrors = []

                let that = this

                this.$http({
                    method: 'PUT',
                    url: this.api_url(`api/seniors/${this.modalOperationData.editModal.pk}/`),
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    },
                    body: this.editForm
                }).then(function(response){
                    that.modalOperationData.editModal.show = false
                    that.list()
                }, function(error) {
                    that.editErrors = error.data.errors
                })
            }
        },
    }
</script>

<style scoped>
    .errors {
        border: dashed indianred 4px;
    }
    .senior-list {
        margin-top: 8em;
    }
</style>
