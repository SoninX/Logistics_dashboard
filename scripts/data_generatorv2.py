import requests
from datetime import datetime, timedelta
import random
import time
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
from math import radians, sin, cos, sqrt, atan2

BASE_URL = "http://localhost:8000/api"
VEHICLE_MODELS = ["Tata Ace", "Tata 407", "Mahindra Jeeto", "Ashok Leyland Dost", "Mahindra Supro", "Tata Ultra", "Eicher Pro", "Bajaj Qute", "Piaggio Ape", "Force Tempo", "Maruti Suzuki Carry", "Tata Winger", "Mahindra Bolero", "Ashok Leyland Partner", "Eicher 14.10", "Tata Signa", "Mahindra Furio", "Ashok Leyland 1616", "BharatBenz 1214", "Volvo FMX"]
INDIAN_FIRST_NAMES = ["Rahul", "Raj", "Amit", "Suresh", "Deepak", "Vijay", "Anil", "Sunil", "Manoj", "Arun", "Sanjay", "Ramesh", "Vikram", "Praveen", "Gopal", "Harish", "Kiran", "Naveen", "Pradeep", "Sandeep", "Ravi", "Dinesh", "Mukesh", "Sachin", "Aakash", "Vishal", "Alok", "Bharat", "Chandan", "Dheeraj"]
INDIAN_LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Mehta", "Reddy", "Jain", "Shah", "Malik", "Yadav", "Thakur", "Rao", "Choudhary", "Pandey", "Mishra", "Srivastava", "Deshmukh", "Naik", "Khan", "Patil", "Joshi", "Gowda"]
INDIAN_CITIES = {"Mumbai": (19.0760, 72.8777), "Delhi": (28.7041, 77.1025), "Bangalore": (12.9716, 77.5946), "Hyderabad": (17.3850, 78.4867), "Chennai": (13.0827, 80.2707), "Kolkata": (22.5726, 88.3639), "Pune": (18.5204, 73.8567), "Ahmedabad": (23.0225, 72.5714), "Jaipur": (26.9124, 75.7873), "Surat": (21.1702, 72.8311), "Lucknow": (26.8467, 80.9462), "Kanpur": (26.4499, 80.3319), "Nagpur": (21.1458, 79.0882), "Indore": (22.7196, 75.8577), "Thane": (19.2183, 72.9781), "Bhopal": (23.2599, 77.4126), "Visakhapatnam": (17.6868, 83.2185), "Patna": (25.5941, 85.1376), "Vadodara": (22.3072, 73.1812), "Ghaziabad": (28.6692, 77.4538)}
WEATHER_IMPACT = {"Clear": {"speed_factor": 1.0, "delay_factor": 1.0, "fuel_factor": 1.0}, "Rain": {"speed_factor": 0.7, "delay_factor": 1.5, "fuel_factor": 1.2}, "Snow": {"speed_factor": 0.5, "delay_factor": 2.0, "fuel_factor": 1.5}}

