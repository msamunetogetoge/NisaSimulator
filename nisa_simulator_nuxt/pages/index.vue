<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <v-card>
        <v-card-title class="headline">
          Welcome to NISA SIMULATOR
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="(item, i) in items"
              :key="i"
              :to="item.to"
              router
              exact
            >
              <v-list-item-action>
                <v-icon>{{ item.icon }}</v-icon>
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title v-text="item.title" />
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'IndexPage',
  data() {
    return {
      items: [
        {
          icon: 'mdi-chart-areaspline',
          title: 'チャート',
          to: '/chart',
        },
        {
          icon: 'mdi-chart-pie',
          title: 'ポートフォリオ',
          to: '/portfolio',
        },
      ],
    }
  },
}
</script>
