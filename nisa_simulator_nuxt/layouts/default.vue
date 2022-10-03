<!-- todo -->
<!-- updataData を実装する。ただし、python側でapiが準備出来てから。 -->
<template>
  <v-app dark>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="miniVariant"
      :clipped="clipped"
      fixed
      app
    >
      <v-list>
        <v-list-item
          v-for="(item, i) in items"
          :key="i"
          :to="item.to"
          nuxt
          exact
        >
          <v-list-item-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title v-text="item.title" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item @click="updateData">
          <v-list-item-action>
            <v-icon>{{ updateItem.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title v-text="updateItem.title" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item :href="sbiItem.to" :target="'_blank'">
          <v-list-item-action>
            <v-icon>{{ sbiItem.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title v-text="sbiItem.title" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar :clipped-left="clipped" fixed app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title v-text="title" />
    </v-app-bar>
    <v-main>
      <v-container>
        <v-dialog v-model="dialog" persistent width="300">
          <v-card height="190" class="text-center">
            <v-progress-circular
              :indeterminate="dialog"
              :size="100"
              color="primary"
              class="mt-4"
              >Updating...
            </v-progress-circular>
          </v-card>
        </v-dialog>
        <Nuxt />
      </v-container>
    </v-main>
    <v-footer :absolute="!fixed" app>
      <v-card width="100%" class="lighten-1 text-center">
        <v-col class="text-center" cols="12">
          {{ new Date().getFullYear() }} — <strong>masamunenoheya</strong>
        </v-col>
      </v-card>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  name: 'DefaultLayout',

  data() {
    return {
      url: '/api',
      dialog: false,
      clipped: false,
      drawer: false,
      fixed: false,
      items: [
        {
          icon: 'mdi-home',
          title: 'ホーム',
          to: '/',
        },
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
      sbiItem: {
        icon: 'mdi-login',
        title: 'SBI証券',
        to: 'https://site0.sbisec.co.jp/marble/fund/powersearch/fundpsearch.do?Param7=other_3',
      },
      updateItem: {
        icon: 'mdi-update',
        title: 'データ更新',
      },
      title: 'Nisa Simulator',
    }
  },
  methods: {
    async updateData() {
      this.dialog = true
      await this.$axios
        .$post(this.url + '/update')
        .then(function () {})
        .catch(function (error) {
          console.error(error)
          alert('データ更新に失敗しました')
        })
      this.dialog = false
    },
  },
})
</script>