logging.basicConfig(filename="data_generation.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def generate_timestamp(start_date, end_date):
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def post_with_retry(endpoint, batch):
    response = requests.post(f"{BASE_URL}/{endpoint}/batch", json=batch)
    response.raise_for_status()
    return response.json()

def post_in_batches(endpoint, data, batch_size=100):
    ids = []
    for i in tqdm(range(0, len(data), batch_size), desc=f"Inserting {endpoint}", unit="batch"):
        batch = data[i:i+batch_size]
        try:
            response_data = post_with_retry(endpoint, batch)
            ids.extend([r["id"] for r in response_data])
            logging.info(f"Inserted {len(batch)} records to {endpoint}")
        except Exception as e:
            logging.error(f"Error inserting {endpoint}: {e}")
        time.sleep(0.1)
    return ids

def generate_vehicles():
    vehicles = []
    for i in range(20):
        model = VEHICLE_MODELS[i]
        last_maintenance = datetime.now() - timedelta(days=random.randint(1, 180))
        base_efficiency = 8.0 + random.random() * 7.0
        vehicle = {
            "model": model,
            "fuel_efficiency": round(base_efficiency, 1),
            "last_maintenance_date": last_maintenance.strftime("%Y-%m-%d %H:%M:%S"),
            "mileage": random.randint(50000, 200000),
            "idle_hours": round(random.uniform(100, 1000), 1),
            "status": random.choice(["Active", "Active", "Active", "Inactive", "Maintenance"]),
            "avg_fuel_consumption": round(base_efficiency * 0.9, 1),
            "engine_hours": random.randint(1000, 5000),
            "tire_condition": random.choice(["Good", "Good", "Fair", "Fair", "Poor"]),
            "battery_health": random.randint(70, 100)
        }
        vehicles.append(vehicle)
    return post_in_batches("vehicles", vehicles)

def generate_drivers():
    drivers = []
    for i in range(50):
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        joined_date = datetime.now() - timedelta(days=random.randint(180, 365*3))
        driver = {
            "name": f"{first_name} {last_name}",
            "license_number": f"DL{random.randint(10000000, 99999999)}",
            "total_deliveries": random.randint(50, 500),
            "punctuality_score": round(random.uniform(75, 99), 1),
            "incident_count": random.randint(0, 3),
            "status": random.choice(["Available", "On Duty", "Off Duty"]),
            "training_completed": random.choice(["Yes", "No"]),
            "joined_date": joined_date.strftime("%Y-%m-%d %H:%M:%S"),
            "contact_number": f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}"
        }
        drivers.append(driver)
    return post_in_batches("drivers", drivers)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def generate_routes():
    routes = []
    cities = list(INDIAN_CITIES.keys())
    for i in range(100):
        origin_city = random.choice(cities)
        dest_city = random.choice(cities)
        while dest_city == origin_city:
            dest_city = random.choice(cities)
        origin_lat, origin_lng = INDIAN_CITIES[origin_city]
        dest_lat, dest_lng = INDIAN_CITIES[dest_city]
        distance = calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng)
        route = {
            "origin_lat": round(origin_lat, 6),
            "origin_lng": round(origin_lng, 6),
            "dest_lat": round(dest_lat, 6),
            "dest_lng": round(dest_lng, 6),
            "distance_km": round(distance, 1),
            "typical_traffic": round(random.uniform(0.3, 0.9), 2),
            "route_name": f"{origin_city} to {dest_city}"
        }
        routes.append(route)
    return post_in_batches("routes", routes)

def generate_slas():
    slas = [
        {"name": "Standard", "max_hours": 48.0, "penalty": 500.0},
        {"name": "Express", "max_hours": 24.0, "penalty": 1000.0},
        {"name": "Priority", "max_hours": 12.0, "penalty": 2000.0}
    ]
    return post_in_batches("slas", slas)

