<template>
    <div class="main-content">
        <h1> Component from Vue </h1>
        <h3> Hede: {{ userId }} </h3>
    </div>
</template>

<script>
    export default {
        name: "App.vue",
        props: {
            userId: Object
        },
        mounted() {
            console.log(this.userId)
        }
    }
</script>

<style scoped>
    .main-content {
        margin: 0 auto;
        font-family: sans-serif;
        background-color: #ccf7e2;
        padding: 10px;
        border-radius: 5px;
        max-width: 500px;
    }
</style>