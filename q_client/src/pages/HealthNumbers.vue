<template>
  <q-page padding class="row justify-center">
    <div class="main-content">
      <q-card>
        <q-card-title>
          Blood Pressure
        </q-card-title>
        <q-card-separator />
        <q-card-main class="row">
          <div class="col-sm-4 col-xs-5 row last-value">
            <div class="text-weight-bolder col-12 text-positive" style="font-size: 3em">
              {{bloodPressureChart.data.lastMeasurement[0]}}/{{bloodPressureChart.data.lastMeasurement[1]}}
            </div>
            <div class="text-blue-grey-4 col-5" style="font-size: 1.2em; font-weight: bold;">
              mmHg
            </div>
            <div class="text-blue-grey-4 col-6 text-right" style="margin-top: 2px;">
              {{bloodPressureChart.data.lastMeasurement[2]}}
            </div>
          </div>
          <div class="col-sm-8 col-xs-7">
            <line-chart :chart-data="bloodPressureChart.data" ref="bloodPressure" :options="bloodPressureChart.options" :height="bloodPressureChart.options.height"></line-chart>
          </div>
        </q-card-main>
      </q-card>

      <q-card>
        <q-card-title>
          Body Weight
        </q-card-title>
        <q-card-separator />
        <q-card-main class="row">
          <div class="col-sm-4 col-xs-5 row last-value">
            <div class="text-weight-bolder col-7 text-positive" style="font-size: 3em">
              {{weightChart.data.lastMeasurement[0]}}
            </div>
            <div class="col-5 text-blue-grey-4">
              <div style="font-size: 1.2em; font-weight: bold; height: 22px; margin-top: 4px;">lbs</div>
              <div>{{weightChart.data.lastMeasurement[1]}}</div>
            </div>
          </div>
          <div class="col-sm-8 col-xs-7">
            <line-chart :chart-data="weightChart.data" ref="weight" :options="weightChart.options" :height="weightChart.options.height"></line-chart>
          </div>
        </q-card-main>
      </q-card>

      <!-- this is static -->
      <q-card>
        <q-card-title>Blood Sugar</q-card-title>
        <q-card-separator />
        <q-card-main class="row">
          <div class="col-sm-4 col-xs-5 row last-value">
            <div class="text-weight-bolder col-7 text-positive" style="font-size: 3em">
              {{bloodSugar.data.lastMeasurement[0]}}
            </div>
            <div class="col-5 text-blue-grey-4">
              <div style="font-size: 1.2em; font-weight: bold; height: 22px; margin-top: 4px;">mg/dl</div>
              <div>{{bloodSugar.data.lastMeasurement[1]}}</div>
            </div>
          </div>
          <div class="col-sm-8 col-xs-7">
            <bar-chart :chart-data="bloodSugar.data" ref="bloodSugar" :options="bloodSugar.options" :height="bloodSugar.options.height"></bar-chart>
          </div>
        </q-card-main>
      </q-card>

      <!-- this is static -->
      <q-card>
        <q-card-title class="row" style="display: flex;">
          <span class="col-4" style="width: 100px;">Positive Moods</span>
          <span class="tag text-white bg-positive col-6">Improve</span>
        </q-card-title>
        <q-card-separator/>
        <q-card-main class="text-blue-grey-4" style="font-size: 1.6em">
          <div class="row">
            <div class="col-1 text-positive"><q-icon name="arrow_upward"/></div>
            <div class="col-5">Amused</div>
            <div class="col-1"><q-icon name="brightness_1" style="font-size: 0.8em"/></div>
            <div class="col-5">Calm</div>
          </div>
          <div class="row">
            <div class="col-1 text-positive"><q-icon name="arrow_upward" /></div>
            <div class="col-5 text-positive">Happy</div>
            <div class="col-1 text-negative"><q-icon name="arrow_downward" /></div>
            <div class="col-5">Optimistic</div>
          </div>
          <div class="row">
            <div class="col-1"><q-icon name="brightness_1" style="font-size: 0.8em"/></div>
            <div class="col-5">Loving</div>
            <div class="col-1 text-negative"><q-icon name="arrow_downward" /></div>
            <div class="col-5 text-negative">Excited</div>
          </div>
        </q-card-main>
      </q-card>
    </div>
  </q-page>
</template>

<script>
import LineChart from 'components/LineChart'
import BarChart from 'components/BarChart'
import moment from 'moment'

