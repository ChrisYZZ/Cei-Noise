# enhanced_route_analyzer_fixed.py
"""
修复后的航路分析系统
"""

import numpy as np
from typing import List, Dict, Tuple
import math
import matplotlib.pyplot as plt
import matplotlib
# 解决中文显示问题
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

from datetime import datetime, timedelta

class EnhancedRouteAnalyzer:
    """
    基于《城市低空航路规划研究综述》的航路分析系统
    """
    
    def __init__(self):
        # 基于论文第3.5节的参数设置
        self.REFERENCE_DISTANCE = 1  # 1米参考距离
        self.SAFETY_SEPARATION = 50  # 50米安全间隔
        self.GROUND_EFFECT_THRESHOLD = 100  # 100米以下考虑地面效应
        
    def calculate_collision_risk(self, point1: Dict, point2: Dict, 
                                obstacles: List[Dict]) -> Dict:
        """
        计算航段碰撞风险
        对应论文第3.5节公式(11)：NTSC = 冲突飞行时间 / 总飞行时间
        """
        
        # 1. 基于高度的基础风险（论文提到低空飞行风险较高）
        avg_height = (point1["height"] + point2["height"]) / 2
        height_risk = 0.0
        
        if avg_height < 50:  # 极低空
            height_risk = 0.3
        elif avg_height < 100:  # 低空
            height_risk = 0.2
        elif avg_height < 150:  # 中低空
            height_risk = 0.1
        else:  # 相对安全高度
            height_risk = 0.05
            
        # 2. 水平碰撞风险（基于航段长度和密度）
        segment_length = self._haversine_distance(
            point1["latitude"], point1["longitude"],
            point2["latitude"], point2["longitude"]
        )
        
        # 航段越长，潜在碰撞风险越高
        length_risk = min(segment_length / 5000, 0.3)  # 5km以上风险达到最大
        
        # 3. 障碍物风险
        obstacle_risk = 0.0
        for obstacle in obstacles:
            distance = self._point_to_line_distance(obstacle, point1, point2)
            if distance < self.SAFETY_SEPARATION:
                # 距离越近，风险越高
                obstacle_risk += (1 - distance / self.SAFETY_SEPARATION) * 0.2
                
        # 4. 总风险计算
        total_risk = height_risk * 0.4 + length_risk * 0.3 + obstacle_risk * 0.3
        
        return {
            "total_risk": min(total_risk, 1.0),
            "height_risk": height_risk,
            "length_risk": length_risk,
            "obstacle_risk": min(obstacle_risk, 1.0),
            "risk_level": self._get_risk_level(total_risk)
        }
    
    def calculate_ground_impact_risk(self, drone_position: Dict, 
                                   population_density: float = 0.5) -> Dict:
        """
        计算对地风险
        对应论文第3.5节公式(12)和(13)：
        P_impact(x,y) = ρ(x,y) · A_exp
        A_exp(θ) = 2(r_p + r_uav) * h_p/tanθ + π(r_uav + r_p)²
        """
        
        # 参数设置（基于论文）
        r_p = 0.5  # 人的平均半径（米）
        r_uav = 2  # 无人机半径（米）
        h_p = 1.7  # 人的平均高度（米）
        
        # 计算撞击角度（简化为基于高度的角度）
        theta = math.atan2(drone_position["height"], 100)  # 假设100米水平距离
        
        # 计算暴露面积 A_exp
        if theta > 0:
            A_exp = 2 * (r_p + r_uav) * h_p / math.tan(theta) + \
                    math.pi * (r_uav + r_p) ** 2
        else:
            A_exp = math.pi * (r_uav + r_p) ** 2
            
        # 地面撞击概率
        P_impact = population_density * A_exp / 1000  # 归一化
        
        # 考虑高度衰减
        height_attenuation = math.exp(-drone_position["height"] / 100)
        
        # 地面效应（论文提到低空飞行时增强）
        if drone_position["height"] < self.GROUND_EFFECT_THRESHOLD:
            ground_effect = 3 * (1 - drone_position["height"] / self.GROUND_EFFECT_THRESHOLD)
        else:
            ground_effect = 0
            
        # 最终风险 - 修复拼写错误
        final_risk = P_impact * height_attenuation * (1 + ground_effect / 10)
        
        return {
            "impact_probability": P_impact,
            "exposure_area": A_exp,
            "height_factor": height_attenuation,
            "ground_effect": ground_effect,
            "total_ground_risk": min(final_risk, 1.0)
        }
    
    def analyze_route_conflicts(self, routes: List[Dict]) -> Dict:
        """
        分析多条航路之间的冲突
        基于论文第3.2节的空域结构分析
        """
        conflicts = []
        
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                route1 = routes[i]["path"]
                route2 = routes[j]["path"]
                
                # 检查时空冲突
                for k1, point1 in enumerate(route1):
                    for k2, point2 in enumerate(route2):
                        # 检查是否在相同时间窗口
                        time_diff = abs(point1["time"] - point2["time"])
                        
                        if time_diff < 60:  # 60秒内认为是同一时间窗口
                            # 计算空间距离
                            horizontal_distance = self._haversine_distance(
                                point1["latitude"], point1["longitude"],
                                point2["latitude"], point2["longitude"]
                            )
                            
                            vertical_distance = abs(point1["height"] - point2["height"])
                            
                            # 3D距离
                            total_distance = math.sqrt(
                                horizontal_distance**2 + vertical_distance**2
                            )
                            
                            # 如果距离小于安全间隔，记录冲突
                            if total_distance < self.SAFETY_SEPARATION:
                                conflicts.append({
                                    "route1": routes[i]["name"],
                                    "route2": routes[j]["name"],
                                    "point1_index": k1,
                                    "point2_index": k2,
                                    "time": point1["time"],
                                    "distance": total_distance,
                                    "location": {
                                        "longitude": (point1["longitude"] + point2["longitude"]) / 2,
                                        "latitude": (point1["latitude"] + point2["latitude"]) / 2,
                                        "height": (point1["height"] + point2["height"]) / 2
                                    },
                                    "severity": self._calculate_conflict_severity(
                                        total_distance, time_diff
                                    )
                                })
        
        return {
            "total_conflicts": len(conflicts),
            "conflicts": conflicts,
            "risk_assessment": self._assess_overall_risk(conflicts)
        }
    
    def _calculate_conflict_severity(self, distance: float, time_diff: float) -> str:
        """计算冲突严重程度"""
        if distance < 20 and time_diff < 10:
            return "CRITICAL"
        elif distance < 30 and time_diff < 30:
            return "HIGH"
        elif distance < 40 and time_diff < 45:
            return "MEDIUM"
        else:
            return "LOW"
            
    def _assess_overall_risk(self, conflicts: List[Dict]) -> Dict:
        """评估整体风险水平"""
        if not conflicts:
            return {"level": "SAFE", "score": 0}
            
        critical_count = sum(1 for c in conflicts if c["severity"] == "CRITICAL")
        high_count = sum(1 for c in conflicts if c["severity"] == "HIGH")
        
        risk_score = critical_count * 10 + high_count * 5 + len(conflicts)
        
        if risk_score > 50:
            level = "UNACCEPTABLE"
        elif risk_score > 30:
            level = "HIGH"
        elif risk_score > 10:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        return {
            "level": level,
            "score": risk_score,
            "critical_conflicts": critical_count,
            "high_conflicts": high_count
        }
    
    def _get_risk_level(self, risk_value: float) -> str:
        """获取风险等级"""
        if risk_value > 0.7:
            return "HIGH"
        elif risk_value > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Haversine公式计算距离"""
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _point_to_line_distance(self, point: Dict, line_start: Dict, 
                               line_end: Dict) -> float:
        """计算点到线段的距离"""
        # 简化计算
        dist_to_start = self._haversine_distance(
            point.get("latitude", 0), point.get("longitude", 0),
            line_start["latitude"], line_start["longitude"]
        )
        
        dist_to_end = self._haversine_distance(
            point.get("latitude", 0), point.get("longitude", 0),
            line_end["latitude"], line_end["longitude"]
        )
        
        return min(dist_to_start, dist_to_end)


# 测试用例：设计有冲突隐患的航线
class ConflictTestScenarios:
    """包含多种冲突场景的测试用例"""
    
    @staticmethod
    def get_crossing_routes():
        """获取交叉航线（高冲突风险）"""
        return [
            {
                "name": "Route-EW-A",  # 使用英文避免字体问题
                "description": "East-West route through city center",
                "path": [
                    {"longitude": 113.30, "latitude": 23.12, "height": 120, "time": 0},
                    {"longitude": 113.31, "latitude": 23.12, "height": 120, "time": 30},
                    {"longitude": 113.32, "latitude": 23.12, "height": 120, "time": 60},
                    {"longitude": 113.33, "latitude": 23.12, "height": 120, "time": 90},
                    {"longitude": 113.34, "latitude": 23.12, "height": 120, "time": 120}
                ]
            },
            {
                "name": "Route-NS-B",
                "description": "North-South route through city center",
                "path": [
                    {"longitude": 113.32, "latitude": 23.10, "height": 120, "time": 0},
                    {"longitude": 113.32, "latitude": 23.11, "height": 120, "time": 30},
                    {"longitude": 113.32, "latitude": 23.12, "height": 120, "time": 60},  # 冲突点
                    {"longitude": 113.32, "latitude": 23.13, "height": 120, "time": 90},
                    {"longitude": 113.32, "latitude": 23.14, "height": 120, "time": 120}
                ]
            }
        ]
    
    @staticmethod
    def get_parallel_routes():
        """获取平行航线（低冲突风险）"""
        return [
            {
                "name": "North-Corridor",
                "description": "Flying along northern area",
                "path": [
                    {"longitude": 113.30, "latitude": 23.14, "height": 150, "time": 0},
                    {"longitude": 113.31, "latitude": 23.14, "height": 150, "time": 60},
                    {"longitude": 113.32, "latitude": 23.14, "height": 150, "time": 120},
                    {"longitude": 113.33, "latitude": 23.14, "height": 150, "time": 180}
                ]
            },
            {
                "name": "South-Corridor",
                "description": "Flying along southern area",
                "path": [
                    {"longitude": 113.30, "latitude": 23.10, "height": 150, "time": 0},
                    {"longitude": 113.31, "latitude": 23.10, "height": 150, "time": 60},
                    {"longitude": 113.32, "latitude": 23.10, "height": 150, "time": 120},
                    {"longitude": 113.33, "latitude": 23.10, "height": 150, "time": 180}
                ]
            }
        ]
    
    @staticmethod
    def get_vertical_conflict_routes():
        """获取垂直冲突航线（不同高度层）"""
        return [
            {
                "name": "Low-Alt-Route",
                "description": "Flying at 80m altitude",
                "path": [
                    {"longitude": 113.32, "latitude": 23.11, "height": 80, "time": 0},
                    {"longitude": 113.32, "latitude": 23.12, "height": 80, "time": 60},
                    {"longitude": 113.32, "latitude": 23.13, "height": 80, "time": 120}
                ]
            },
            {
                "name": "High-Alt-Route",
                "description": "Flying at 150m altitude",
                "path": [
                    {"longitude": 113.32, "latitude": 23.11, "height": 150, "time": 30},
                    {"longitude": 113.32, "latitude": 23.12, "height": 150, "time": 90},
                    {"longitude": 113.32, "latitude": 23.13, "height": 150, "time": 150}
                ]
            }
        ]
    
    @staticmethod
    def get_complex_scenario():
        """获取复杂场景（多条航线，多种冲突）"""
        return [
            {
                "name": "Logistics-Main-1",
                "description": "Connecting logistics center to downtown",
                "path": [
                    {"longitude": 113.28, "latitude": 23.10, "height": 120, "time": 0},
                    {"longitude": 113.30, "latitude": 23.11, "height": 120, "time": 60},
                    {"longitude": 113.32, "latitude": 23.12, "height": 120, "time": 120},
                    {"longitude": 113.34, "latitude": 23.13, "height": 120, "time": 180}
                ]
            },
            {
                "name": "Medical-Emergency",
                "description": "Emergency transport between hospitals",
                "path": [
                    {"longitude": 113.30, "latitude": 23.13, "height": 100, "time": 30},
                    {"longitude": 113.31, "latitude": 23.12, "height": 100, "time": 90},
                    {"longitude": 113.32, "latitude": 23.11, "height": 100, "time": 150},
                    {"longitude": 113.33, "latitude": 23.10, "height": 100, "time": 210}
                ]
            },
            {
                "name": "Inspection-Loop",
                "description": "City facility inspection",
                "path": [
                    {"longitude": 113.31, "latitude": 23.11, "height": 80, "time": 0},
                    {"longitude": 113.33, "latitude": 23.11, "height": 80, "time": 60},
                    {"longitude": 113.33, "latitude": 23.13, "height": 80, "time": 120},
                    {"longitude": 113.31, "latitude": 23.13, "height": 80, "time": 180},
                    {"longitude": 113.31, "latitude": 23.11, "height": 80, "time": 240}
                ]
            }
        ]
    
    @staticmethod
    def get_high_conflict_scenario():
        """获取高冲突场景，用于测试冲突检测能力"""
        return [
            {
                "name": "Rush-Hour-1",
                "description": "Morning rush hour delivery",
                "path": [
                    {"longitude": 113.30, "latitude": 23.11, "height": 100, "time": 0},
                    {"longitude": 113.31, "latitude": 23.11, "height": 100, "time": 20},
                    {"longitude": 113.32, "latitude": 23.11, "height": 100, "time": 40},
                    {"longitude": 113.33, "latitude": 23.11, "height": 100, "time": 60}
                ]
            },
            {
                "name": "Rush-Hour-2",
                "description": "Crossing morning delivery",
                "path": [
                    {"longitude": 113.31, "latitude": 23.10, "height": 100, "time": 10},
                    {"longitude": 113.31, "latitude": 23.11, "height": 100, "time": 30},  # 近距离冲突
                    {"longitude": 113.31, "latitude": 23.12, "height": 100, "time": 50},
                    {"longitude": 113.31, "latitude": 23.13, "height": 100, "time": 70}
                ]
            },
            {
                "name": "Rush-Hour-3",
                "description": "Another crossing route",
                "path": [
                    {"longitude": 113.32, "latitude": 23.10, "height": 105, "time": 20},
                    {"longitude": 113.32, "latitude": 23.11, "height": 105, "time": 40},  # 垂直接近
                    {"longitude": 113.32, "latitude": 23.12, "height": 105, "time": 60},
                    {"longitude": 113.32, "latitude": 23.13, "height": 105, "time": 80}
                ]
            }
        ]


# 可视化工具
class RouteVisualizer:
    """航路可视化工具"""
    
    @staticmethod
    def plot_routes_with_conflicts(routes: List[Dict], conflicts: List[Dict]):
        """绘制航路和冲突点"""
        plt.figure(figsize=(12, 10))
        
        # 绘制航路
        colors = ['blue', 'green', 'red', 'orange', 'purple']
        for i, route in enumerate(routes):
            lons = [p["longitude"] for p in route["path"]]
            lats = [p["latitude"] for p in route["path"]]
            plt.plot(lons, lats, 'o-', color=colors[i % len(colors)], 
                    label=route["name"], markersize=6)
            
            # 标注航路点的时间
            for j, point in enumerate(route["path"]):
                plt.annotate(f't={point["time"]}s', 
                           (point["longitude"], point["latitude"]),
                           fontsize=8, ha='right')
        
        # 绘制冲突点
        if conflicts:
            conflict_lons = [c["location"]["longitude"] for c in conflicts]
            conflict_lats = [c["location"]["latitude"] for c in conflicts]
            plt.scatter(conflict_lons, conflict_lats, c='red', s=200, 
                       marker='X', label='Conflict Points', zorder=5)
            
            # 标注冲突严重程度
            for conflict in conflicts:
                plt.annotate(f'{conflict["severity"]}\n{conflict["distance"]:.1f}m', 
                           (conflict["location"]["longitude"], 
                            conflict["location"]["latitude"]),
                           fontsize=10, ha='center', va='bottom',
                           bbox=dict(boxstyle="round,pad=0.3", 
                                   facecolor="yellow", alpha=0.7))
        
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Route Conflict Analysis')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('route_conflicts.png', dpi=300, bbox_inches='tight')
        print("Route conflict visualization saved as 'route_conflicts.png'")
        plt.close()
    
    @staticmethod
    def plot_3d_routes(routes: List[Dict]):
        """3D航路可视化"""
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        colors = ['blue', 'green', 'red', 'orange', 'purple']
        
        for i, route in enumerate(routes):
            lons = [p["longitude"] for p in route["path"]]
            lats = [p["latitude"] for p in route["path"]]
            heights = [p["height"] for p in route["path"]]
            
            ax.plot(lons, lats, heights, 'o-', color=colors[i % len(colors)], 
                   label=route["name"], markersize=6)
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Height (m)')
        ax.set_title('3D Route View')
        ax.legend()
        plt.savefig('route_3d.png', dpi=300, bbox_inches='tight')
        print("3D route visualization saved as 'route_3d.png'")
        plt.close()


# 增强的测试用例
if __name__ == "__main__":
    analyzer = EnhancedRouteAnalyzer()
    scenarios = ConflictTestScenarios()
    
    # 测试1：交叉航线冲突分析
    print("\n=== Test 1: Crossing Routes Conflict Analysis ===")
    crossing_routes = scenarios.get_crossing_routes()
    crossing_conflicts = analyzer.analyze_route_conflicts(crossing_routes)
    
    print(f"Found {crossing_conflicts['total_conflicts']} conflicts")
    for conflict in crossing_conflicts['conflicts']:
        print(f"- {conflict['route1']} vs {conflict['route2']} at time {conflict['time']}s")
        print(f"  Distance: {conflict['distance']:.2f}m, Severity: {conflict['severity']}")
    
    print(f"\nOverall Risk Assessment: {crossing_conflicts['risk_assessment']}")
    
    # 可视化
    visualizer = RouteVisualizer()
    visualizer.plot_routes_with_conflicts(crossing_routes, crossing_conflicts['conflicts'])
    
    # 测试2：平行航线分析
    print("\n=== Test 2: Parallel Routes Analysis ===")
    parallel_routes = scenarios.get_parallel_routes()
    parallel_conflicts = analyzer.analyze_route_conflicts(parallel_routes)
    print(f"Parallel route conflicts: {parallel_conflicts['total_conflicts']}")
    
    # 测试3：垂直分层分析
    print("\n=== Test 3: Vertical Separation Analysis ===")
    vertical_routes = scenarios.get_vertical_conflict_routes()
    vertical_conflicts = analyzer.analyze_route_conflicts(vertical_routes)
    print(f"Vertical separation conflicts: {vertical_conflicts['total_conflicts']}")
    
    # 测试4：复杂场景分析
    print("\n=== Test 4: Complex Scenario Analysis ===")
    complex_routes = scenarios.get_complex_scenario()
    complex_conflicts = analyzer.analyze_route_conflicts(complex_routes)
    
    print(f"Complex scenario conflicts: {complex_conflicts['total_conflicts']}")
    print(f"Risk assessment: {complex_conflicts['risk_assessment']}")
    
    # 3D可视化
    visualizer.plot_3d_routes(complex_routes)
    
    # 测试5：对地风险评估
    print("\n=== Test 5: Ground Risk Assessment ===")
    test_positions = [
        {"longitude": 113.32, "latitude": 23.12, "height": 50},
        {"longitude": 113.32, "latitude": 23.12, "height": 100},
        {"longitude": 113.32, "latitude": 23.12, "height": 200}
    ]
    
    for pos in test_positions:
        ground_risk = analyzer.calculate_ground_impact_risk(pos, population_density=0.8)
        print(f"Ground risk at {pos['height']}m altitude: {ground_risk['total_ground_risk']:.3f}")
        print(f"  - Impact probability: {ground_risk['impact_probability']:.3f}")
        print(f"  - Exposure area: {ground_risk['exposure_area']:.2f} m²")
        print(f"  - Height factor: {ground_risk['height_factor']:.3f}")
        print(f"  - Ground effect: {ground_risk['ground_effect']:.3f}")
    
    # 测试6：高冲突场景测试
    print("\n=== Test 6: High Conflict Scenario ===")
    high_conflict_routes = scenarios.get_high_conflict_scenario()
    high_conflicts = analyzer.analyze_route_conflicts(high_conflict_routes)
    
    print(f"High conflict scenario results:")
    print(f"  - Total conflicts: {high_conflicts['total_conflicts']}")
    print(f"  - Risk level: {high_conflicts['risk_assessment']['level']}")
    print(f"  - Risk score: {high_conflicts['risk_assessment']['score']}")
    
    # 详细展示每个冲突
    for i, conflict in enumerate(high_conflicts['conflicts']):
        print(f"\nConflict {i+1}:")
        print(f"  Routes: {conflict['route1']} <-> {conflict['route2']}")
        print(f"  Time: {conflict['time']}s")
        print(f"  Distance: {conflict['distance']:.2f}m")
        print(f"  Severity: {conflict['severity']}")
        print(f"  Location: ({conflict['location']['longitude']:.4f}, "
              f"{conflict['location']['latitude']:.4f}, "
              f"{conflict['location']['height']:.1f}m)")
    
    # 可视化高冲突场景
    visualizer.plot_routes_with_conflicts(high_conflict_routes, high_conflicts['conflicts'])
    
    print("\n=== Analysis Complete ===")
    print("Visualizations have been saved as PNG files.")