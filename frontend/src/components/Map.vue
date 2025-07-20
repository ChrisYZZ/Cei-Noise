<template>
  <div class="map-box" id="contanter"></div>
  <div class="btn-box">
    <div
      class="btn"
      :class="item.selected ? 'btn-select' : ''"
      @click="changeLayer(item)"
      v-for="item in btnList"
      :key="item.name"
    >
      {{ item.name }}
    </div>
    <br />
  </div>
  <div class="NOISE-BOX">
    噪声图
    <select
      style="height: 30px"
      class="select-box"
      v-model="selectedRoute"
      @change="updateHeatmap"
    >
      <option v-for="(item, index) in noiseList" :key="index" :value="index">
        {{ item.name }}
      </option>
    </select>
  </div>
  <!-- 添加风场参数输入div。插入在NOISE-BOX后，作为类似UI控件。 -->
  <div class="WIND-BOX">
    风场参数
    <input
      class="select-box"
      v-model="windDirection"
      type="number"
      placeholder="风向 (0-360)"
    />
    <input
      class="select-box"
      v-model="windLevel"
      type="number"
      placeholder="风级 (1-10)"
    />
    <div class="btn" @click="updateWindParams">应用参数</div>
  </div>
  
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
// import { CesiumHeatmap } from 'cqdlzx-cesium-heatmap'
import { WindFieldManager } from '../utils/WindField.js'; // 风场模块

const btnList = ref([
  {
    name: '三维模型',
    selected: true,
    type: '3dtiles',
  },
  {
    name: '飞行路线',
    selected: false,
    type: 'fly',
  },
  {
    name: 'poi',
    selected: false,
    type: 'poi',
  },
  {
    name: '热力图',
    selected: false,
    type: 'heatMap',
  },
  // {
  //   name: '噪声图',
  //   selected: false,
  //   type: 'heatMap1',
  // },
  {
    name: 'noise-map',
    selected: false,
    type: 'noiseMap',
  },

  {
    name: '风场',
    selected: false,
    type: 'windField',
  },
  
])

onMounted(() => {
  initMap()
  initNosieList()
})

let noiseList = ref([])
let selectedRoute = ref(null)
const initNosieList = () => {
  //axios.get('http://127.0.0.1:8000/data').then((res) => {
  axios.get('/api/data').then((res) => {
    let _data = res.data
    noiseList.value = _data
  })
}

let viewer
// 在initMap函数中调用示例，可根据实际需求修改坐标
const initMap = () => {
  viewer = new Cesium.Viewer('contanter', {
    baseLayer: Cesium.ImageryLayer.fromProviderAsync(
      Cesium.ArcGisMapServerImageryProvider.fromUrl(
        'https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer'
      )
    ),
    animation: false, //是否显示动画控件
    geocoder: true, //是否显示地名查找控件
    timeline: false, //是否显示时间线控件
    sceneModePicker: true, //是否显示投影方式控件
    navigationHelpButton: false, //是否显示帮助信息控件
    infoBox: true, //是否显示点击要素之后显示的信息
  })
  //  let layer = Cesium.ImageryLayer.fromProviderAsync(
  //     Cesium.IonImageryProvider.fromAssetId(3812)
  //   )
  //   viewer.scene.imageryLayers.add(layer);

  // viewer.camera.changed.addEventListener(function () {
  //   const { position, heading, pitch, roll } = viewer.camera
  //   // 定义笛卡尔坐标
  //   const cartesian = new Cesium.Cartesian3(position.x, position.y, position.z)
  //   // 定义椭球体参数
  //   const ellipsoid = Cesium.Ellipsoid.WGS84
  //   // 将笛卡尔坐标转换为84坐标
  //   const cartographic = ellipsoid.cartesianToCartographic(cartesian)
  //   const longitude = Cesium.Math.toDegrees(cartographic.longitude)
  //   const latitude = Cesium.Math.toDegrees(cartographic.latitude)
  //   const height = cartographic.height
  //   // 输出84坐标
  //   console.log(longitude, latitude, height, heading, pitch, roll)
  // })

  viewer.canvas.addEventListener('click', (event) => {
    const ray = viewer.camera.getPickRay(event)
    if (!ray) return

    const cartesian = viewer.scene.globe.pick(ray, viewer.scene)
    if (!cartesian) return

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian)
    const longitude = Cesium.Math.toDegrees(cartographic.longitude)
    const latitude = Cesium.Math.toDegrees(cartographic.latitude)
    const height = cartographic.height

    console.log(
      `Longitude: ${longitude}, Latitude: ${latitude}, Height: ${height}`
    )
  })
  //
  // /11/1074/693.png

  // viewer.imageryLayers.addImageryProvider(
  //   new Cesium.UrlTemplateImageryProvider({
  //     url: '/tiles/1576396593/{z}/{x}/{y}.png',
  //   })
  // )

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(
      113.25998414350605,
      23.068504647483266,
      554.6266437605619
    ),
    orientation: {
      roll: 6.283091165942747,
      pitch: -0.050350776440997835,
      heading: 6.045396694337831,
    },
  })

  init3DTilesLayer({
    selected: true,
  })
}

