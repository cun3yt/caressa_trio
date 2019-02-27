<template>
    <div>
        <a href="/accounts/facility">Residents List</a>

        <h1>Settings</h1>

        <h2>Check In Time</h2>

        <div v-if="loading">
            <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/site/loader.gif">
        </div>

        <table v-else>
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
    </div>
</template>

<script>
    import Vue from 'vue';
    import { TimePicker } from 'element-ui';

    Vue.use(TimePicker);

    export default {
        name: "Settings",
        data () {
            return {
                remindAt: null,
                deadline: null,
                loading: true,
            }
        },

    }
</script>

<style scoped>

</style>
