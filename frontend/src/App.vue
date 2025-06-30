<template>
  <map-view></map-view>
  <div class="legend-box">
    <div class="header-box">图例</div>
    <div class="legend-item">
      <div class="legend-color one6"></div>
      <div class="legend-text">70~80</div>
    </div>
    <div class="legend-item">
      <div class="legend-color one5"></div>
      <div class="legend-text">65~70</div>
    </div>
    <div class="legend-item">
      <div class="legend-color one4"></div>
      <div class="legend-text">60~65</div>
    </div>
    <div class="legend-item">
      <div class="legend-color one3"></div>
      <div class="legend-text">55~60</div>
    </div>
    <div class="legend-item">
      <div class="legend-color one1"></div>
      <div class="legend-text">50~55</div>
    </div>
    <div class="legend-item">
      <div class="legend-color one"></div>
      <div class="legend-text">40~50</div>
    </div>
  </div>
</template>

<script setup>
import MapView from './components/Map.vue'
</script>

<style scoped>
.legend-box {
  position: absolute;
  bottom: 10px;
  left: 10px;
  width: 100px;
  height: 200px;
  padding: 20px;
  z-index: 99;
  background: white;
  border-radius: 10px;
}
.header-box {
  font-size: 16px;
  color: #333333;
  text-align: center;
}
.legend-item {
  color: #333333;
  display: flex;
  align-items: center;
}
.legend-color {
  width: 10px;
  height: 10px;
  background: #333333;
  margin-right: 10px;
}
.one {
  background: #81c8a6;
}
.one1 {
  background: #4abff3;
}
.one2 {
  background: #d0dd00;
}
.one3 {
  background: #fcf000;
}
.one4 {
  background: #ec4d06;
}
.one5 {
  background: #d20e18;
}
.one6 {
  background: #9b0b12;
}
</style>
