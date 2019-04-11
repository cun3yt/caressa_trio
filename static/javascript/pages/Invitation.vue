<template>
    <div>
        <el-row>
            <el-col style="font-size: 42px" :span="12" :offset="6">
                <span style="color: #2FCD8C;">Care</span><span style="color: #83ddba;">ssa</span>
            </el-col>
            <el-col :span="12" :offset="6">
                <div style="color: #606266">
                    <h3>Welcome, {{name}}</h3>
                    <h4>Sign Up Here to Connect with {{ senior }} on Caressa.</h4>
                </div>
                <el-card class="box-card">
                    <el-form ref="signUpForm" :rules="rules" :model="signUpForm" label-width="120px" label-position="top">
                        <el-form-item label="Email address">
                            <el-input :disabled="true" v-model="signUpForm.email"></el-input>
                        </el-form-item>
                        <el-form-item label="Password" prop="pass1">
                            <el-input type="password" v-model="signUpForm.pass1" autocomplete="off"></el-input>
                        </el-form-item>
                        <el-form-item label="Password Confirmation" prop="pass2">
                            <el-input type="password" v-model="signUpForm.pass2" autocomplete="off"></el-input>
                        </el-form-item>
                        <p>By signing up, you agree our <a href="https://www.caressa.ai">Terms & Conditions</a></p>
                        <el-form-item>
                            <el-button type="plain" style="background-color: #2FCD8C; color: #FFFFFF;" @click="submitForm">Sign Up and Download</el-button>
                        </el-form-item>
                    </el-form>
                </el-card>
            </el-col>
        </el-row>
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
            name: String,
            email: String,
            senior: String,
            invitationCode: String,
            baseUrl: String
        },
        data () {
            let validatePass1 = (rule, value, callback) => {
                if (value.trim() === '') {
                    callback(new Error('Please input the password'));
                } else {
                    if (this.signUpForm.pass2 !== '') {
                        this.$refs.signUpForm.validateField('pass2');
                    }
                    callback();
                }
            };
            let validatePass2 = (rule, value, callback) => {
                if (value.trim() === '') {
                    callback(new Error('Please input the password again'));
                } else if (value !== this.signUpForm.pass1) {
                    callback(new Error('Two inputs don\'t match!'));
                } else {
                    callback();
                }
            };
            return {
                csrfToken: null,
                signUpForm: {
                    email: this.email,
                    pass1: '',
                    pass2: '',

                },
                rules: {
                    pass1: [
                        { validator: validatePass1, trigger: 'blur' }
                    ],
                    pass2: [
                        { validator: validatePass2, trigger: 'blur' }
                    ]
                }
            }
        },
        methods: {
            submitForm: function () {
                let vm = this
                this.$refs.signUpForm.validate((valid) => {
                    if (valid) {
                        this.$http({
                            headers: {
                                'X-CSRFToken': this.csrfToken
                            },
                            method: 'POST',
                            url: `${vm.baseUrl}/accounts/invitation/?invitation_code=${vm.invitationCode}`,
                            emulateJSON: true,
                            body: {
                                email: this.email,
                                password1: this.signUpForm.pass1,
                                password2: this.signUpForm.pass2,
                                invitation_code: this.invitationCode

                            }
                        }).then(_=>{
                            window.location.href = `${vm.baseUrl}/accounts/app-downloads/`
                        }, err=>{
                            console.log(err)
                        })
                    } else {
                        console.log('error submit!!');
                        return false;
                    }
                });
            }
        },
        mounted() {
            this.csrfToken = Cookies.get('csrftoken')
        }
    }
</script>

<style scoped>

</style>
