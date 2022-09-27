<template>
  <!-- <section>This is ChartPage</section> -->

  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="8">
      <line-chart
        :chart-options="chartOptions"
        :chart-data="chartData"
        :width="width"
        :height="height"
        :title="'hogege'"
        chart-id="myCustomId"
      />
    </v-col>
  </v-row>

  <!-- <v-container justify="center" align="center">
    <line-chart
      :chart-options="chartOptions"
      :chart-data="chartData"
      :width="width"
      :height="height"
      chart-id="myCustomId"
    />
  </v-container> -->
</template>


<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'ChartPage',
  props: {
    chartId: {
      type: String,
      default: 'line-chart',
    },
    datasetIdKey: {
      type: String,
      default: 'label',
    },
    width: {
      type: Number,
      default: 800,
    },
    height: {
      type: Number,
      default: 400,
    },
    cssClasses: {
      default: '',
      type: String,
    },
    styles: {
      type: Object,
      default: () => {},
    },
    plugins: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      graph: '',
      url: '/api',
      chartData: {
        labels: [],
        datasets: [],
      },
      chartOptions: {
        responsive: true,
        title: {
          display: true,
          position: 'top',
          text: 'title',
        },
        legend: {
          display: true,
          position: 'bottom',
        },
      },
    }
  },

  mounted() {
    // graph にデータを送る
    // python側のapi待ち
    this.graph = 'GRAPH is CREATED'
    this.getChart()
  },
  methods: {
    async getChart() {
      const graphResponse = await this.$axios.$get(this.url + '/graph/')
      this.chartData = JSON.parse(graphResponse)
    },
  },
})
</script>>
