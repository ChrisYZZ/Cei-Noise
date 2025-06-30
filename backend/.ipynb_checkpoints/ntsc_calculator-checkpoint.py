# ntsc_calculator.py
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class FlightSegment:
    """飞行段数据结构"""
    start_time: float
    end_time: float
    start_pos: Dict[str, float]
    end_pos: Dict[str, float]
    aircraft_id: str

class NTSCCalculator:
    """NTSC (Near-Term Separation Capability) 计算器"""
    
    def __init__(self):
        self.HORIZONTAL_SEPARATION = 50  # 水平安全间隔（米）
        self.VERTICAL_SEPARATION = 30    # 垂直安全间隔（米）
        
    def calculate_ntsc(self, flight_segments: List[FlightSegment]) -> Dict:
        """计算NTSC指标"""
        total_flight_time = 0
        conflict_time = 0
        conflict_details = []
        
        # 计算总飞行时间
        for segment in flight_segments:
            total_flight_time += segment.end_time - segment.start_time
        
        # 检查每对飞行段之间的冲突
        for i in range(len(flight_segments)):
            for j in range(i + 1, len(flight_segments)):
                seg1 = flight_segments[i]
                seg2 = flight_segments[j]
                
                if seg1.aircraft_id == seg2.aircraft_id:
                    continue
                    
                # 计算时间重叠
                overlap_start = max(seg1.start_time, seg2.start_time)
                overlap_end = min(seg1.end_time, seg2.end_time)
                
                if overlap_start < overlap_end:
                    conflict_duration, min_distance = self._calculate_conflict_duration(
                        seg1, seg2, overlap_start, overlap_end
                    )
                    if conflict_duration > 0:
                        conflict_time += conflict_duration
                        conflict_details.append({
                            "aircraft_pair": (seg1.aircraft_id, seg2.aircraft_id),
                            "duration": conflict_duration,
                            "min_distance": min_distance,
                            "time_range": (overlap_start, overlap_end)
                        })
        
        ntsc = conflict_time / total_flight_time if total_flight_time > 0 else 0
        
        return {
            "ntsc_value": ntsc,
            "conflict_percentage": ntsc * 100,
            "total_flight_time": total_flight_time,
            "total_conflict_time": conflict_time,
            "conflict_details": conflict_details,
            "safety_level": self._get_safety_level(ntsc)
        }
    
    def _calculate_conflict_duration(self, seg1: FlightSegment, seg2: FlightSegment,
                                   overlap_start: float, overlap_end: float) -> Tuple[float, float]:
        """计算冲突持续时间和最小距离"""
        conflict_duration = 0
        min_distance = float('inf')
        time_step = 1.0  # 1秒的时间步长
        
        t = overlap_start
        while t <= overlap_end:
            pos1 = self._interpolate_position(seg1, t)
            pos2 = self._interpolate_position(seg2, t)
            
            horizontal_dist = self._haversine_distance(
                pos1['latitude'], pos1['longitude'],
                pos2['latitude'], pos2['longitude']
            )
            vertical_dist = abs(pos1['height'] - pos2['height'])
            
            total_distance = math.sqrt(horizontal_dist**2 + vertical_dist**2)
            min_distance = min(min_distance, total_distance)
            
            if (horizontal_dist < self.HORIZONTAL_SEPARATION and 
                vertical_dist < self.VERTICAL_SEPARATION):
                conflict_duration += time_step
                
            t += time_step
            
        return conflict_duration, min_distance
    
    def _interpolate_position(self, segment: FlightSegment, time: float) -> Dict[str, float]:
        """线性插值计算位置"""
        t_ratio = (time - segment.start_time) / (segment.end_time - segment.start_time)
        t_ratio = max(0, min(1, t_ratio))
        
        return {
            'longitude': segment.start_pos['longitude'] + 
                        t_ratio * (segment.end_pos['longitude'] - segment.start_pos['longitude']),
            'latitude': segment.start_pos['latitude'] + 
                       t_ratio * (segment.end_pos['latitude'] - segment.start_pos['latitude']),
            'height': segment.start_pos['height'] + 
                     t_ratio * (segment.end_pos['height'] - segment.start_pos['height'])
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """计算两点间距离（米）"""
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _get_safety_level(self, ntsc: float) -> str:
        """根据NTSC值判断安全等级"""
        if ntsc < 0.01:
            return "EXCELLENT"
        elif ntsc < 0.05:
            return "GOOD"
        elif ntsc < 0.1:
            return "ACCEPTABLE"
        elif ntsc < 0.2:
            return "WARNING"
        else:
            return "CRITICAL"