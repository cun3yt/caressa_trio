<template>
    <div>
        <div v-if="loading">
            <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
        </div>

        <div v-else>
            <a href="/accounts/facility">Residents List</a>

            <div>Welcome {{user.first_name}} {{user.last_name}}</div>

            <h1>Settings</h1>

            <h2>Check In Time</h2>

            <table>
                <tr>
                    <td><label for="morning-start-at">Morning Starts At: </label></td>
                    <td><el-time-select id="morning-start-at" v-model="morningStartAt" placeholder="Select time"
                                        :picker-options="{ start: '04:00', step: '00:15', end: '10:30' }" >
                        </el-time-select>
                    </td>
                </tr>
                <tr>
                    <td><label for="deadline">Check In Necessary Before: </label></td>
                    <td><el-time-select id="deadline" v-model="deadline" placeholder="Select time"
                                        :picker-options="{ start: '04:00', step: '00:15', end: '10:30' }" >
                        </el-time-select>
                    </td>
                </tr>
                <tr>
                    <td><label for="remind-at">Remind At: </label></td>
                    <td>
                        <el-time-select id="remind-at" v-model="remindAt" placeholder="Select time"
                                        :picker-options="{ start: '04:00', step: '00:15', end: '10:30' }" >
                        </el-time-select>
                    </td>
                </tr>
            </table>

            <el-row>
                <el-button type="primary" @click="onSave" :loading="isSaving">Save</el-button>
                <el-button @click="onCancel">Cancel</el-button>
            </el-row>
        </div>
    </div>
</template>

<script>
    import Vue from 'vue';
    import { TimePicker } from 'element-ui';

    Vue.use(TimePicker);

    export default {
        name: "Settings",
        components: { },
        props: {
            clientId: String,
            clientSecret: String,
            apiBase: String
        },
        data () {
            return {
                morningStartAt: null,
                deadline: null,
                remindAt: null,
                loading: true,
                seniorLivingFacilityId: null,
                isSaving: false,
            }
        },
        mounted: function () {
            this.auth.setup(this.clientId, this.clientSecret, this.apiBase)

            this.auth.requireLogin((userData) => {
                this.user = userData
                this.getSeniorLivingFacility(this.user.senior_living_facility).then(
                    (response) => {
                        this.morningStartAt = response.data.check_in_morning_start
                        this.deadline = response.data.check_in_deadline
                        this.remindAt = response.data.check_in_reminder
                        this.seniorLivingFacilityId = this.user.senior_living_facility
                        this.loading = false
                    },
                    (error) => { console.error(error) }
                )
            })
        },
        methods: {
            getSeniorLivingFacility (seniorLivingFacilityId) {
                return this.auth.http({
                    method: 'GET',
                    url: this.api_url(`api/senior_living_facilities/${seniorLivingFacilityId}/`),
                })
            },
            api_url (path) {     // todo move to a common place
                return `${this.apiBase}/${path}`
            },
            onSave () {
                console.log('onSave...', this.seniorLivingFacilityId)

                this.isSaving = true

                this.auth.http({
                    method: 'PATCH',
                    url: this.api_url(`api/senior_living_facilities/${this.seniorLivingFacilityId}/`),
                    body: {
                        'check_in_morning_start': this.morningStartAt,
                        'check_in_deadline': this.deadline,
                        'check_in_reminder': this.remindAt,
                    }
                }).then(
                    (response) => {
                        console.log('success', response)
                        this.$message({
                            message: 'Successfully saved',
                            type: 'success',
                        })
                        this.isSaving = false
                    },
                    (error) => {
                        console.error(error)
                        this.$message.error('An error happened! Please Try again later.');
                        this.isSaving = false
                    }
                )
            },
            onCancel () {
                this.$message("Cancelled, redirecting.")
                setTimeout(() => { window.location.href = "/accounts/facility" }, 1000)
            }
        }
    }
</script>

<style scoped>

</style>
