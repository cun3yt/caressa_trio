<template>
    <div>
        <el-form ref="form" :model="form" label-width="120px" label-position="top">
            <el-form-item label="Email address">
                <el-input v-model="form.email"></el-input>
            </el-form-item>
            <el-form-item label="Password">
                <el-input v-model="form.password"></el-input>
            </el-form-item>
            <el-form-item label="Password Confirmation">
                <el-input v-model="form.passwordConfirmation"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="logProps">Sign Up</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
    import Vue from 'vue';
    import { TimePicker } from 'element-ui';


    Vue.use(TimePicker);

    export default {
        name: "Invitation",
        components: { },
        props: {
            invitationCode: String,
            prospect: String,
        },
        data () {
            return {
                csrfToken: null,
                form: {
                    email: null,
                    password: null,
                    passwordConfirmation: null,

                }
            }
        },
        methods: {
            logProps: function () {
                debugger
                console.log('Invitation Code: ', this.invitationCode)
                console.log('prospect: ', this.prospect)
                console.log('CSRF: ', this.csrfToken)
            },
            sendForm: function () {
                console.log(this.$http)

            }
        },
        mounted() {
            this.csrfToken = Cookies.get('csrftoken')
        }
    }
</script>

<style scoped>

</style>
