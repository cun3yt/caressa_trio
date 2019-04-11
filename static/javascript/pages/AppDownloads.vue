<template>
    <div>
        <el-card>
            <el-row>
                <el-col :span="14">
                    <div style="font-size: 84px">
                        <span style="color: #2FCD8C; ">Care</span><span style="color: #83ddba;">ssa</span>
                    </div>
                    <div style="font-size: 24px; font-weight: 300">
                        <h4 style="color: #606266;">Reach your beloved from everywhere,</h4>
                        <h4 style="color: #606266; line-height: 20px">Download Caressa Now</h4>
                    </div>
                    <a href="https://www.caressa.ai" target="_blank">
                    <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/apple_store_download.svg"
                         alt="apple store download" width="%150" height="%150">
                    </a>
                </el-col>
                <el-col :span="10">
                    <img src="https://s3-us-west-1.amazonaws.com/caressa-prod/images/caressa_app_with_hand.png"
                         alt="caressa_app_in_iphone"
                         width="90%" height="90%">
                </el-col>
            </el-row>
        </el-card>
    </div>
</template>

<script>
    import Vue from 'vue';
    import { TimePicker } from 'element-ui';


    Vue.use(TimePicker);

    export default {
        name: "AppDownloads"
    }
</script>

<style scoped>

</style>
