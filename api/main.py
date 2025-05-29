from fastapi import FastAPI
from api.database import Base, engine
from api.routers import vehicle, driver, delivery, weather, maintenance, route, sla, traffic

app = FastAPI(title="Logistics Dashboard API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(vehicle.router, prefix="/api")
app.include_router(driver.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(weather.router, prefix="/api")
app.include_router(maintenance.router, prefix="/api")
app.include_router(route.router, prefix="/api")
app.include_router(sla.router, prefix="/api")
app.include_router(traffic.router, prefix="/api")