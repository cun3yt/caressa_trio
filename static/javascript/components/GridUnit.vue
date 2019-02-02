<template>
    <div>
        <span v-if="content.length==1">
            <input v-model='fieldValue' v-if="isEdit" v-on:keyup.stop="updateFormInput()" type="text" :name="name">
            <span v-else>{{ content[0] }}</span>
        </span>
        <div v-else v-for="entry in content">
            <label style="font-weight: bold">{{ entry.label }}:</label>
            <grid-unit :content="[entry.value]" :is-edit="isEdit" :name="entry.key"></grid-unit>
        </div>
    </div>
</template>

<script>
    import bus from '../utils.communication.js'

    export default {
        name: "grid-unit",
        props: {
            content: Array,
            name: String,
            isEdit: Boolean
        },
        mounted: function () {
            if (!this.isEdit) {
                return
            }

            if (this.content.length > 1) {
                return
            }

            this.updateFormInput()
            bus.$on('clearForm', this.clearForm)
        },
        data: function () {
            return {
                fieldValue: ''
            }
        },
        methods: {
            updateFormInput: function () {
                let app = this.$root.$children[0]
                app.$data.formData[this.name] = this.fieldValue
            },
            clearForm: function () {
                this.fieldValue = ''
            }
        }
    }
</script>

<style scoped>

</style>