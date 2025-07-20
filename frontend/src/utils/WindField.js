// src/utils/WindField.js
// 模块化风场管理器，使用Cesium ParticleSystem模拟简单风流动画。
// 可调整参数：windDirection (角度，0=北，90=东)，windLevel (速度等级，1-10，影响粒子速度)。
// 优先简单均匀风场，无需精细数据。updateCallback应用风力向量。
// 依赖：Cesium已导入（项目中已有）。

import * as Cesium from 'cesium'; // 假设项目main.js已全局导入Cesium，或在此导入

export class WindFieldManager {
  constructor(viewer, options = {}) {
    this.viewer = viewer; // Cesium Viewer实例
    this.particleSystem = null; // 粒子系统实例
    this.isActive = false; // 是否激活
    this.windDirection = options.direction || 0; // 默认北风 (度)
    this.windLevel = options.level || 5; // 默认中级风速 (1-10)
    this.particleCount = options.count || 2000; // 粒子数，平衡性能
    this.emitterBounds = options.bounds || this.getDefaultBounds(); // 发射范围，默认全球简化
  }

  // 获取默认发射范围（简化到可见区域，可基于项目城市边界调整）
  getDefaultBounds() {
    return new Cesium.Rectangle.fromDegrees(-180, -90, 180, 90); // 全球，或调整为GZ城市边界
  }

  // 创建粒子系统
  createParticleSystem() {
    if (this.particleSystem) return; // 避免重复创建

    const windForce = this.windLevel * 0.1; // 速度缩放，等级转实际速度 (可调)

    this.particleSystem = new Cesium.ParticleSystem({
      image: '/wind_particle.png', // 需添加纹理文件（简单白线或箭头，public文件夹）
      startColor: Cesium.Color.WHITE.withAlpha(0.7), // 开始颜色
      endColor: Cesium.Color.WHITE.withAlpha(0.0), // 渐隐结束
      startScale: 1.0, // 开始大小
      endScale: 2.0, // 结束大小（膨胀效果）
      particleLife: 5.0, // 粒子寿命 (秒)
      speed: 1.0, // 基础速度
      imageSize: new Cesium.Cartesian2(5, 5), // 粒子像素大小
      emissionRate: this.particleCount / 10, // 每秒发射率
      lifetime: Infinity, // 系统无限循环
      emitter: new Cesium.BoxEmitter(new Cesium.Cartesian3(1000000, 1000000, 1000000)), // 大盒子发射，覆盖地图
      // emitter: new Cesium.RectangleEmitter(this.emitterBounds), // 备选：矩形发射
      updateCallback: (particle, dt) => this.applyWindForce(particle, dt, windForce),
    });

    this.viewer.scene.primitives.add(this.particleSystem);
    this.particleSystem.show = false; // 初始隐藏
  }

  // updateCallback: 应用风力（简单向量计算，可解释）
  applyWindForce(particle, dt, windForce) {
    // 计算风向向量 (x=东, y=北, 简化2D)
    const directionRad = Cesium.Math.toRadians(this.windDirection);
    const windVector = new Cesium.Cartesian3(
      Math.sin(directionRad) * windForce, // 东向分量
      Math.cos(directionRad) * windForce, // 北向分量 
      0 // 无垂直风
    );

    // 更新粒子速度 (累加风力 * 时间步)
    Cesium.Cartesian3.add(particle.velocity, Cesium.Cartesian3.multiplyByScalar(windVector, dt, windVector), particle.velocity);
  }

  // 切换激活状态 (按钮调用)
  toggle() {
    if (!this.particleSystem) this.createParticleSystem();
    this.isActive = !this.isActive;
    this.particleSystem.show = this.isActive;
  }

  // 更新参数 (后端API调用后设置，或前端输入)
  updateParams(direction, level) {
    this.windDirection = direction;
    this.windLevel = level;
    // 无需重启系统，updateCallback会实时应用新参数
  }

  // 销毁 (清理)
  destroy() {
    if (this.particleSystem) {
      this.viewer.scene.primitives.remove(this.particleSystem);
      this.particleSystem = null;
    }
  }
}

// 使用示例：在Map.vue中实例化
// const windManager = new WindFieldManager(viewer);
// windManager.toggle();
