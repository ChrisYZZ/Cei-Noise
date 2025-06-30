python

复制
# airspace_capacity_analyzer.py
from typing import Dict, List
import math

class AirspaceCapacityAnalyzer:
    """空域容量分析器"""
    
    def __init__(self):
        # 中国低空空域定义
        self.AIRSPACE_LAYERS = {
            "ultra_low": {"floor": 0, "ceiling": 120, "name": "超低空"},
            "low_low": {"floor": 120, "ceiling": 300, "name": "低空下层"},
            "low_mid": {"floor": 300, "ceiling": 600, "name": "低空中层"},
            "low_high": {"floor": 600, "ceiling": 1000, "name": "低空上层"}
        }
        
        # 安全间隔标准
        self.SEPARATION_STANDARDS = {
            "VFR": {"longitudinal": 100, "lateral": 50, "vertical": 30},
            "IFR": {"longitudinal": 200, "lateral": 100, "vertical": 50}
        }
        
    def calculate_capacity(self, airspace_params: Dict) -> Dict:
        """计算空域容量"""
        length = airspace_params.get('length', 10000)  # 默认10km
        width = airspace_params.get('width', 2000)     # 默认2km
        height_range = airspace_params.get('height_range', (120, 300))  # 默认高度层
        flight_rules = airspace_params.get('flight_rules', 'VFR')
        
        # 获取间隔标准
        separation = self.SEPARATION_STANDARDS[flight_rules]
        
        # 1. 计算物理容量
        physical_capacity = self._calculate_physical_capacity(
            length, width, height_range, separation
        )
        
        # 2. 计算运行容量（考虑实际约束）
        operational_capacity = self._calculate_operational_capacity(
            physical_capacity, airspace_params
        )
        
        # 3. 计算动态容量（考虑流量）
        dynamic_capacity = self._calculate_dynamic_capacity(
            operational_capacity, length, airspace_params.get('avg_speed', 50)
        )
        
        return {
            "physical_capacity": physical_capacity,
            "operational_capacity": operational_capacity,
            "dynamic_capacity": dynamic_capacity,
            "utilization_factors": self._get_utilization_factors(airspace_params),
            "recommendations": self._generate_recommendations(dynamic_capacity)
        }
    
    def _calculate_physical_capacity(self, length: float, width: float, 
                                   height_range: Tuple[float, float], 
                                   separation: Dict) -> Dict:
        """计算物理容量"""
        # 纵向容量
        aircraft_length = 10  # 假设无人机长度10米
        longitudinal_capacity = int(length / (separation['longitudinal'] + aircraft_length))
        
        # 横向容量
        lateral_capacity = max(1, int(width / separation['lateral']))
        
        # 垂直容量
        height_diff = height_range[1] - height_range[0]
        vertical_capacity = max(1, int(height_diff / separation['vertical']))
        
        # 总容量
        total_capacity = longitudinal_capacity * lateral_capacity * vertical_capacity
        
        return {
            "total": total_capacity,
            "longitudinal": longitudinal_capacity,
            "lateral": lateral_capacity,
            "vertical": vertical_capacity,
            "dimensions": {
                "length": length,
                "width": width,
                "height": height_diff
            }
        }
    
    def _calculate_operational_capacity(self, physical_capacity: Dict, 
                                      params: Dict) -> Dict:
        """计算运行容量"""
        # 基础容量
        base_capacity = physical_capacity['total']
        
        # 应用各种约束因子
        controller_factor = params.get('controller_workload_factor', 0.7)
        weather_factor = params.get('weather_factor', 0.85)
        equipment_factor = params.get('equipment_factor', 0.9)
        
        # 运行容量
        operational = int(base_capacity * controller_factor * weather_factor * equipment_factor)
        
        return {
            "capacity": operational,
            "reduction_rate": 1 - (operational / base_capacity),
            "limiting_factors": {
                "controller_workload": controller_factor,
                "weather": weather_factor,
                "equipment": equipment_factor
            }
        }
    
    def _calculate_dynamic_capacity(self, operational_capacity: Dict, 
                                  route_length: float, avg_speed: float) -> Dict:
        """计算动态容量（流量）"""
        capacity = operational_capacity['capacity']
        
        # 飞行时间（小时）
        flight_time = (route_length / 1000) / avg_speed
        
        # 小时流量
        hourly_flow = int(capacity / flight_time) if flight_time > 0 else 0
        
        # 15分钟流量（用于短期调度）
        quarter_flow = int(hourly_flow / 4)
        
        return {
            "hourly_flow": hourly_flow,
            "quarter_flow": quarter_flow,
            "avg_separation_time": (3600 / hourly_flow) if hourly_flow > 0 else 0,
            "flight_time_minutes": flight_time * 60
        }
    
    def analyze_layer_capacity(self, layer_name: str, area_params: Dict) -> Dict:
        """分析特定高度层的容量"""
        if layer_name not in self.AIRSPACE_LAYERS:
            return {"error": "Invalid layer name"}
            
        layer = self.AIRSPACE_LAYERS[layer_name]
        
        # 设置该层的参数
        params = area_params.copy()
        params['height_range'] = (layer['floor'], layer['ceiling'])
        
        # 计算容量
        capacity = self.calculate_capacity(params)
        
        # 添加层特定信息
        capacity['layer_info'] = {
            "name": layer['name'],
            "altitude_range": f"{layer['floor']}-{layer['ceiling']}m",
            "typical_operations": self._get_layer_operations(layer_name)
        }
        
        return capacity
    
    def _get_layer_operations(self, layer_name: str) -> List[str]:
        """获取高度层典型运行类型"""
        operations = {
            "ultra_low": ["设施巡检", "航拍摄影", "农业植保"],
            "low_low": ["物流配送", "应急救援", "城市监测"],
            "low_mid": ["区域运输", "客运飞行", "测绘作业"],
            "low_high": ["城际运输", "通用航空", "科研飞行"]
        }
        return operations.get(layer_name, [])
    
    def _get_utilization_factors(self, params: Dict) -> Dict:
        """获取利用率因子"""
        return {
            "time_of_day": self._get_time_factor(params.get('hour', 12)),
            "day_of_week": self._get_day_factor(params.get('weekday', 3)),
            "season": self._get_season_factor(params.get('month', 6)),
            "demand_level": params.get('demand_level', 0.6)
        }
    
    def _get_time_factor(self, hour: int) -> float:
        """根据时间获取利用率因子"""
        # 高峰时段
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 0.9
        # 日间
        elif 9 <= hour <= 17:
            return 0.7
        # 夜间
        else:
            return 0.3
            
    def _get_day_factor(self, weekday: int) -> float:
        """根据星期获取利用率因子"""
        # 周一到周五
        if weekday < 5:
            return 0.8
        # 周末
        else:
            return 0.5
            
    def _get_season_factor(self, month: int) -> float:
        """根据季节获取利用率因子"""
        # 春秋季
        if month in [3, 4, 5, 9, 10, 11]:
            return 0.9
        # 夏季
        elif month in [6, 7, 8]:
            return 0.8
        # 冬季
        else:
            return 0.7
    
    def _generate_recommendations(self, dynamic_capacity: Dict) -> List[str]:
        """生成容量优化建议"""
        recommendations = []
        
        if dynamic_capacity['hourly_flow'] < 20:
            recommendations.append("当前容量较低，建议优化空域结构或放宽间隔标准")
        
        if dynamic_capacity['avg_separation_time'] < 60:
            recommendations.append("平均间隔时间较短，建议加强冲突监测")
            
        if dynamic_capacity['flight_time_minutes'] > 30:
            recommendations.append("航路较长，建议设置中间监控点")
            
        return recommendations