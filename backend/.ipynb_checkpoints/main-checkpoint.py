from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from route_optimizer import RouteOptimizer
from airspace_capacity import AirspaceCapacityAnalyzer
import math




app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 预定义的广州市飞行线路
FLIGHT_ROUTES = [ {
        "name": "珠江新城CBD商务快递线",
        "description": "高层建筑密集区的商务快递配送",
        "base_noise": 82,
        "path": [
            {"longitude": 113.3234, "latitude": 23.1367, "height": 120, "time": 0},
            {"longitude": 113.3240, "latitude": 23.1320, "height": 120, "time": 60},
            {"longitude": 113.3245, "latitude": 23.1280, "height": 120, "time": 120},
            {"longitude": 113.3248, "latitude": 23.1240, "height": 120, "time": 180},
            {"longitude": 113.3250, "latitude": 23.1200, "height": 120, "time": 240},
            {"longitude": 113.3248, "latitude": 23.1160, "height": 120, "time": 300},
            {"longitude": 113.3245, "latitude": 23.1120, "height": 120, "time": 360},
            {"longitude": 113.3244, "latitude": 23.1066, "height": 120, "time": 420}
        ]
    }, {
        "name": "省医-中山一院医疗应急线",
        "description": "医院间医疗物资和样本快速运送",
        "base_noise": 78,
        "path": [
            {"longitude": 113.2590, "latitude": 23.1283, "height": 150, "time": 0},
            {"longitude": 113.2650, "latitude": 23.1285, "height": 150, "time": 30},
            {"longitude": 113.2710, "latitude": 23.1288, "height": 150, "time": 60},
            {"longitude": 113.2770, "latitude": 23.1292, "height": 150, "time": 90},
            {"longitude": 113.2830, "latitude": 23.1298, "height": 150, "time": 120},
            {"longitude": 113.2890, "latitude": 23.1305, "height": 150, "time": 150},
            {"longitude": 113.2950, "latitude": 23.1311, "height": 150, "time": 180}
        ]
    }, {
        "name": "白云机场-黄埔港物流线",
        "description": "长距离货物运输线路",
        "base_noise": 85,
        "path": [
            {"longitude": 113.3089, "latitude": 23.3924, "height": 200, "time": 0},
            {"longitude": 113.3200, "latitude": 23.3600, "height": 200, "time": 120},
            {"longitude": 113.3300, "latitude": 23.3300, "height": 200, "time": 240},
            {"longitude": 113.3400, "latitude": 23.3000, "height": 200, "time": 360},
            {"longitude": 113.3500, "latitude": 23.2700, "height": 200, "time": 480},
            {"longitude": 113.3600, "latitude": 23.2400, "height": 200, "time": 600},
            {"longitude": 113.3700, "latitude": 23.2100, "height": 200, "time": 720},
            {"longitude": 113.3800, "latitude": 23.1800, "height": 200, "time": 840},
            {"longitude": 113.3900, "latitude": 23.1500, "height": 200, "time": 960},
            {"longitude": 113.4000, "latitude": 23.1200, "height": 200, "time": 1080},
            {"longitude": 113.4589, "latitude": 23.0967, "height": 200, "time": 1200}
        ]
    }, {
        "name": "大学城教育园区巡检线",
        "description": "校园安全巡逻和监控",
        "base_noise": 75,
        "path": [
            {"longitude": 113.3984, "latitude": 23.0588, "height": 80, "time": 0},
            {"longitude": 113.4000, "latitude": 23.0600, "height": 80, "time": 60},
            {"longitude": 113.4020, "latitude": 23.0620, "height": 80, "time": 120},
            {"longitude": 113.4040, "latitude": 23.0640, "height": 80, "time": 180},
            {"longitude": 113.4060, "latitude": 23.0660, "height": 80, "time": 240},
            {"longitude": 113.4040, "latitude": 23.0680, "height": 80, "time": 300},
            {"longitude": 113.4020, "latitude": 23.0660, "height": 80, "time": 360},
            {"longitude": 113.4000, "latitude": 23.0640, "height": 80, "time": 420},
            {"longitude": 113.3984, "latitude": 23.0588, "height": 80, "time": 480}
        ]
    }, {
        "name": "老城区文物保护巡查线",
        "description": "历史建筑和文物保护区巡查",
        "base_noise": 76,
        "path": [
            {"longitude": 113.2507, "latitude": 23.1307, "height": 60, "time": 0},
            {"longitude": 113.2520, "latitude": 23.1320, "height": 60, "time": 60},
            {"longitude": 113.2540, "latitude": 23.1340, "height": 60, "time": 120},
            {"longitude": 113.2560, "latitude": 23.1360, "height": 60, "time": 180},
            {"longitude": 113.2580, "latitude": 23.1340, "height": 60, "time": 240},
            {"longitude": 113.2560, "latitude": 23.1320, "height": 60, "time": 300},
            {"longitude": 113.2540, "latitude": 23.1300, "height": 60, "time": 360}
        ]
    }] 

