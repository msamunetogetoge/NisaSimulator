<template>
  <v-container fluid>
    <v-row justify="center" align="center">
      <v-col>
        <v-select
          v-model="e1"
          :items="methods"
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
          :items-per-page="5"
          class="elevation-1"
        ></v-data-table>
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'PortfolioPage',
  data() {
    return {
      e1: 'ほげ',
      methods: [],
      headers: [
        {
          text: 'Dessert (100g serving)',
          align: 'start',
          sortable: false,
          value: 'name',
        },
        { text: 'Calories', value: 'calories' },
        { text: 'Fat (g)', value: 'fat' },
        { text: 'Carbs (g)', value: 'carbs' },
        { text: 'Protein (g)', value: 'protein' },
        { text: 'Iron (%)', value: 'iron' },
      ],
      portfolio: [
        {
          name: 'Frozen Yogurt',
          calories: 159,
          fat: 6.0,
          carbs: 24,
          protein: 4.0,
          iron: '1%',
        },
        {
          name: 'Ice cream sandwich',
          calories: 237,
          fat: 9.0,
          carbs: 37,
          protein: 4.3,
          iron: '1%',
        },
        {
          name: 'Eclair',
          calories: 262,
          fat: 16.0,
          carbs: 23,
          protein: 6.0,
          iron: '7%',
        },
        {
          name: 'Cupcake',
          calories: 305,
          fat: 3.7,
          carbs: 67,
          protein: 4.3,
          iron: '8%',
        },
        {
          name: 'Gingerbread',
          calories: 356,
          fat: 16.0,
          carbs: 49,
          protein: 3.9,
          iron: '16%',
        },
        {
          name: 'Jelly bean',
          calories: 375,
          fat: 0.0,
          carbs: 94,
          protein: 0.0,
          iron: '0%',
        },
        {
          name: 'Lollipop',
          calories: 392,
          fat: 0.2,
          carbs: 98,
          protein: 0,
          iron: '2%',
        },
        {
          name: 'Honeycomb',
          calories: 408,
          fat: 3.2,
          carbs: 87,
          protein: 6.5,
          iron: '45%',
        },
        {
          name: 'Donut',
          calories: 452,
          fat: 25.0,
          carbs: 51,
          protein: 4.9,
          iron: '22%',
        },
        {
          name: 'KitKat',
          calories: 518,
          fat: 26.0,
          carbs: 65,
          protein: 7,
          iron: '6%',
        },
      ],
      formatedDate: () => {
        const date = new Date()
        const formatday = `${date.getFullYear()}年${
          date.getMonth() + 1
        }月${date.getDate()}日`
        return formatday
      },
    }
  },
  mounted() {
    // portfolio, methods を取得する
  },
}
</script>