const changeLayer = (item) => {
  item.selected = !item.selected
  switch (item.type) {
    case '3dtiles':
      init3DTilesLayer(item)
      break
    case 'fly':
      satrt(item)
      break
    case 'poi':
      initGeojson(item)
      break
    case 'heatMap':
      initHeatMap(item)
      break
    case 'heatMap1':
      initHeatMap1(item)
      break
    case 'noiseMap':
      initNoiseMap(item)
      break
    case 'windField':
      toggleWindField(item)
      break
  }
}
let NoiseMapLayer
const initNoiseMap = (item) => {
  // 如果已存在图层且按钮未选中，则移除
  if (NoiseMapLayer && !item.selected) {
    viewer.imageryLayers.remove(NoiseMapLayer)
    NoiseMapLayer = null
    return  // 重要：添加 return，避免继续执行添加代码
  }
  
  // 只有在按钮选中时才添加图层
  if (item.selected) {
    NoiseMapLayer = viewer.imageryLayers.addImageryProvider(
      new Cesium.UrlTemplateImageryProvider({
        url: '/tiles/1576396593/{z}/{x}/{y}.png',
      })
    )
  }
}

/*
let NoiseMapLayer
const initNoiseMap = (item) => {
  if (NoiseMapLayer) {
    viewer.imageryLayers.remove(NoiseMapLayer)
  }
  NoiseMapLayer = viewer.imageryLayers.addImageryProvider(
    new Cesium.UrlTemplateImageryProvider({
      url: '/tiles/1576396593/{z}/{x}/{y}.png',
    })
  )
}
*/

let tilesetLayer
const init3DTilesLayer = (data) => {
  if (tilesetLayer && !data.selected) {
    viewer.scene.primitives.remove(tilesetLayer)
    tilesetLayer = null
    return
  }
  add3DTilesLayer({
    url: '/GZ3dtile/tileset.json',
    success: (tileset) => {
      tilesetLayer = tileset
      // satrt()
    },
  })
}

async function add3DTilesLayer(opiton) {
  if (!opiton) return false
  if (!opiton.url) {
    if (opiton.error) {
      opiton.error('无3dtiles文件的url')
    } else {
      throw new Error('无3dtiles文件的url')
    }
    return false
  }

  const tileset = await Cesium.Cesium3DTileset.fromUrl(opiton.url, {
    skipLevelOfDetail: true,
    baseScreenSpaceError: 1024,
    skipScreenSpaceErrorFactor: 16,
    skipLevels: 1,
    immediatelyLoadDesiredLevelOfDetail: false,
    loadSiblings: false,
    cullWithChildrenBounds: true,
    backFaceCulling: opiton.doubleSided ? false : true,
    // 这个参数默认是false，同等条件下，叶子节点会优先加载。但是Cesium的tile加载优先级有很多考虑条件，
    // 这个只是其中之一，如果skipLevelOfDetail=false，这个参数几乎无意义。所以要配合skipLevelOfDetail=true来使用，
    // 此时设置preferLeaves=true。这样我们就能最快的看见符合当前视觉精度的块，对于提升大数据以及网络环境不好的前提下有一点点改善意义。
    preferLeaves: true,
    maximumScreenSpaceError: 40, // 最大的屏幕空间误差
    maximumNumberOfLoadedTiles: 100000, // 最大加载瓦片个数
    // skipScreenSpaceErrorFactor: 16,
    maximumMemoryUsage: 512, // 内存分配变小有利于倾斜摄影数据回收，提升性能体验
  })
  viewer.scene.primitives.add(tileset)
  if (opiton.success) opiton.success(tileset)

  return {
    tiles: tileset,
  }
}

