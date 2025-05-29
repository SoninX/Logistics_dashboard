import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api"

def generate_timestamp():
    now = datetime.now()
    delta = random.randint(-7, 7) * 3600  # Random hours within a week
    return (now + timedelta(seconds=delta)).strftime("%Y-%m-%d %H:%M:%S")

def generate_vehicles():
    vehicles = [
        {
            "model": f"Model-{i}",
            "fuel_efficiency": 10.0 - i*0.1,
            "last_maintenance_date": generate_timestamp(),
            "mileage": random.randint(10000, 100000),
            "idle_hours": random.uniform(0, 100),
            "status": random.choice(["Active", "Inactive", "Maintenance"]),
            "avg_fuel_consumption": random.uniform(5, 15),
            "engine_hours": random.randint(100, 1000),
            "tire_condition": random.choice(["Good", "Fair", "Poor"]),
            "battery_health": random.randint(50, 100)
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/vehicles/batch", json=vehicles)
    return [r["id"] for r in response.json()]

def generate_drivers():
    drivers = [
        {
            "name": f"Driver {i}",
            "license_number": f"LN{i:03d}",
            "total_deliveries": random.randint(0, 100),
            "punctuality_score": random.uniform(0, 100),
            "incident_count": random.randint(0, 5),
            "status": random.choice(["Available", "On Duty", "Off Duty"]),
            "training_completed": random.choice(["Yes", "No"]),
            "joined_date": generate_timestamp(),
            "contact_number": f"+1-555-01{i:02d}"
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/drivers/batch", json=drivers)
    return [r["id"] for r in response.json()]

def generate_routes():
    routes = [
        {
            "origin_lat": 40.0 + i*0.1,
            "origin_lng": -74.0 + i*0.1,
            "dest_lat": 41.0 + i*0.1,
            "dest_lng": -73.0 + i*0.1,
            "distance_km": 100.0 + i*10,
            "typical_traffic": random.uniform(0.1, 1.0),
            "route_name": f"Route {i}"
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/routes/batch", json=routes)
    return [r["id"] for r in response.json()]

def generate_slas():
    slas = [
        {
            "name": f"SLA {i}",
            "max_hours": 4.0 + i*0.5,
            "penalty": 100.0 + i*50
        }
        for i in range(3)
    ]
    response = requests.post(f"{BASE_URL}/slas/batch", json=slas)
    return [r["id"] for r in response.json()]

def generate_deliveries(vehicle_ids, driver_ids, route_ids, sla_ids):
    sla_types = ["Standard", "Express", "Priority"]
    statuses = ["Pending", "In Transit", "Delivered"]
    vehicle_conditions = ["Good", "Fair", "Needs Repair"]
    weather_conditions = ["Clear", "Rain", "Snow"]
    weather_severities = ["Low", "Moderate", "High"]
    times_of_day = ["Morning", "Afternoon", "Evening", "Night"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    deliveries = [
        {
            "vehicle_id": random.choice(vehicle_ids),
            "driver_id": random.choice(driver_ids),
            "scheduled_time": generate_timestamp(),
            "actual_time": generate_timestamp(),
            "status": random.choice(statuses),
            "sla_type": random.choice(sla_types),
            "distance_km": random.uniform(50, 200),
            "fuel_consumed": random.uniform(10, 50),
            "idle_time_min": random.uniform(0, 60),
            "vehicle_condition": random.choice(vehicle_conditions),
            "origin_lat": random.uniform(40, 41),
            "origin_lng": random.uniform(-74, -73),
            "dest_lat": random.uniform(40, 41),
            "dest_lng": random.uniform(-74, -73),
            "estimated_time_min": random.uniform(30, 120),
            "actual_time_min": random.uniform(30, 150),
            "fuel_efficiency": random.uniform(5, 15),
            "estimated_fuel_cost": random.uniform(20, 100),
            "route_efficiency": random.uniform(0.7, 1.0),
            "traffic_index": random.uniform(0.1, 1.0),
            "sla_compliance": random.randint(0, 100),
            "delay_minutes": random.uniform(0, 60),
            "penalty_amount": random.uniform(0, 500),
            "weather_condition": random.choice(weather_conditions),
            "weather_severity": random.choice(weather_severities),
            "temperature": random.uniform(-10, 35),
            "humidity": random.randint(20, 90),
            "wind_speed": random.uniform(0, 20),
            "date": generate_timestamp(),
            "time_of_day": random.choice(times_of_day),
            "day_of_week": random.choice(days_of_week),
            "is_weekend": random.choice([True, False])
        }
        for _ in range(10)
    ]
    response = requests.post(f"{BASE_URL}/deliveries/batch", json=deliveries)
    return [r["id"] for r in response.json()]

def generate_weather():
    weather = [
        {
            "location": f"City {i}",
            "timestamp": generate_timestamp(),
            "temperature": random.uniform(-10, 35),
            "condition": random.choice(["Clear", "Rain", "Snow"]),
            "wind_speed": random.uniform(0, 20),
            "humidity": random.randint(20, 90),
            "severity": random.choice(["Low", "Moderate", "High"])
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/weather/batch", json=weather)
    return [r["id"] for r in response.json()]

def generate_maintenance(vehicle_ids):
    maintenance = [
        {
            "vehicle_id": random.choice(vehicle_ids),
            "date": generate_timestamp(),
            "type": random.choice(["Oil Change", "Tire Rotation", "Brake Repair"]),
            "cost": random.uniform(100, 1000),
            "description": f"Maintenance {i}",
            "status": random.choice(["Scheduled", "Completed"])
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/maintenance/batch", json=maintenance)
    return [r["id"] for r in response.json()]

def generate_traffic():
    traffic = [
        {
            "location": f"City {i}",
            "timestamp": generate_timestamp(),
            "traffic_index": random.uniform(0.1, 1.0),
            "delay_minutes": random.uniform(5, 60),
            "severity": random.choice(["Low", "Moderate", "High"])
        }
        for i in range(5)
    ]
    response = requests.post(f"{BASE_URL}/traffic/batch", json=traffic)
    return [r["id"] for r in response.json()]

def main():
    # Clear existing data
    for endpoint in ["vehicles", "drivers", "routes", "slas", "deliveries", "weather", "maintenance", "traffic"]:
        requests.delete(f"{BASE_URL}/{endpoint}/all")

    # Generate data
    vehicle_ids = generate_vehicles()
    driver_ids = generate_drivers()
    route_ids = generate_routes()
    sla_ids = generate_slas()
    generate_deliveries(vehicle_ids, driver_ids, route_ids, sla_ids)
    generate_weather()
    generate_maintenance(vehicle_ids)
    generate_traffic()
    print("Data generation complete.")

if __name__ == "__main__":
    main()