<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      {{ graph }}
    </v-col>
    This is ChartPage
  </v-row>
</template>

<script>
export default {
  name: 'ChartPage',
  data() {
    return {
      graph: '',
    }
  },
  mounted() {
    // graph にデータを送る
    // python側のapi待ち
    this.graph = 'GRAPH is CREATED'
  },
}
</script>
