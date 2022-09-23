<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6" v-html="graph"> </v-col>
    This is ChartPage
  </v-row>
</template>

<!-- todo -->
<!-- plotly.jsのグラフオブジェクトを表示出来るようにする -->
<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  name: 'ChartPage',
  data() {
    return {
      graph: '',
      url: '/api',
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
      // let graphResponse = ''
      // await this.$axios
      //   .$get(this.url + '/graph/')
      //   .then(function (response) {
      //     graphResponse = response.graph
      //   })
      //   .catch(function (error) {
      //     console.log(error)
      //   })
      const graphResponse = await this.$axios.$get(this.url + '/graph/')

      this.graph = graphResponse
    },
  },
})
</script>>
