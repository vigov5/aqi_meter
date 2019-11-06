<template>
  <div
    id="app"
    class="h-screen w-screen bg-gray-200"
  >
    <div class=" text-center flex flex-col pt-10">
      <div class="mx-auto flex flex-col">
        <div class="flex flex-row items-center mx-auto">
          <svg
            viewBox="0 0 20 20"
            class="w-4 h-4 fill-current text-red-500 mx-2"
          >
            <path d="M0 0l20 8-8 4-2 8z" />
          </svg>
          <span class="text-2xl">{{ place }}</span>
        </div>
        <div>
          {{ location }}
        </div>
        <div>
          {{ time }}
        </div>
      </div>
      <div class="flex flex-col">
        <div v-bind:class="['flex flex-row items-center mx-auto mt-10 rounded rounded-lg text-gray-800 shadow-md', rightClasses[level]]">
          <div v-bind:class="['px-10 py-6 rounded-tl-lg rounded-bl-lg', leftClasses[level]]">
            <div class="text-6xl font-bold leading-none">
              {{ aqi }}
            </div>
            <span class="text-sm">
              US AQI
            </span>
          </div>
          <div class="text-2xl px-10 h-auto max-w-xs">
            {{ texts[level] }}
          </div>
        </div>
        <div class="bg-white mt-6 mx-auto flex flex-col pt-4 pb-8 rounded rounded-lg shadow-md">
          <div class="text-xl">
            Pollutants
          </div>
          <div class="flex flex-row mt-4">
            <div class="mx-10 px-4 border-l-4 border-gray-500 text-left">
              <div>
                <span class="font-bold text-xl">
                  PM2.5
                </span>
                <span class="text-gray-600">
                  µg/m<sup>3</sup>
                </span>
              </div>
              <div class="text-left font-hairline text-3xl">
                {{ pm25 }}
              </div>
            </div>
            <div class="mx-10 px-4 border-l-4 border-gray-500 text-left">
              <div>
                <span class="font-bold text-xl">
                  PM10
                </span>
                <span class="text-gray-600">
                  µg/m<sup>3</sup>
                </span>
              </div>
              <div class="text-left font-hairline text-3xl">
                {{ pm10 }}
              </div>
            </div>
          </div>
        </div>
        <div class="bg-white mt-6 mx-auto flex flex-col pt-4 pb-4 rounded rounded-lg shadow-md px-6">
          <div class="text-xl">
            Last 12 hours
          </div>
          <div class="flex flex-row mt-4 h-40 items-end">
            <div
              v-for="(item, index) in last_aqis"
              v-bind:key="index"
              class="ml-1"
            >
              <div class="text-xs text-center w-full">
                {{ item.aqi }}
              </div>
              <div
                v-bind:class="['w-6', leftClasses[item.level]]"
                v-bind:style="{height: item.aqi/300*128 + 'px' }"
              >
              </div>
              <span class="text-xs">
                {{ item.time }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const Influx = require('influx')
const influx = new Influx.InfluxDB(process.env.VUE_APP_DB_URL)

export default {
  name: 'app',
  data () {
    return {
      place: process.env.VUE_APP_PLACE || 'Unknown',
      location: process.env.VUE_APP_LOCATION || 'Middle of Nowhere, Milky Way',
      aqi: 0,
      pm25: 0,
      pm10: 0,
      time: new Date().toString(),
      timer: '',
      levels: [50, 100, 150, 200, 300],
      last_aqis: [],
      texts: ['Good', 'Moderate', 'Unhealthy for sensitive groups', 'Unhealthy', 'Very Unhealthy'],
      leftClasses: ['bg-green-300', 'bg-yellow-400', 'bg-orange-400', 'bg-red-400', 'bg-purple-400'],
      rightClasses: ['bg-green-200', 'bg-yellow-300', 'bg-orange-300', 'bg-red-300', 'bg-purple-300']
    }
  },
  created () {
    this.fetchAQIData()
    this.timer = setInterval(this.fetchAQIData, 5 * 60 * 1000)
  },
  computed: {
    level: function () {
      return this.calcLevel(this.aqi)
    }
  },
  methods: {
    calcLevel: function (aqi) {
      for (let i = 0; i < this.levels.length; i++) {
        if (aqi <= this.levels[i]) return i
      }

      return 0
    },
    fetchAQIData () {
      influx.query(`select aqi, pm25, pm10 from aqi order by time desc limit 1`).then(rows => {
        rows.forEach(row => {
          this.aqi = row.aqi
          this.pm25 = row.pm25
          this.pm10 = row.pm10
          this.time = row.time.toString()
          // console.log(`AQI: ${row.aqi}, PM2.5: ${row.pm25}µg/m3, PM10: ${row.pm10}µg/m3`)
        })
      })

      let endRange = new Date()
      let startRange = new Date()
      startRange.setHours(startRange.getHours() - 12)
      influx.query(`SELECT mean(aqi) FROM aqi WHERE time >= '${startRange.toISOString()}' AND time < '${endRange.toISOString()}' GROUP BY time(1h) fill(none) LIMIT 12`).then(rows => {
        let tmp = []
        rows.forEach((row, index) => {
          let aqi = row.mean.toFixed(0)
          tmp.push({
            time: `${row.time.getHours()}h`,
            level: this.calcLevel(aqi),
            aqi: aqi
          })
        })
        this.last_aqis = tmp
      })
    },
    cancelAutoUpdate () {
      clearInterval(this.timer)
    }
  },
  beforeDestroy () {
    clearInterval(this.timer)
  }
}
</script>

<style>
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
</style>