let planeModel
const satrt = (_data) => {
  if (planeModel && !_data.selected) {
    viewer.entities.remove(planeModel)
    planeModel = null
    viewer.clock.shouldAnimate = false
    return
  }
  //axios.get('http://127.0.0.1:8000/data').then((res) => { //更换绝对地址，适应端口调整可能性
  axios.get('/api/data').then((res) => {
    let _data = res.data
    viewer.clock.shouldAnimate = true
    // 起始时间
    let start = Cesium.JulianDate.fromDate(new Date(2025, 4, 23))
    // 结束时间
    let stop = Cesium.JulianDate.addSeconds(start, 900, new Cesium.JulianDate())
    // 设置始时钟始时间
    viewer.clock.startTime = start.clone()
    // 设置时钟当前时间
    viewer.clock.currentTime = start.clone()
    // 设置始终停止时间
    viewer.clock.stopTime = stop.clone()
    // 时间速率，数字越大时间过的越快
    viewer.clock.multiplier = 10
    // 时间轴
    // viewer.timeline.zoomTo(start, stop)
    // 循环执行,即为2，到达终止时间，重新从起点时间开始
    viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP
    for (let j = 0; j < _data.length; j++) {
      let property = computeFlight(_data[j], start)
      // 添加模型
      planeModel = viewer.entities.add({
        // 和时间轴关联
        availability: new Cesium.TimeIntervalCollection([
          new Cesium.TimeInterval({
            start: start,
            stop: stop,
          }),
        ]),
        position: property,
        // 根据所提供的速度计算模型的朝向
        orientation: new Cesium.VelocityOrientationProperty(property),
        // 模型数据
        model: {
          uri: '/CesiumDrone.glb',
          minimumPixelSize: 64,
          // scale: 0.1,
          // maximumScale: 0.2,
        },
        path: {
          resolution: 1,
          material: new Cesium.PolylineGlowMaterialProperty({
            glowPower: 0.1,
            color: Cesium.Color.YELLOW,
          }),
          width: 5,
        },
      })

      planeModel.position.setInterpolationOptions({
        interpolationDegree: 5,
        interpolationAlgorithm: Cesium.LagrangePolynomialApproximation,
      })
    }
  })
}
let noiseLayer
const updateHeatmap = () => {
  //axios.get(`http://127.0.0.1:8000/noise?index=${selectedRoute.value}`).then((res) => {
  axios.get(`/api/noise?index=${selectedRoute.value}`).then((res) => {
      let _data = res.data
      console.log(_data)
      initHeatMap1(_data)
    })
}

const initHeatMap1 = (_data) => {
  if (noiseLayer) {
    noiseLayer.delete()
    noiseLayer = null
  }

  const { points, minNoise, maxNoise, minLon, maxLon, minLat, maxLat } = _data

  let bounds = {
    west: minLon,
    east: maxLon,
    south: minLat,
    north: maxLat,
  }

  // init heatmap
  noiseLayer = CesiumHeatmap.create(
    viewer, // your cesium viewer
    bounds, // bounds for heatmap layer
    {
      // heatmap.js options go here
      // maxOpacity: 0.3
    }
  )

  // random example data
  let data = points

  let valueMin = minNoise * 10
  let valueMax = maxNoise * 10

  // add data to heatmap
  noiseLayer.setWGS84Data(valueMin, valueMax, data)

  // const defaultDataValue = [10, 500]
  // const defaultOpacityValue = [0.5, 1]
  // const points = []
  // fetch('/2.geojson', {
  //   method: 'GET',
  //   headers: {
  //     'Content-Type': 'application/json',
  //   },
  // }).then((response) => {
  //   response.json().then((data) => {
  //     if (data)
  //       data.features.forEach(function (feature) {
  //         const lon = feature.geometry.coordinates[0]
  //         const lat = feature.geometry.coordinates[1]
  //         points.push({
  //           x: lon,
  //           y: lat,
  //           value: 400 + 100 * Math.random(),
  //         })
  //       })

  //     console.log(points)
  // noiseLayer = new CesiumHeatmap(viewer, {
  //   // zoomToLayer: true,
  //   points,
  //   heatmapDataOptions: {
  //     max: defaultDataValue[1],
  //     min: defaultDataValue[0],
  //   },
  //   heatmapOptions: {
  //     maxOpacity: defaultOpacityValue[1],
  //     minOpacity: defaultOpacityValue[0],
  //   },
  // })
  //   })
  // })
}

