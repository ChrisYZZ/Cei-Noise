import unittest
from route_optimizer import RouteOptimizer
from airspace_capacity import AirspaceCapacityAnalyzer

class TestRouteOptimization(unittest.TestCase):
    
    def setUp(self):
        self.optimizer = RouteOptimizer()
        self.analyzer = AirspaceCapacityAnalyzer()
    
    def test_matrix_route_generation(self):
        """测试矩阵型航路生成"""
        route = self.optimizer.generate_matrix_route(
            (113.32, 23.11),
            (113.33, 23.14)
        )
        
        # 验证路径生成
        self.assertTrue(len(route) > 2)
        self.assertEqual(route[0]["longitude"], 113.32)
        self.assertEqual(route[0]["latitude"], 23.11)
        
        # 验证路径连续性
        for i in range(len(route) - 1):
            self.assertIn("time", route[i])
            self.assertIn("height", route[i])
            
        print(f"生成了 {len(route)} 个航路点")
        
    def test_capacity_calculation(self):
        """测试容量计算"""
        test_route = [
            {"longitude": 113.32, "latitude": 23.11, "height": 100, "time": 0},
            {"longitude": 113.33, "latitude": 23.12, "height": 100, "time": 60},
            {"longitude": 113.34, "latitude": 23.13, "height": 100, "time": 120},
        ]
        
        capacity = self.analyzer.calculate_route_capacity(test_route)
        
        # 验证返回的容量指标
        self.assertIn("max_aircraft_count", capacity)
        self.assertIn("throughput_per_hour", capacity)
        self.assertIn("route_length_km", capacity)
        self.assertGreater(capacity["max_aircraft_count"], 0)
        self.assertGreater(capacity["route_length_km"], 0)
        
        print(f"航路容量: {capacity}")
        
    def test_safety_assessment(self):
        """测试安全评估"""
        test_route = [
            {"longitude": 113.32, "latitude": 23.11, "height": 50, "time": 0},
            {"longitude": 113.33, "latitude": 23.12, "height": 100, "time": 60},
        ]
        
        safety = self.optimizer.validate_route_safety(test_route)
        
        # 验证安全评估结果
        self.assertIn("collision_risk", safety)
        self.assertIn("ground_risk", safety)
        self.assertIn("total_risk", safety)
        self.assertIn("is_safe", safety)
        
        self.assertGreaterEqual(safety["collision_risk"], 0)
        self.assertLessEqual(safety["collision_risk"], 1)
        
        print(f"安全评估: {safety}")
        
    def test_conflict_analysis(self):
        """测试冲突分析"""
        routes = [
            [
                {"longitude": 113.32, "latitude": 23.11, "height": 100},
                {"longitude": 113.33, "latitude": 23.12, "height": 100},
            ],
            [
                {"longitude": 113.31, "latitude": 23.12, "height": 100},
                {"longitude": 113.34, "latitude": 23.11, "height": 100},
            ]
        ]
        
        conflict_prob = self.analyzer.analyze_conflict_probability(routes, 5)
        
        # 验证冲突概率
        self.assertGreaterEqual(conflict_prob, 0)
        self.assertLessEqual(conflict_prob, 1)
        
        print(f"冲突概率: {conflict_prob}")

if __name__ == '__main__':
    unittest.main()
