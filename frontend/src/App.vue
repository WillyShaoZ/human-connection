<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('App Launch')
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* Global styles */
page {
  background: #FFE135;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', Roboto,
    'Helvetica Neue', sans-serif;
}

/* Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
