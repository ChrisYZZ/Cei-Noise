# ground_risk_evaluator.py
import math
from typing import Dict, List, Tuple

class GroundRiskEvaluator:
    """对地风险评估器"""
    
    def __init__(self):
        # 无人机参数
        self.UAV_PARAMS = {
            "small": {"radius": 1, "weight": 5, "impact_energy": 100},
            "medium": {"radius": 2, "weight": 25, "impact_energy": 500},
            "large": {"radius": 3, "weight": 50, "impact_energy": 1000}
        }
        
        # 人员参数
        self.PERSON_PARAMS = {
            "radius": 0.5,  # 米
            "height": 1.7   # 米
        }
        
    def evaluate_ground_risk(self, position: Dict, uav_type: str = "medium") -> Dict:
        """评估对地风险"""
        # 获取无人机参数
        uav = self.UAV_PARAMS.get(uav_type, self.UAV_PARAMS["medium"])
        
        # 1. 计算撞击概率区域
        impact_area = self._calculate_impact_area(position['height'], uav)
        
        # 2. 获取人口密度
        population_density = self._get_population_density(
            position['longitude'], position['latitude']
        )
        
        # 3. 计算撞击概率
        impact_probability = self._calculate_impact_probability(
            impact_area, population_density
        )
        
        # 4. 计算伤害严重度
        severity = self._calculate_severity(position['height'], uav)
        
        # 5. 综合风险评估
        total_risk = impact_probability * severity
        
        # 6. 计算缓解措施效果
        mitigation = self._calculate_mitigation_effect(position)
        
        return {
            "impact_probability": impact_probability,
            "impact_area_m2": impact_area,
            "severity_score": severity,
            "total_risk": total_risk,
            "risk_level": self._get_risk_level(total_risk),
            "population_density": population_density,
            "mitigation_factor": mitigation,
            "mitigated_risk": total_risk * (1 - mitigation),
            "recommendations": self._get_risk_recommendations(total_risk, position)
        }
    
    def _calculate_impact_area(self, height: float, uav: Dict) -> float:
        """计算撞击影响区域（基于论文公式）"""
        # 撞击角度（假设失控后的下降角）
        impact_angle = math.radians(45)  # 45度角
        
        # 水平偏移距离
        horizontal_distance = height / math.tan(impact_angle)
        
        # 考虑风的影响（简化模型）
        wind_drift = height * 0.1  # 假设10%的高度作为风偏移
        
        # 总影响半径
        impact_radius = horizontal_distance + wind_drift + uav['radius']
        
        # 影响面积
        impact_area = math.pi * impact_radius ** 2
        
        return impact_area
    
    def _get_population_density(self, lon: float, lat: float) -> float:
        """获取人口密度（人/平方米）"""
        # 实际应用中应该调用GIS服务获取真实数据
        # 这里使用简化的区域判断
        
        # 广州市中心区域坐标范围（示例）
        city_center = {
            "min_lon": 113.25, "max_lon": 113.35,
            "min_lat": 23.10, "max_lat": 23.15
        }
        
        # 判断是否在市中心
        if (city_center["min_lon"] <= lon <= city_center["max_lon"] and
            city_center["min_lat"] <= lat <= city_center["max_lat"]):
            # 市中心人口密度（人/平方米）
            return 0.01  # 相当于10000人/平方公里
        else:
            # 郊区人口密度
            return 0.001  # 相当于1000人/平方公里
    
    def _calculate_impact_probability(self, impact_area: float, 
                                    population_density: float) -> float:
        """计算撞击概率"""
        # 暴露人数
        exposed_people = impact_area * population_density
        
        # 考虑人员在该区域的概率（简化为线性关系）
        probability = min(exposed_people * 0.1, 1.0)  # 每10个暴露人员增加100%概率
        
        return probability
    
    def _calculate_severity(self, height: float, uav: Dict) -> float:
        """计算伤害严重度"""
        # 撞击速度（自由落体简化）
        impact_velocity = math.sqrt(2 * 9.8 * height)
        
        # 动能
        kinetic_energy = 0.5 * uav['weight'] * impact_velocity ** 2
        
        # 归一化严重度（0-1）
        max_energy = 10000  # 最大能量阈值
        severity = min(kinetic_energy / max_energy, 1.0)
        
        return severity
    
    def _calculate_mitigation_effect(self, position: Dict) -> float:
        """计算缓解措施效果"""
        mitigation = 0.0
        
        # 降落伞系统（高度大于50米时有效）
        if position['height'] > 50:
            mitigation += 0.3
            
        # 地理围栏
        mitigation += 0.2
        
        # 实时监控
        mitigation += 0.1
        
        return min(mitigation, 0.8)  # 最大缓解80%风险
    
    def _get_risk_level(self, risk_score: float) -> str:
        """获取风险等级"""
        if risk_score < 0.1:
            return "LOW"
        elif risk_score < 0.3:
            return "MEDIUM"
        elif risk_score < 0.6:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_risk_recommendations(self, risk_score: float, position: Dict) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        if risk_score > 0.3:
            recommendations.append("建议提高飞行高度以降低地面风险")
            
        if position['height'] < 100:
            recommendations.append("建议安装降落伞系统作为应急措施")
            
        if risk_score > 0.5:
            recommendations.append("建议避开人口密集区域飞行")
            recommendations.append("建议配备实时监控和紧急干预系统")
            
        return recommendations