# 广州塔 113.32,23.11   广州天河体育中心  113.33,23.14
# 噪声计算核心函数
def calculateNoiseAtPoint(dronePosition, groundPoint):
    # 计算水平距离（米）
    R = 6371000  # 地球半径
    φ1 = math.radians(dronePosition['latitude'])
    φ2 = math.radians(groundPoint['latitude'])
    Δφ = math.radians(groundPoint['latitude'] - dronePosition['latitude'])
    Δλ = math.radians(groundPoint['longitude'] - dronePosition['longitude'])

    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) * math.sin(Δλ / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    horizontalDistance = R * c

    # 计算斜距
    verticalDistance = dronePosition['height']
    distance = math.sqrt(horizontalDistance * horizontalDistance + verticalDistance * verticalDistance)

    # 噪声衰减计算
    referenceDistance = 1  # 1米参考距离
    distanceAttenuation = 20 * math.log10(distance / referenceDistance)

    # 大气衰减（简化模型）
    atmosphericAttenuation = 0.005 * distance

    # 地面效应（低空飞行时增强）
    if dronePosition['height'] < 100:
        groundEffect = 3 * (1 - dronePosition['height'] / 100)
    else:
        groundEffect = 0

    return max(distanceAttenuation + atmosphericAttenuation - groundEffect, 0)

# 生成网格化噪声数据（符合当前项目的GeoJSON格式）
def generateNoiseGeoJSON(route, gridSize = 50):
    features = []

    # 确定路线的边界
    minLon = float('inf')
    maxLon = float('-inf')
    minLat = float('inf')
    maxLat = float('-inf')

    for point in route['path']:
        minLon = min(minLon, point['longitude'])
        maxLon = max(maxLon, point['longitude'])
        minLat = min(minLat, point['latitude'])
        maxLat = max(maxLat, point['latitude'])

    # 扩展边界以覆盖噪声影响范围
    buffer = 0.005  # 约500米
    minLon -= buffer
    maxLon += buffer
    minLat -= buffer
    maxLat += buffer

    # 网格采样
    lonStep = gridSize / 111000  # 经度步长
    latStep = gridSize / 111000  # 纬度步长


    for lon in frange(minLon, maxLon + lonStep, lonStep):
        for lat in frange(minLat, maxLat + latStep, latStep):
            maxNoise = float(route['base_noise'])
            minNoise = float(route['base_noise'])
            noise = float(route['base_noise'])

            # 计算整条飞行路线对该点的最大噪声影响
            for index in range(len(route['path']) - 1):
                point = route['path'][index]
                nextPoint = route['path'][index + 1]
                steps = 10  # 插值步数

                for i in range(steps + 1):
                    t = i / steps
                    interpolatedPos = {
                        'longitude': point['longitude'] + t * (nextPoint['longitude'] - point['longitude']),
                        'latitude': point['latitude'] + t * (nextPoint['latitude'] - point['latitude']),
                        'height': point['height'] + t * (nextPoint['height'] - point['height'])
                    }

                    attenuation = calculateNoiseAtPoint(interpolatedPos, {'longitude': lon, 'latitude': lat})
                    noise = route['base_noise'] - attenuation
                    maxNoise = max(maxNoise, noise)
                    minNoise = min(minNoise, noise)

            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]
                },
                'properties': {
                    'noise': noise,
                    'maxNoise': maxNoise,
                    'minNoise': minNoise,
                    'minLon': minLon,
                    'maxLon': maxLon,
                    'minLat': minLat,
                    'maxLat': maxLat,
                    'routeName': route['name']
                }
            })

    return {
        'type': 'FeatureCollection',
        'features': features
    }

