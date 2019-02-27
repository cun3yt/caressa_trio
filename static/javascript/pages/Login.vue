<template>
    <div>
        <p v-if="errors" class="errors">
            Your email address and password didn't match.
            Please try again.
        </p>

        Login
        <form>
            <table>
                <tr>
                    <td>Email Address</td>
                    <td>
                        <input type="email" name="username"
                               autofocus="autofocus" maxlength="254"
                               required="required" id="id_username"
                               v-model="username">
                    </td>
                </tr>
                <tr>
                    <td>Password</td>
                    <td>
                        <input type="password" name="password"
                               required="required" id="id_password"
                               v-model="password">
                    </td>
                </tr>
            </table>

            <input type="hidden" name="next" :value="nextPage">
            <input type="submit" value="Login" v-on:click.prevent="login()">
        </form>

        <p>
            Forget Your Password? <a :href="forgetPasswordUrl">Click Here</a>
        </p>
    </div>
</template>

<script>
    export default {
        name: "Login",
        props: {
            clientId: String,
            clientSecret: String,
            apiBase: String,
            nextPage: String,
            loginUrl: String,
            forgetPasswordUrl: String
        },
        data () {
            return {
                username: '',
                password: '',
                errors: false
            }
        },
        methods: {
            api_url(path) {
                return `${this.apiBase}/${path}`
            },
            login () {
                let that = this
                this.errors = false

                this.$http({
                    method: 'POST',
                    url: this.api_url('o/token/'),
                    emulateJSON: true,
                    body: {
                        grant_type: 'password',
                        username: this.username,
                        password: this.password
                    },
                    headers: {
                        Authorization: 'Basic ' + btoa(this.clientId + ':' + this.clientSecret)
                    }
                }).then(response => {
                    that.$cookies.set('access_token', response.body.access_token)
                    that.$cookies.set('refresh_token', response.body.refresh_token)
                    window.location.href = that.api_url('accounts/facility/')
                }).catch(err => {
                    this.errors = true
                })
            }
        }
    }
</script>

<style scoped>
.errors {
    border: 2px dashed indianred;
    width: 60%;
    padding: 10px;
}
</style>