/**
 * 计算飞行
 * @param source 数据坐标
 * @returns {SampledPositionProperty|*}
 */
function computeFlight(source, start) {
  // 取样位置 相当于一个集合
  let property = new Cesium.SampledPositionProperty()
  let path = source.path
  for (let i = 0; i < path.length; i++) {
    let time = Cesium.JulianDate.addSeconds(
      start,
      path[i].time,
      new Cesium.JulianDate()
    )
    let position = Cesium.Cartesian3.fromDegrees(
      path[i].longitude,
      path[i].latitude,
      path[i].height
    )
    // 添加位置，和时间对应
    property.addSample(time, position)
  }
  return property
}

let geojsonLayer
function initGeojson(item) {
  // 如果已存在图层且按钮未选中，则移除
  if (geojsonLayer && !item.selected) {
    // 通过名称获取数据源并移除
    const dataSource = viewer.dataSources.getByName(geojsonLayer.geojson)[0]
    if (dataSource) {
      viewer.dataSources.remove(dataSource)
    }
    geojsonLayer = null  // 重要：清空引用
    return
  }

  // 只有在按钮选中时才添加
  if (item.selected) {
    geojsonLayer = addGeoJsonLayer({
      url: '/poi.geojson',
      success: (dataSource) => {
        let entities = dataSource.entities.values
        entities.forEach(function (entity) {
          if (entity && entity.position) {
            entity.billboard = {
              image: 'poi.png',
              width: 32,
              height: 32,
            }
          }
        })
      },
    })
  }
}

