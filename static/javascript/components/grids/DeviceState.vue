<template>
    <div>
        <div v-if="device==null">No Device</div>

        <div v-else>
            <div v-if="device.status" class="online">
                <i class="fas fa-circle"></i>
                Online
            </div>
            <div v-else class="offline">
                <i class="fas fa-circle"></i>
                Offline
            </div>

            <div class="check-in-status" v-bind:class="{ 'not-checked-in' : !device.isTodayCheckedIn }">
                Is Today Checked In: {{device.isTodayCheckedIn ? 'Yes' : 'No'}}
            </div>

            <div v-if="!device.isTodayCheckedIn" class="last-check-in">
                Last Check In: {{device.lastCheckInTime}}
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment-timezone'

    moment.tz.setDefault('America/Los_Angeles')

    export default {
        name: "DeviceState",
        props: {
            content: Array
        },
        data () {
            return {
                device: null,
            }
        },
        mounted() {
            if(this.content[0] == null) {
                this.device = null
                return
            }

            this.device = {
                status: this.content[0].is_online,
                lastCheckInTime: this.content[0].last_activity_time,
                isTodayCheckedIn: this.content[0].is_today_checked_in
            }

            if (this.device.lastCheckInTime) {
                this.device.lastCheckInTime = moment(this.device.lastCheckInTime).fromNow()
            }
        },
        computed: {

        }
    }
</script>

<style scoped>
    .online {
        color: seagreen;
    }
    .offline {
        color: indianred;
    }
    .last-check-in {
        font-size: 12px;
    }
    .check-in-status {
        font-size: 12px;
    }
    .not-checked-in {
        padding: 5px;
        background-color: darkred;
        color: white;
    }
</style>
