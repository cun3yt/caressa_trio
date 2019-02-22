<template>
    <div class="header sticky" id="myHeader">
        <div>Welcome {{user.first_name}} {{user.last_name}}</div>
        <button @click="logout()" href="#">Logout</button>
        <div>
            <label class="switch">
                <input type="checkbox" @click="toggleSwitch" v-model="isSwitchOn" checked>
                <span class="slider round"></span>
            </label>
        </div>
        <button @click="activatePublicAddressModal">{{broadcastSwitch}}</button>
        <form id="search">Search <input name="query" v-model="searchKey"></form>
    </div>
</template>

<script>
    import PublicAddress from '../components/PublicAddressModal.vue'
    import bus from '../utils.communication'
    export default {
        name: "FixedHeader",
        components:{PublicAddress},
        props: {
            user: Object,
            logout: Function
        },
        methods: {
            toggleSwitch () {

            },
            activatePublicAddressModal () {
                bus.$emit('broadcast')
            }
        },
        data () {
            return {
                searchKey: '',
                isSwitchOn : true,
            }
        },
        computed: {
            broadcastSwitch: function () {
                return this.isSwitchOn ? 'Broadcast' : 'Send Message to Selected'
            }
        },
        watch: {
            searchKey : function () {
                bus.$emit('searchKey', this.searchKey)
            }
        },
    }
</script>

<style scoped>
    /* Style the header */
    .header {
        padding: 10px 16px;
        background: #f9f9f9;
        color: #42b983;
    }

    /* The sticky class is added to the header with JS when it reaches its scroll position */
    .sticky {
        position: fixed;
        top: 0;
        width: 100%
    }

    /* The switch - the box around the slider */
    .switch {
        position: relative;
        display: inline-block;
        width: 30px;
        height: 17px;
    }

    /* Hide default HTML checkbox */
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    /* The slider */
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        -webkit-transition: .4s;
        transition: .4s;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 13px;
        width: 13px;
        left: 2px;
        bottom: 2px;
        background-color: white;
        -webkit-transition: .4s;
        transition: .4s;
    }

    input:checked + .slider {
        background-color: #2196F3;
    }

    input:focus + .slider {
        box-shadow: 0 0 1px #2196F3;
    }

    input:checked + .slider:before {
        -webkit-transform: translateX(13px);
        -ms-transform: translateX(13px);
        transform: translateX(13px);
    }

    /* Rounded sliders */
    .slider.round {
        border-radius: 34px;
    }

    .slider.round:before {
        border-radius: 50%;
    }
</style>