export default {
  components: {
    LineChart,
    BarChart
  },
  props: ['setupContent'],
  created () {
    this.setupContent({
      title: 'Status'
    })

    let bloodPressureURL = this.$root.$options.hosts.rest + '/flat-api/medical-state/?m-type=blood_pressure&page_size=100'

    this.$auth.get(bloodPressureURL, {}).then(response => {
      let fetchLabels = d => moment(d.created).format('MM/DD')
      let fetchSystolic = d => d.data['systolic']
      let fetchDiastolic = d => d.data['diastolic']

      this.bloodPressureChart.data.labels = response.data.results.map(fetchLabels)
      this.bloodPressureChart.data.datasets[0].data = response.data.results.map(fetchSystolic)
      this.bloodPressureChart.data.datasets[1].data = response.data.results.map(fetchDiastolic)

      this.bloodPressureChart.data.lastMeasurement = this.lastBloodPressure()
      this.$refs.bloodPressure.update()
    })

    let weightURL = this.$root.$options.hosts.rest + '/flat-api/medical-state/?m-type=weight&page_size=100'

    this.$auth.get(weightURL, {}).then(response => {
      let fetchLabels = d => moment(d.created).format('MM/DD')
      let fetchWeight = d => d.data['amount']

      this.weightChart.data.labels = response.data.results.map(fetchLabels)
      this.weightChart.data.datasets[0].data = response.data.results.map(fetchWeight)

      this.weightChart.data.lastMeasurement = this.lastBodyWeight()
      this.$refs.weight.update()
    })
  },
  methods: {
    lastBloodPressure () {
      let count = this.bloodPressureChart.data.datasets[0].data.length
      let systolic = this.bloodPressureChart.data.datasets[0].data[count - 1]
      let diastolic = this.bloodPressureChart.data.datasets[1].data[count - 1]
      let datetime = this.bloodPressureChart.data.labels[count - 1]
      return [systolic, diastolic, datetime]
    },
    lastBodyWeight () {
      let count = this.weightChart.data.datasets[0].data.length
      let weight = this.weightChart.data.datasets[0].data[count - 1]
      let datetime = this.weightChart.data.labels[count - 1]
      return [weight, datetime]
    }
  },
  data () {
    return {
      bloodPressureChart: {
        data: {
          lastMeasurement: [0, 0, 0],
          labels: [],
          datasets: [
            {
              label: 'Systolic',
              backgroundColor: '#00cc99',
              data: [],
              fill: false,
              borderColor: '#00cc99'
            },
            {
              label: 'Diastolic',
              backgroundColor: '#ffcc0f',
              data: [],
              fill: false,
              borderColor: '#ffcc0f'
            }
          ]
        },
        options: {
          height: 250,
          backgroundColor: '#ff0000',
          label: 'Blood Pressure',
          fill: false,
          lineTension: 0,
          legend: {
            display: false
          }
        }
      },

      bloodSugar: {
        data: {
          lastMeasurement: [132, moment('2018-04-24 12:35:00 PST').format('MM/DD')],
          labels: ['03/23', '04/05', '04/13', '04/20', '04/23', '04/24'],
          datasets: [
            {
              label: 'Blood Sugar',
              backgroundColor: '#00cc99',
              data: [125, 130, 132, 116, 123, 132],
              fill: false,
              borderColor: '#00cc99'
            }
          ]
        },
        options: {
          height: 250,
          backgroundColor: '#ff0000',
          label: 'Blood Sugar',
          fill: false,
          legend: {
            display: false
          },
          scales: {
            yAxes: [{
              gridLines: {
                display: true
              },
              ticks: {
                min: 0
                // max: this.yTicks.max,
              }
            }]
          }
        }
      },

      weightChart: {
        data: {
          lastMeasurement: [0, 0],
          labels: [],
          datasets: [
            {
              label: 'Weight (lbs)',
              backgroundColor: '#00cc99',
              data: [],
              fill: false,
              borderColor: '#00cc99'
            }
          ]
        },
        options: {
          height: 250,
          backgroundColor: '#ff0000',
          label: 'Weight (lbs)',
          fill: false,
          lineTension: 0,
          cubicInterpolationMode: 'monotone',
          legend: {
            display: false
          },
          scales: {
            yAxes: [{
              gridLines: {
                display: true
              },
              ticks: {
                min: 0
                // max: this.yTicks.max,
              }
            }]
          }
        }
      }
    }
  }
}
</script>

<style scoped>
  .tag {
    width: 80px;
    border-radius: 100px;
    text-align: center;
    font-size: 0.7em;
    font-weight: bold;
    padding: 3px 8px 4px 8px;
    margin-left: 10px;
  }
</style>