/* 修改data未定义问题
function initGeojson() {
  if (geojsonLayer && geojsonLayer.geojson && !data.selected) { //data应改为item
    viewer.dataSources.remove(
      viewer.dataSources.getByName(geojsonLayer.geojson)[0]
    )
    return
  }

  geojsonLayer = addGeoJsonLayer({
    url: '/poi.geojson',
    success: (dataSource) => {
      let entities = dataSource.entities.values
      let positions = []
      entities.forEach(function (entity) {
        if (entity && entity.position) {
          entity.billboard = {
            image: 'poi.png',
            width: 32,
            height: 32,
          }
        }
      })
    },
  })
}
*/
let earthHeatMap
const initHeatMap = (item) => {  // 添加 item 参数
  if (earthHeatMap && !item.selected) {  // 改为 item.selected
    earthHeatMap.remove()
    earthHeatMap = null
    return
  }
  
  const defaultDataValue = [10, 500]
  const defaultOpacityValue = [0, 1]
  const points = []
  
  fetch('/poi.geojson', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => {
    response.json().then((data) => {
      if (data)
        data.features.forEach(function (feature) {
          const lon = feature.geometry.coordinates[0]
          const lat = feature.geometry.coordinates[1]
          points.push({
            x: lon,
            y: lat,
            value: 100 * Math.random(),
          })
        })
      earthHeatMap = new CesiumHeatmap(viewer, {
        zoomToLayer: true,
        points,
        heatmapDataOptions: {
          max: defaultDataValue[1],
          min: defaultDataValue[0],
        },
        heatmapOptions: {
          maxOpacity: defaultOpacityValue[1],
          minOpacity: defaultOpacityValue[0],
        },
      })
    })
  })
}
/* 修改data未定义问题
const initHeatMap = () => {
  if (earthHeatMap && !data.selected) {
    earthHeatMap.remove()
    earthHeatMap = null
    return
  }
  const defaultDataValue = [10, 500]
  const defaultOpacityValue = [0, 1]
  const points = []
  fetch('/poi.geojson', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => {
    response.json().then((data) => {
      if (data)
        data.features.forEach(function (feature) {
          const lon = feature.geometry.coordinates[0]
          const lat = feature.geometry.coordinates[1]
          points.push({
            x: lon,
            y: lat,
            value: 100 * Math.random(),
          })
        })
      earthHeatMap = new CesiumHeatmap(viewer, {
        zoomToLayer: true,
        points,
        heatmapDataOptions: {
          max: defaultDataValue[1],
          min: defaultDataValue[0],
        },
        heatmapOptions: {
          maxOpacity: defaultOpacityValue[1],
          minOpacity: defaultOpacityValue[0],
        },
      })

      // setTimeout(() => {
      //   console.log('cesiumHeatmap', cesiumHeatmap)
      //   earthHeatMap.remove()
      // }, 1000 * 5)
    })
  })
}
*/
function addGeoJsonLayer(opiton = {}) {
  if (!opiton) return false
  if (!opiton.url) throw new Error('无GeoJson文件的url')

  const _opiton = {
    base: true,
    // style: {
    //   // eslint-disable-next-line new-cap
    //   stroke: new Cesium.Color.fromCssColorString("#5D92FD"),
    //   // fill: Cesium.Color.RED,
    //   strokeWidth: 3,
    //   clampToGround: true,
    // },
  }
  // 将默认数据和传入数据进行解构组合
  opiton = { ..._opiton, ...opiton }
  //
  const promise = Cesium.GeoJsonDataSource.load(
    opiton.url,
    opiton.style || { clampToGround: true }
  )
  const name = `geojson-${new Date().getTime()}`
  promise.then((dataSource) => {
    dataSource.name = name
    dataSource.layerId = opiton.layerId
    if (opiton.success && opiton.success instanceof Function)
      opiton.success(dataSource)
  })
  viewer.dataSources.add(promise)
  return {
    geojson: name,
  }
}

let windManager = null; // 风场实例

// 新data: 参数
const windDirection = ref(0);
const windLevel = ref(5);

// 新: 初始化风场管理器 (在onMounted中调用)
onMounted(() => {
  initMap();
  initNosieList();
  
  // 插入到onMounted末尾，确保viewer已初始化
  windManager = new WindFieldManager(viewer, {
    direction: windDirection.value,
    level: windLevel.value,
  });
});

// 新方法: 切换风场 (匹配init*风格，处理selected)
const toggleWindField = (item) => {
  if (windManager) {
    if (!item.selected) {
      windManager.destroy(); // 或 windManager.toggle() 如果destroy不合适；但匹配其他层remove
    } else {
      windManager.toggle(); // 激活
    }
  }
};

// 新方法: 更新参数 (可从后端fetch后调用)
const updateWindParams = () => {
  if (windManager) {
    windManager.updateParams(windDirection.value, windLevel.value);
    // 可选: axios.post('/api/wind_params', { direction: windDirection.value, level: windLevel.value });
  }
};
</script>

<style scoped>
.map-box {
  height: 100%;
  width: 100%;
}
.NOISE-BOX {
  position: absolute;
  z-index: 99;
  top: 50px;
  left: 10px;
  color: black;
}
.btn-box {
  display: flex;
  position: absolute;
  z-index: 99;
  top: 10px;
  left: 10px;
}
.btn {
  background-color: white;
  margin-right: 10px;
  padding: 5px 10px;
  color: black;
  border-radius: 5px;
  cursor: pointer;
}

.btn-select {
  background-color: #4e6ef2;
  color: white;
}

.WIND-BOX {
  position: absolute;
  z-index: 99;
  top: 90px; /* 调整位置，避免重叠NOISE-BOX */
  left: 10px;
  color: black;
}
.select-box {
  height: 30px; /* 匹配噪声select */
  margin-left: 5px;
}
</style>