# 辅助函数，用于生成浮点数范围
def frange(start, stop, step):
    while start <= stop:
        yield start
        start += step

# 为Map.vue组件生成适配的噪声数据
def generateNoiseDataForHeatmap(route):
    noiseData = generateNoiseGeoJSON(route, 50)
    points = []
    minNoise = 0
    maxNoise = 0
    minLon = None
    maxLon = None
    minLat = None
    maxLat = None

    for feature in noiseData['features']:
        minNoise = feature['properties']['minNoise']
        maxNoise = feature['properties']['maxNoise']
        minLon = feature['properties']['minLon']
        maxLon = feature['properties']['maxLon']
        minLat = feature['properties']['minLat']
        maxLat = feature['properties']['maxLat']
        points.append({
            'x': feature['geometry']['coordinates'][0],
            'y': feature['geometry']['coordinates'][1],
            'value': feature['properties']['noise'] * 10  # 放大以适应热力图显示
        })

    return {
        'points': points,
        'minNoise': minNoise,
        'maxNoise': maxNoise,
        'minLon': minLon,
        'maxLon': maxLon,
        'minLat': minLat,
        'maxLat': maxLat
    }

@app.get("/noise")
def get_data(index: int = None):
    if index is not None and 0 <= index < len(FLIGHT_ROUTES):
        return generateNoiseDataForHeatmap(FLIGHT_ROUTES[index])
    return generateNoiseDataForHeatmap(FLIGHT_ROUTES[0])

@app.get("/data")
def get_data():
    return FLIGHT_ROUTES

##########################城市低空航路规划#############################
# 初始化优化器
route_optimizer = RouteOptimizer()
capacity_analyzer = AirspaceCapacityAnalyzer()

@app.get("/optimize_route")
def optimize_route(
    start_lon: float, start_lat: float,
    end_lon: float, end_lat: float,
    route_type: str = "matrix"
):
    """基于论文理论优化航路"""
    
    if route_type == "matrix":
        optimized_path = route_optimizer.generate_matrix_route(
            (start_lon, start_lat),
            (end_lon, end_lat)
        )
    
    # 安全评估
    safety_assessment = route_optimizer.validate_route_safety(
        optimized_path, 
        []  # 障碍物列表，实际应用中需要真实数据
    )
    
    # 容量分析
    capacity_metrics = capacity_analyzer.calculate_route_capacity(
        optimized_path
    )
    
    return {
        "optimized_path": optimized_path,
        "safety_assessment": safety_assessment,
        "capacity_metrics": capacity_metrics
    }

@app.get("/airspace_analysis")
def analyze_airspace():
    """分析当前空域状况"""
    
    # 分析所有航路的冲突概率
    all_routes = [route["path"] for route in FLIGHT_ROUTES]
    
    conflict_probability = capacity_analyzer.analyze_conflict_probability(
        all_routes,
        traffic_density=5  # 假设每平方公里5架无人机
    )
    
    # 计算每条航路的容量
    route_capacities = []
    for route in FLIGHT_ROUTES:
        capacity = capacity_analyzer.calculate_route_capacity(route["path"])
        route_capacities.append({
            "name": route["name"],
            "capacity": capacity
        })
    
    return {
        "conflict_probability": conflict_probability,
        "route_capacities": route_capacities,
        "recommendations": generate_recommendations(conflict_probability)
    }

def generate_recommendations(conflict_prob: float) -> List[str]:
    """基于分析结果生成建议"""
    recommendations = []
    
    if conflict_prob > 0.3:
        recommendations.append("建议增加航路间隔或实施分时飞行")
    if conflict_prob > 0.5:
        recommendations.append("建议重新规划部分航路以减少交叉")
        
    return recommendations

##########################城市低空航路规划#############################

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080,  reload=True)