def generate_deliveries(vehicle_ids, driver_ids, route_ids, sla_ids):
    vehicle_data = requests.get(f"{BASE_URL}/vehicles").json()
    driver_data = requests.get(f"{BASE_URL}/drivers").json()
    route_data = requests.get(f"{BASE_URL}/routes").json()
    active_vehicles = [v["id"] for v in vehicle_data if v["status"] == "Active"]
    available_drivers = [d["id"] for d in driver_data if d["status"] in ["Available", "On Duty"]]
    vehicle_efficiency = {v["id"]: v["fuel_efficiency"] for v in vehicle_data}
    route_coords = {r["id"]: (r["origin_lat"], r["origin_lng"], r["dest_lat"], r["dest_lng"]) for r in route_data}

    sla_types = ["Standard", "Express", "Priority"]
    statuses = ["Pending", "In Transit", "Delivered", "Delayed", "Cancelled"]
    vehicle_conditions = ["Good", "Fair", "Needs Repair"]
    weather_conditions = ["Clear", "Rain", "Snow"]
    weather_severities = ["Low", "Moderate", "High"]
    times_of_day = ["Morning", "Afternoon", "Evening", "Night"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()

    deliveries = []
    for _ in range(5000):
        vehicle_id = random.choice(active_vehicles)
        driver_id = random.choice(available_drivers)
        route_id = random.choice(route_ids)
        origin_lat, origin_lng, dest_lat, dest_lng = route_coords[route_id]
        efficiency = vehicle_efficiency.get(vehicle_id, 8.0)
        base_distance = random.uniform(50, 500)
        weather = random.choice(weather_conditions)
        weather_factor = WEATHER_IMPACT[weather]

        speed = 40 * weather_factor["speed_factor"]
        estimated_hours = base_distance / speed
        actual_hours = estimated_hours * random.uniform(0.9, 1.5) * weather_factor["delay_factor"]

        scheduled = generate_timestamp(start_date, end_date)
        actual = scheduled + timedelta(minutes=round(actual_hours * 60))

        base_fuel_consumption = base_distance / efficiency
        fuel_consumed = base_fuel_consumption * weather_factor["fuel_factor"] * random.uniform(0.9, 1.1)

        sla_compliance = 100 - random.randint(0, 30) if weather == "Clear" else 100 - random.randint(10, 60)

        day = random.choice(days_of_week)
        is_weekend = day in ["Saturday", "Sunday"]
        weekend_factor = 1.3 if is_weekend else 1.0

        delivery = {
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "scheduled_time": scheduled.strftime("%Y-%m-%d %H:%M:%S"),
            "actual_time": actual.strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choices(statuses, weights=[0.1, 0.2, 0.6, 0.09, 0.01])[0],
            "sla_type": random.choice(sla_types),
            "distance_km": round(base_distance, 1),
            "fuel_consumed": round(fuel_consumed, 1),
            "idle_time_min": round(random.uniform(5, 60), 1),
            "vehicle_condition": random.choices(vehicle_conditions, weights=[0.7, 0.25, 0.05])[0],
            "origin_lat": origin_lat,
            "origin_lng": origin_lng,
            "dest_lat": dest_lat,
            "dest_lng": dest_lng,
            "estimated_time_min": round(estimated_hours * 60, 1),
            "actual_time_min": round(actual_hours * 60 * weekend_factor, 1),
            "fuel_efficiency": round(efficiency * random.uniform(0.8, 1.2), 1),
            "estimated_fuel_cost": round(fuel_consumed * 100, 2),
            "route_efficiency": round(random.uniform(0.8, 1.0), 2),
            "traffic_index": round(random.uniform(0.3, 0.9), 2),
            "sla_compliance": max(0, min(100, round(sla_compliance, 1))),
            "delay_minutes": max(0, round((actual_hours - estimated_hours) * 60 * weekend_factor, 1)),
            "penalty_amount": round(random.uniform(0, 500) if sla_compliance < 90 else 0, 2),
            "weather_condition": weather,
            "weather_severity": random.choices(weather_severities, weights=[0.6, 0.3, 0.1])[0],
            "temperature": round(random.uniform(10, 40), 1),
            "humidity": random.randint(30, 90),
            "wind_speed": round(random.uniform(0, 15), 1),
            "date": scheduled.strftime("%Y-%m-%d %H:%M:%S"),
            "time_of_day": random.choice(times_of_day),
            "day_of_week": day,
            "is_weekend": is_weekend
        }
        deliveries.append(delivery)
    return post_in_batches("deliveries", deliveries, batch_size=200)

def generate_weather():
    weather_records = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(365):
        record_date = start_date + timedelta(days=i)
        city = random.choice(list(INDIAN_CITIES.keys()))
        month = record_date.month
        if month in [11, 12, 1, 2]:
            temp = random.uniform(5, 25)
            condition = random.choices(["Clear", "Rain", "Snow"], weights=[0.7, 0.2, 0.1])[0]
        elif month in [3, 4, 5]:
            temp = random.uniform(25, 45)
            condition = random.choices(["Clear", "Rain"], weights=[0.9, 0.1])[0]
        else:
            temp = random.uniform(20, 35)
            condition = random.choices(["Clear", "Rain"], weights=[0.3, 0.7])[0]
        weather = {
            "location": city,
            "timestamp": record_date.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temp, 1),
            "condition": condition,
            "wind_speed": round(random.uniform(0, 20), 1),
            "humidity": random.randint(30, 95),
            "severity": random.choices(["Low", "Moderate", "High"], weights=[0.6, 0.3, 0.1])[0]
        }
        weather_records.append(weather)
    return post_in_batches("weather", weather_records)

