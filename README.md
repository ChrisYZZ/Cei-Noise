# 3D Map 项目文档

这个项目是一个基于Vue.js和Cesium的前端3D地图应用，结合了Python FastAPI后端，用于展示3D模型、飞行路线、热力图、噪声图、风场等功能。项目采用前后端分离架构，前端通过Vite构建工具管理，后端负责API服务和静态文件（如3D Tiles资源）提供。以下我将详细介绍每个部分的功能、使用方式、修改方法，以及如何连接后端和调试。

## 项目概述

- **前端**：使用Vue 3和Cesium库实现3D地图渲染。核心组件是`Map.vue`，负责加载Cesium视图、处理图层切换（如3D Tiles、POI、热力图、噪声图、风场、六边形网格）和用户交互（如OD路径规划、风场/噪声影响模拟）。`App.vue`是入口组件，包含地图视图和图例。
- **后端**：基于FastAPI的Python服务。主要处理路径规划API（`/plan_route`），并提供静态文件服务（如`/tiles`路径下的3D Tiles资源）。
- **依赖**：前端依赖Cesium、axios、turf.js等；后端依赖FastAPI、Uvicorn（用于运行服务器）。
- **数据**：项目使用GLB模型、GeoJSON文件、CZML格式的路径数据等。静态资源放在`public`和`backend/static`目录下。
- **功能**：支持动态图层切换、实时热力图渲染、风场粒子系统模拟、噪声影响可视化、自定义OD路径规划（包括风场和噪声偏移）。


## 前端部分详解

### 1. `App.vue`
   - **功能**：这是Vue应用的根组件。它导入`Map.vue`作为地图视图，并添加一个图例盒子（legend-box），用于显示噪声或热力图的颜色梯度（例如40~50 dB对应绿色）。图例是静态的，帮助用户理解颜色含义。
   - **使用方式**：无需手动调用；运行项目时自动渲染。图例固定在左下角。
   - **如何更改**：如果需要调整图例颜色或范围，修改`<style scoped>`中的`.one`、`.one1`等类（这些是颜色块的CSS）。添加新图例项时，在`<template>`中复制`<div class="legend-item">`结构，并相应添加CSS类。如果想动态生成图例，可以用Vue的`v-for`替换静态项。
   - **注意**：图例目前硬编码为噪声级别；如果用于其他图层，需要添加条件渲染（如`v-if`）。

### 2. `Map.vue`
   - **功能**：核心组件，初始化Cesium视图（在`#contanter` div中）。包括：
     - 图层切换按钮（btnList）：控制3D模型、飞行路线、POI、热力图、噪声图、风场等显示。
     - 噪声图选择：下拉菜单切换不同噪声路线热力图。
     - 风场级别选择：低/中/高风力，更新粒子系统。
     - 六边形网格选择：多选高度层（100m~400m），更新风场或噪声可视化。
     - OD路径规划：选择或输入起点/终点，调用后端API生成路径。集成风场（偏移路径）和噪声（二元选择）影响。
     - 其他：使用Cesium实体渲染路径、粒子系统模拟风场、热力图库渲染噪声/热力。
   - **使用方式**：在`App.vue`中导入`<map-view>`。运行前端后，通过按钮和下拉菜单交互。自定义OD时，输入格式为"经度,纬度"（如"113.2688,23.1091"）。
   - **如何更改**：
     - 添加新图层：在`btnList` ref中添加对象（如`{ name: '新图层', selected: false, type: 'newType' }`），然后在`changeLayer`方法中处理逻辑（例如添加/移除Cesium实体）。
     - 修改风场：调整`updateWindField`中的粒子系统参数（如emissionRate、forces函数中的速度分量）。
     - 自定义路径逻辑：在`planRoute`或`loadSelectedRoute`中修改axios调用参数，或在后端响应处理中调整CZML格式。
     - 噪声影响：在`updateNoiseForRoute`中扩展逻辑，例如基于噪声级别动态调整路径颜色或添加警报实体。
   - **注意**：Cesium需要Ion token（已硬编码）；热力图使用`CesiumHeatmap.js`库。如果文件被截断（如truncated characters），检查完整代码确保ref声明完整。

### 3. `main.js`
   - **功能**：Vue应用启动脚本。导入`App.vue`并挂载到`#app`。
   - **使用方式**：自动运行，无需干预。
   - **如何更改**：如果添加全局插件或store，在这里导入并使用`app.use()`。例如集成Vue Router时添加`app.use(router)`。

### 4. `index.html`
   - **功能**：HTML入口模板。加载Cesium CSS/JS、热力图库，并定义`#app` div。
   - **使用方式**：Vite自动处理。
   - **如何更改**：如果更换Cesium版本，更新`<link>`和`<script>`路径。添加自定义样式时，在`<style>`中写入。

