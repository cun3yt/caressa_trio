<template>
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">
                    <div class="modal-header">
                        <slot name="header">
                            Start Your Anouncement
                        </slot>
                    </div>
                    <div>
                        <div>
                            <i id="play" :class="playerIcon"
                               @click="playback"
                               style="font-size:26px; color:royalblue; cursor: pointer;"
                            />
                            <i :class="isRecording ? 'fas fa-stop-circle' : 'fas fa-microphone'"
                               v-on:click="toggleRecorder"
                               style="font-size:26px; color:royalblue; cursor: pointer;"/>
                            <audio ref="player" id="player" :src="audioSource && audioSource.url"/>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <slot name="footer">
                            <button class="modal-default-button" @click="closeModal">
                                Cancel
                            </button>
                            <button class="modal-default-button" @click="submitRecord">
                                Submit
                            </button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
    import Recorder from '../plugins/recorder.js'

    export default {
        name: 'public-address-modal',
        props: {
            accessToken: String,
            apiBase: String,
            user: Object,
            editSubmit: Function,
            errors: Array
        },
        mounted() {
            this.setupPlayer()
        },
        data (){
            return {
                audio: {
                    isUploading   : false,
                    recorder      : this._initRecorder(),
                    recordList    : [],
                    selected      : {},
                    uploadStatus  : null,
                    isPlaying: false,
                    player: null,
                    lastRecordKey: ''
                }
            }
        },
        methods: {
            closeModal: function (){
                this.$emit('close')
            },
            uploadFile: function (uploadUrl) {
                const recorderLength = this.audio.recorder.records.length
                const data = this.audio.recorder.records[recorderLength - 1]
                let file = new File([data.blob], this.audio.lastRecordKey)

                this.$http({
                    method: 'PUT',
                    url: uploadUrl,
                    body: file,
                    headers: {
                        'Content-Type': 'audio/mp3',
                    }
                }).then(response => {
                    this.queueUpNewMessage().then(response => this.closeModal())
                }).catch(err => {
                    console.log(err)
                })
            },
            queueUpNewMessage: function () {
                return this.$http({
                    method: 'POST',
                    url: this.api_url('new_message/'),
                    body: {
                       type: 'facility_web_audio',
                        key: this.audio.lastRecordKey,
                    },
                    headers:{
                        Authorization: 'Bearer ' + this.accessToken
                    }
                })
            },
            api_url(path) {
                return `${this.apiBase}/${path}`
            },
            setupPlayer () {
                this.audio.player = this.$refs.player
                this.audio.player.addEventListener('ended', () => {
                    this.audio.isPlaying = false
                })
            },
            toggleRecorder () {
                if (!this.isRecording || (this.isRecording && this.isPause)) {
                    this.audio.recorder.start()
                } else {
                    this.audio.recorder.stop()
                    this.audio.lastRecordKey = this.audioRecordKeyGenerator()
                }
            },
            stopRecorder () {
                if (!this.isRecording) {
                    return
                }
                this.audio.recorder.stop()
                this.audio.recordList = this.audio.recorder.recordList()
            },
            _initRecorder () {
                return new Recorder({
                    beforeRecording : (val) => { console.log(`beforeRecording ${val}`) },
                    afterRecording  : (val) => { console.log(`afterRecording: ${val}`) },
                    pauseRecording  : (val) => { console.log(`pauseRecording: ${val}`) },
                    micFailed       : (val) => {console.log(`micFailed: ${val}`)},
                    bitRate         : this.bitRate,
                    sampleRate      : this.sampleRate
                })
            },
            playback () {
                if (!this.audioSource) {
                    return
                }
                if (this.audio.isPlaying) {
                    this.audio.player.pause()
                } else {
                    setTimeout(() => { this.audio.player.play() }, 0)
                }
                this.audio.isPlaying = !this.audio.isPlaying
            },
            audioRecordKeyGenerator () {
                let today = new Date()
                let dd = today.getDate()
                let mm = today.getMonth() + 1
                let yyyy = today.getFullYear()
                let hour = today.getHours()
                let min = today.getMinutes()
                let sec = today.getSeconds()
                if (hour < 10) {
                    hour = '0' + hour
                }
                if (min < 10) {
                    min = '0' + min
                }
                if (sec < 10) {
                    sec = '0' + sec
                }
                if (dd < 10) {
                    dd = '0' + dd
                }
                if (mm < 10) {
                    mm = '0' + mm
                }
                return `${this.user.pk}-${hour}-${min}-${sec}-${mm}-${dd}-${yyyy}.mp3`
            },
            generateSignedUrl () {
                return this.$http({
                    method: 'POST',
                    url: this.api_url('generate_signed_url/'),
                    emulateJSON: true,
                    body: {
                        'key': this.audio.lastRecordKey,
                        'content-type': 'audio/mp3',
                        'client-method': 'put_object',
                        'request-type': 'PUT'
                    },
                    headers: {
                        Authorization: 'Bearer ' + this.accessToken
                    }
                })
            },
            submitRecord () {
                this.generateSignedUrl().then(res => {
                    this.uploadFile(res.body)
                })
            }

        },
        computed: {
            playerIcon () {
                return this.audio.isPlaying ? 'fas fa-pause' : 'fas fa-play'
            },
            isRecording () {
                return this.audio.recorder.isRecording
            },
            audioSource () {
                const recorderLength = this.audio.recorder.records.length
                const url = this.audio.recorder.records[recorderLength - 1]
                if (url) {
                    return url
                } else {
                    return false
                }
            }
        }
    }
</script>

<style scoped>
    .modal-mask {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, .5);
        display: table;
        transition: opacity .3s ease;
    }

    .modal-wrapper {
        display: table-cell;
        vertical-align: middle;
    }

    .modal-container {
        width: 300px;
        margin: 0px auto;
        padding: 20px 30px;
        background-color: #fff;
        border-radius: 2px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
        transition: all .3s ease;
        font-family: Helvetica, Arial, sans-serif;
    }

    .modal-header h3 {
        margin-top: 0;
        color: #42b983;
    }

    .modal-body {
        margin: 20px 0;
    }

    .modal-default-button {
        float: right;
    }

    /*
     * The following styles are auto-applied to elements with
     * transition="modal" when their visibility is toggled
     * by Vue.js.
     *
     * You can easily play with the modal transition by editing
     * these styles.
     */

    .modal-enter {
        opacity: 0;
    }

    .modal-leave-active {
        opacity: 0;
    }

    .modal-enter .modal-container,
    .modal-leave-active .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }

    .disabled {
        color: #A4A4A4;
    }
    .disabled input {
        cursor: not-allowed;
        color: #A4A4A4;
    }
</style>