def generate_maintenance(vehicle_ids):
    maintenance_records = []
    start_date = datetime.now() - timedelta(days=365)
    for _ in range(365):
        vehicle_id = random.choice(vehicle_ids)
        record_date = start_date + timedelta(days=random.randint(0, 364))
        maintenance_type = random.choices(
            ["Oil Change", "Tire Rotation", "Brake Repair", "Filter Change", "Battery Check"],
            weights=[0.4, 0.3, 0.1, 0.15, 0.05]
        )[0]
        cost_ranges = {
            "Oil Change": (500, 2000),
            "Tire Rotation": (300, 1000),
            "Brake Repair": (2000, 8000),
            "Filter Change": (300, 1500),
            "Battery Check": (200, 1000)
        }
        maintenance = {
            "vehicle_id": vehicle_id,
            "date": record_date.strftime("%Y-%m-%d %H:%M:%S"),
            "type": maintenance_type,
            "cost": round(random.uniform(*cost_ranges[maintenance_type]), 2),
            "description": f"{maintenance_type} for vehicle {vehicle_id}",
            "status": "Completed"
        }
        maintenance_records.append(maintenance)
    return post_in_batches("maintenance", maintenance_records)

def generate_traffic():
    traffic_records = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(365):
        record_date = start_date + timedelta(days=i)
        city = random.choice(list(INDIAN_CITIES.keys()))
        hour = record_date.hour
        if 7 <= hour < 10 or 17 <= hour < 20:
            traffic_index = random.uniform(0.7, 1.0)
            delay = random.uniform(20, 60)
            severity = random.choices(["Moderate", "High"], weights=[0.4, 0.6])[0]
        else:
            traffic_index = random.uniform(0.3, 0.7)
            delay = random.uniform(5, 20)
            severity = random.choices(["Low", "Moderate"], weights=[0.7, 0.3])[0]
        traffic = {
            "location": city,
            "timestamp": record_date.strftime("%Y-%m-%d %H:%M:%S"),
            "traffic_index": round(traffic_index, 2),
            "delay_minutes": round(delay, 1),
            "severity": severity
        }
        traffic_records.append(traffic)
    return post_in_batches("traffic", traffic_records)

def main():
    confirm = input("This will delete all existing data. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    print("Clearing existing data...")
    for endpoint in ["vehicles", "drivers", "routes", "slas", "deliveries", "weather", "maintenance", "traffic"]:
        requests.delete(f"{BASE_URL}/{endpoint}/all")

    print("\nGenerating vehicles (20 records)...")
    vehicle_ids = generate_vehicles()
    print(f"Generated {len(vehicle_ids)} vehicles")

    print("\nGenerating drivers (50 records)...")
    driver_ids = generate_drivers()
    print(f"Generated {len(driver_ids)} drivers")

    print("\nGenerating routes (100 records)...")
    route_ids = generate_routes()
    print(f"Generated {len(route_ids)} routes")

    print("\nGenerating SLAs (3 records)...")
    sla_ids = generate_slas()
    print(f"Generated {len(sla_ids)} SLAs")

    print("\nGenerating weather data (365 records)...")
    weather_ids = generate_weather()
    print(f"Generated {len(weather_ids)} weather records")

    print("\nGenerating maintenance records (365 records)...")
    maintenance_ids = generate_maintenance(vehicle_ids)
    print(f"Generated {len(maintenance_ids)} maintenance records")

    print("\nGenerating traffic data (365 records)...")
    traffic_ids = generate_traffic()
    print(f"Generated {len(traffic_ids)} traffic records")

    print("\nGenerating deliveries (5000 records)...")
    delivery_ids = generate_deliveries(vehicle_ids, driver_ids, route_ids, sla_ids)
    print(f"Generated {len(delivery_ids)} deliveries")

    print("\nData generation complete. Summary:")
    print(f"- Vehicles: {len(vehicle_ids)}")
    print(f"- Drivers: {len(driver_ids)}")
    print(f"- Routes: {len(route_ids)}")
    print(f"- SLAs: {len(sla_ids)}")
    print(f"- Weather: {len(weather_ids)}")
    print(f"- Maintenance: {len(maintenance_ids)}")
    print(f"- Traffic: {len(traffic_ids)}")
    print(f"- Deliveries: {len(delivery_ids)}")

if __name__ == "__main__":
    main()