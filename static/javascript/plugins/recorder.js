import { Mp3Encoder } from 'lamejs'

//Utility
function convertTimeMMSS (seconds) {
    return new Date(seconds * 1000).toISOString().substr(14, 5)
}

// Encoder
class Encoder{
    constructor(config) {
        this.bitRate    = config.bitRate
        this.sampleRate = config.sampleRate
        this.dataBuffer = []
        this.encoder    = new Mp3Encoder(1, this.sampleRate, this.bitRate)
    }

    encode(arrayBuffer) {
        const maxSamples = 1152
        const samples    = this._convertBuffer(arrayBuffer)
        let remaining    = samples.length

        for (let i = 0; remaining >= 0; i += maxSamples) {
            const left = samples.subarray(i, i + maxSamples)
            const buffer = this.encoder.encodeBuffer(left)
            this.dataBuffer.push(new Int8Array(buffer))
            remaining -= maxSamples
        }
    }

    finish() {
        this.dataBuffer.push(this.encoder.flush())
        const blob = new Blob(this.dataBuffer, { type: 'audio/mp3' })
        this.dataBuffer = []

        return {
            id    : Date.now(),
            blob  : blob,
            url   : URL.createObjectURL(blob)
        }
    }

    _floatTo16BitPCM(input, output) {
        for (let i = 0; i < input.length; i++) {
            const s = Math.max(-1, Math.min(1, input[i]))
            output[i] = (s < 0 ? s * 0x8000 : s * 0x7FFF)
        }
    }

    _convertBuffer(arrayBuffer) {
        const data = new Float32Array(arrayBuffer)
        const out = new Int16Array(arrayBuffer.length)
        this._floatTo16BitPCM(data, out)
        return out
    }
}
// Recorder
export default class Recorder {
    constructor (options = {}) {
        this.beforeRecording = options.beforeRecording
        this.pauseRecording  = options.pauseRecording
        this.afterRecording  = options.afterRecording
        this.micFailed       = options.micFailed
        this.bitRate         = options.bitRate || 128
        this.sampleRate      = options.sampleRate || 44100

        this.bufferSize = 4096
        this.records    = []

        this.isPause     = false
        this.isRecording = false

        this.duration = 0
        this.volume   = 0

        this._duration = 0
    }

    start () {
        const constraints = {
            video: false,
            audio: {
                channelCount: 1,
                echoCancellation: false
            }
        }

        this.beforeRecording && this.beforeRecording('start recording')

        navigator.mediaDevices
            .getUserMedia(constraints)
            .then(this._micCaptured.bind(this))
            .catch(this._micError.bind(this))
        this.isPause = false
        this.isRecording = true
        this.lameEncoder = new Encoder({
            bitRate    : this.bitRate,
            sampleRate : this.sampleRate
        })
    }

    stop () {
        this.stream.getTracks().forEach((track) => track.stop())
        this.input.disconnect()
        this.processor.disconnect()
        this.context.close()

        const record = this.lameEncoder.finish()
        record.duration = convertTimeMMSS(this.duration)
        this.records.push(record)

        this._duration = 0
        this.duration  = 0

        this.isPause     = false
        this.isRecording = false

        this.afterRecording && this.afterRecording(record)
    }

    pause () {
        this.stream.getTracks().forEach((track) => track.stop())
        this.input.disconnect()
        this.processor.disconnect()
        this.context.close()

        this._duration = this.duration
        this.isPause = true

        this.pauseRecording && this.pauseRecording('pause recording')
    }

    recordList () {
        return this.records
    }

    lastRecord () {
        return this.records.slice(-1)
    }

    _micCaptured (stream) {
        this.context    = new(window.AudioContext || window.webkitAudioContext)()
        this.duration   = this._duration
        this.input      = this.context.createMediaStreamSource(stream)
        this.processor  = this.context.createScriptProcessor(this.bufferSize, 1, 1)
        this.stream     = stream

        this.processor.onaudioprocess = (ev) => {
            const sample = ev.inputBuffer.getChannelData(0)
            let sum = 0.0

            this.lameEncoder.encode(sample)

            for (let i = 0; i < sample.length; ++i) {
                sum += sample[i] * sample[i]
            }

            this.duration = parseFloat(this._duration) + parseFloat(this.context.currentTime.toFixed(2))
            this.volume = Math.sqrt(sum / sample.length).toFixed(2)
        }

        this.input.connect(this.processor)
        this.processor.connect(this.context.destination)
    }

    _micError (error) {
        this.micFailed && this.micFailed(error)
    }
}
