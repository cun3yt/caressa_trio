<template>
  <div class="main-content">
    Health Numbers
    <div class="layout-view">
      <line-chart :chart-data="chartData" ref="lineChart" :options="chartOptions" :height="chartOptions.height"></line-chart>
    </div>

  </div>
</template>

<script>
  import LineChart from './LineChart'

  export default {
    components: {
      LineChart
    },
    props: ['setupContent'],
    created () {
      this.setupContent({
        title: 'Status'
      })

      this.$http.get(this.$root.$options.apiHost + '/a_user_medical_state?measurement=eq.blood_pressure&order=created', {
        // 'measurement_0': 'blood_pressure'
      }).then(response => {
        let fetchLabels = d => d.created.slice(0, 10)
        let fetchSystolic = d => d.data['systolic']
        let fetchDiastolic = d => d.data['diastolic']

        this.chartData.labels = response.data.map(fetchLabels)
        this.chartData.datasets[0].data = response.data.map(fetchSystolic)
        this.chartData.datasets[1].data = response.data.map(fetchDiastolic)

        this.$refs.lineChart.update()
      })
    },
    data () {
      return {
        chartData: {
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
        chartOptions: {
          height: 150,
          backgroundColor: '#ff0000',
          label: 'Blood Pressure',
          fill: false
        }
      }
    }
  }
</script>