### 5. `style.css`
   - **功能**：全局CSS，重置根元素样式，确保全屏地图。
   - **使用方式**：自动应用。
   - **如何更改**：调整字体、颜色方案。如果需要主题切换，添加CSS变量（如`--bg-color`）并在组件中使用。

### 6. `vite.config.js`
   - **功能**：Vite构建配置。启用Vue插件，并设置代理（`/tiles`代理到后端，如`https://noise-map.com`，但注释中提到`http://localhost:3737`）。
   - **使用方式**：运行`npm run dev`时生效。
   - **如何更改**：代理目标改为后端URL（如`target: 'http://localhost:8000'`）。添加更多代理规则时，扩展`proxy`对象。

### 7. `package.json` 和 `package-lock.json`
   - **功能**：定义依赖（如Vue、axios、Cesium-heatmap）和脚本（如`dev`、`build`）。
   - **使用方式**：安装依赖用`npm install`；运行用`npm run dev`。
   - **如何更改**：添加新包时，用`npm install <package>`更新；修改脚本以自定义构建命令。

## 后端部分详解

### 1. `main.py`
   - **功能**：FastAPI主应用。添加CORS支持（允许前端跨域），定义根端点（`/`），并挂载静态文件（如`/tiles`从`static/tiles`提供）。
   - **使用方式**：运行`uvicorn main:app --reload`（需安装Uvicorn）。访问`http://localhost:8000/`测试。
   - **如何更改**：切换静态目录时，修改`app.mount("/tiles", StaticFiles(directory="static/tiles"))`。添加新路由时，用`app.include_router()`导入其他py文件。
   - **注意**：生产环境限制CORS origins；注释中有一个未启用的optimized_tiles挂载。

### 2. `plan_route.py`
   - **功能**：路径规划路由（`/plan_route` POST）。接收OD坐标，计算简单直线路径，生成CZML格式（用于Cesium动态实体，如无人机模型和路径）。未来可集成风场/噪声逻辑。
   - **使用方式**：前端通过axios POST发送`{origin: "lon,lat", destination: "lon,lat"}`。返回CZML JSON。
   - **如何更改**：复杂路径计算时，导入geopy或numpy调整距离/偏移。添加风场影响：在路径生成循环中加入速度矢量偏移。噪声集成：查询噪声数据调整高度或路径。
   - **注意**：当前是匀速直线；飞行时间至少30秒。

## 如何安装和运行

1. **前端**：
   - 安装依赖：`npm install`
   - 运行开发服务器：`npm run dev`（默认http://localhost:5173）
   - 构建生产包：`npm run build`

2. **后端**：
   - 创建虚拟环境：`python -m venv venv` 并激活。
   - 安装依赖：`pip install fastapi uvicorn pydantic`
   - 运行服务器：`uvicorn backend.main:app --reload --port 8000`

3. **完整运行**：先启动后端，再启动前端。确保静态资源（如GLB文件）放在`backend/static/tiles`。

## 如何连通后端

- **代理配置**：在`vite.config.js`中，`/tiles`代理到后端URL。前端axios调用时，用相对路径如`/plan_route`（Vite会代理）。
- **直接调用**：在`Map.vue`的axios中，设置`baseURL: 'http://localhost:8000'`。如果跨域问题，检查后端CORS。
- **测试连通**：用Postman发送POST到`/plan_route`，验证CZML返回。然后在前端控制台日志axios响应。

## 如何调试

- **前端调试**：
  - 用Chrome DevTools：检查Vue组件状态（安装Vue Devtools扩展）。在`Map.vue`的methods中添加`console.log`追踪变量（如`originalPositions`）。
  - Cesium问题：启用`viewer.scene.debugShowFramesPerSecond = true`显示FPS；用`Cesium.Inspector`插件调试实体。
  - 热力图/粒子：如果不渲染，检查库导入和数据范围（e.g., heatmap bounds）。

- **后端调试**：
  - 用`print`语句或logging模块输出变量（如路径positions）。
  - FastAPI自带Swagger UI：访问`http://localhost:8000/docs`测试API。
  - 错误处理：捕获异常，提高HTTPException detail。

- **前后端联合调试**：
  - 监控网络请求：DevTools Network tab查看axios调用和响应。
  - 如果路径不渲染，检查CZML格式（用JSON.stringify日志）。
  - 性能问题：风场粒子过多时，降低emissionRate；大文件加载用浏览器缓存检查。

如果有特定问题，欢迎在Issue中描述，我会进一步优化代码。
