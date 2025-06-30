from typing import List, Dict
import numpy as np
import math  

class AirspaceCapacityAnalyzer:
    """基于论文的空域容量分析"""
    
    def __init__(self):
        self.safety_separation = 50  # 米
        self.max_density = 10  # 架/平方公里
        
    def calculate_route_capacity(self, route: List[Dict], 
                                route_width: float = 100) -> Dict:
        """计算航路容量"""
        
        # 计算航路长度
        total_length = self._calculate_route_length(route)
        
        # 基于论文中的容量定义
        capacity_metrics = {
            "max_aircraft_count": 0,
            "throughput_per_hour": 0,
            "density_limit": 0,
            "safety_factor": 0.8,
            "route_length_km": total_length / 1000
        }
        
        # 最大航空器数量 = 航路长度 / (安全间隔 + 航空器长度)
        aircraft_length = 10  # 假设无人机长度10米
        if total_length > 0:
            capacity_metrics["max_aircraft_count"] = int(
                total_length / (self.safety_separation + aircraft_length)
            )
        
        # 小时吞吐量（基于平均速度）
        avg_speed = 50  # km/h
        if total_length > 0:
            travel_time = (total_length / 1000) / avg_speed  # 小时
            if travel_time > 0:
                capacity_metrics["throughput_per_hour"] = int(
                    capacity_metrics["max_aircraft_count"] / travel_time
                )
        
        # 密度限制（每平方公里最大架数）
        route_area = (total_length / 1000) * (route_width / 1000)  # 平方公里
        if route_area > 0:
            capacity_metrics["density_limit"] = int(
                self.max_density * route_area
            )
        
        return capacity_metrics
    
    def analyze_conflict_probability(self, 
                                   routes: List[List[Dict]], 
                                   traffic_density: float) -> float:
        """分析冲突概率（基于论文中的NTSC指标）"""
        
        # 找出所有交叉点
        intersections = self._find_route_intersections(routes)
        
        # 基于交叉点数量和流量密度计算冲突概率
        base_conflict_rate = len(intersections) * 0.01
        density_factor = min(traffic_density / self.max_density, 1.0)
        
        # NTSC = 冲突时间 / 总飞行时间
        conflict_probability = min(
            base_conflict_rate * density_factor, 
            1.0
        )
        
        return conflict_probability
    
    def _calculate_route_length(self, route: List[Dict]) -> float:
        """计算航路总长度（米）"""
        total_length = 0.0
        
        for i in range(len(route) - 1):
            # 使用Haversine公式计算距离
            lat1, lon1 = route[i]["latitude"], route[i]["longitude"]
            lat2, lon2 = route[i+1]["latitude"], route[i+1]["longitude"]
            
            distance = self._haversine_distance(lat1, lon1, lat2, lon2)
            total_length += distance
            
        return total_length
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """计算两点间距离（米）"""
        R = 6371000  # 地球半径（米）
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _find_route_intersections(self, routes: List[List[Dict]]) -> List[Dict]:
        """找出航路交叉点（简化版）"""
        intersections = []
        
        # 简化处理：检查航路点是否接近
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                for point1 in routes[i]:
                    for point2 in routes[j]:
                        # 如果两点距离小于100米，认为是交叉点
                        distance = self._haversine_distance(
                            point1["latitude"], point1["longitude"],
                            point2["latitude"], point2["longitude"]
                        )
                        if distance < 100:
                            intersections.append({
                                "route1": i,
                                "route2": j,
                                "location": {
                                    "longitude": (point1["longitude"] + point2["longitude"]) / 2,
                                    "latitude": (point1["latitude"] + point2["latitude"]) / 2
                                }
                            })
        
        return intersections
