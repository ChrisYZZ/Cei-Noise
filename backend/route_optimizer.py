import numpy as np
from typing import List, Dict, Tuple
import math

class RouteOptimizer:
    """基于论文中的航路规划理论"""
    
    def __init__(self):
        self.route_types = {
            "matrix": "矩阵节点型航路",
            "over_buildings": "建筑节点型航路", 
            "over_roads": "道路沿线型航路"
        }
    
    def generate_matrix_route(self, 
                            start: Tuple[float, float], 
                            end: Tuple[float, float],
                            grid_size: float = 0.002,  # 约200米
                            altitude: float = 120) -> List[Dict]:
        """生成矩阵节点型航路（棋盘式）"""
        path = []
        
        # 计算网格点
        lon_steps = int(abs(end[0] - start[0]) / grid_size) + 1
        lat_steps = int(abs(end[1] - start[1]) / grid_size) + 1
        
        # 生成曼哈顿式路径
        current_lon, current_lat = start
        time_counter = 0
        
        # 先沿经度方向移动
        for i in range(lon_steps):
            lon = start[0] + i * grid_size * np.sign(end[0] - start[0])
            path.append({
                "longitude": lon,
                "latitude": current_lat,
                "height": altitude,
                "time": time_counter
            })
            time_counter += 60
        
        # 再沿纬度方向移动
        for j in range(1, lat_steps):
            lat = start[1] + j * grid_size * np.sign(end[1] - start[1])
            path.append({
                "longitude": path[-1]["longitude"],  # 使用最后一个点的经度
                "latitude": lat,
                "height": altitude,
                "time": time_counter
            })
            time_counter += 60
            
        return path
    
    def validate_route_safety(self, route: List[Dict], obstacles: List[Dict] = None) -> Dict:
        """基于论文中的安全评估方法验证航路安全性"""
        if obstacles is None:
            obstacles = []
            
        safety_assessment = {
            "collision_risk": 0.0,
            "ground_risk": 0.0,
            "total_risk": 0.0,
            "safe_segments": [],
            "risk_segments": [],
            "is_safe": True
        }
        
        # 检查每个航段
        for i in range(len(route) - 1):
            segment_risk = self._calculate_segment_risk(
                route[i], route[i+1], obstacles
            )
            
            if segment_risk < 0.3:  # 安全阈值
                safety_assessment["safe_segments"].append(i)
            else:
                safety_assessment["risk_segments"].append(i)
                
            safety_assessment["collision_risk"] += segment_risk
            
        # 平均碰撞风险
        if len(route) > 1:
            safety_assessment["collision_risk"] /= (len(route) - 1)
            
        # 计算对地风险（基于论文公式）
        safety_assessment["ground_risk"] = self._calculate_ground_risk(route)
        
        # 总风险评估
        safety_assessment["total_risk"] = (
            safety_assessment["collision_risk"] * 0.6 + 
            safety_assessment["ground_risk"] * 0.4
        )
        
        # 判断是否安全
        safety_assessment["is_safe"] = safety_assessment["total_risk"] < 0.5
        
        return safety_assessment
    
    def _calculate_segment_risk(self, point1: Dict, point2: Dict, 
                               obstacles: List[Dict]) -> float:
        """计算航段碰撞风险"""
        # 简化的风险计算
        risk = 0.0
        
        # 基于高度的基础风险
        avg_height = (point1["height"] + point2["height"]) / 2
        if avg_height < 50:
            risk += 0.2  # 低空飞行风险较高
        elif avg_height < 100:
            risk += 0.1
            
        # 障碍物风险（如果有障碍物数据）
        for obstacle in obstacles:
            min_distance = self._point_to_line_distance(
                obstacle, point1, point2
            )
            if min_distance < 50:  # 50米安全距离
                risk += (50 - min_distance) / 50 * 0.5
                
        return min(risk, 1.0)
    
    def _calculate_ground_risk(self, route: List[Dict]) -> float:
        """基于论文公式计算对地风险"""
        total_risk = 0.0
        
        for point in route:
            # 基于高度的风险衰减
            height_factor = math.exp(-point["height"] / 100)
            
            # 简化的人口密度估算（实际应用中应使用真实数据）
            # 广州市中心区域人口密度较高
            if 113.32 <= point["longitude"] <= 113.33 and 23.11 <= point["latitude"] <= 23.14:
                population_density = 0.8  # 市中心
            else:
                population_density = 0.4  # 其他区域
            
            # 使用论文中的公式简化版
            point_risk = population_density * height_factor
            total_risk += point_risk
            
        return total_risk / len(route) if route else 0
    
    def _point_to_line_distance(self, point: Dict, 
                               line_start: Dict, 
                               line_end: Dict) -> float:
        """计算点到线段的最短距离（简化版）"""
        # 这里使用简化的曼哈顿距离
        # 实际应用中应该使用更精确的计算方法
        
        # 点到线段起点的距离
        dist1 = abs(point.get("longitude", 0) - line_start["longitude"]) + \
                abs(point.get("latitude", 0) - line_start["latitude"])
        
        # 点到线段终点的距离  
        dist2 = abs(point.get("longitude", 0) - line_end["longitude"]) + \
                abs(point.get("latitude", 0) - line_end["latitude"])
        
        # 返回较小值（米为单位，1度约等于111000米）
        return min(dist1, dist2) * 111000
