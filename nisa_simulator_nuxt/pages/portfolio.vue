<template>
  <v-container fluid>
    <v-row justify="center" align="center">
      <v-col>
        <v-select
          v-model="selected_name"
          :items="method_names"
          menu-props="auto"
          label="Select Method"
          hide-details
          prepend-icon="mdi-calculator"
          single-line
        ></v-select>
      </v-col>
    </v-row>
    <v-row justify="center" align="center">
      <v-card>
        <v-card-title> {{ formatedDate() }} のポートフォリオ </v-card-title>
        <v-data-table
          :headers="headers"
          :items="portfolio"
          :sort-by="'yen'"
          :sort-desc="true"
          hide-default-footer
          class="elevation-1"
        ></v-data-table>
      </v-card>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  name: 'PortfolioPage',
  data() {
    return {
      selected_name: '',
      method_names: [],
      headers: [],
      portfolio: [],
      url: '/api',
      formatedDate: () => {
        const date = new Date()
        const formatday = `${date.getFullYear()}年${
          date.getMonth() + 1
        }月${date.getDate()}日`
        return formatday
      },
    }
  },
  watch: {
    selected_name() {
      this.getPortfolio()
    },
  },

  mounted() {
    this.getMethods()
    this.getHeaders()
  },

  methods: {
    async getHeaders() {
      const headersResponse = JSON.parse(
        await this.$axios.$get(this.url + '/portfolio_header')
      )
      this.headers = headersResponse.headers
    },
    async getMethods() {
      const methodsResponse = await this.$axios.$get(this.url + '/methods')
      this.method_names = methodsResponse
    },
    async getPortfolio() {
      const portfolioResponse = JSON.parse(
        await this.$axios.$get(this.url + '/portfolio/' + this.selected_name)
      )
      this.portfolio = []
      this.portfolio = portfolioResponse.portfolio
    },
  },
})
</script>
