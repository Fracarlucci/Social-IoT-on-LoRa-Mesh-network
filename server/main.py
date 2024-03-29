from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import db

Session = sessionmaker(bind=db.engine)
session = Session()

app = FastAPI()

class SensorsDataModel(BaseModel):
    acceleration: tuple
    pressure: float
    temperature: float
    humidity: float
    battery_percentage: float

@app.get("/sensors/{id}")
async def read_sensors(id: int):
    query = session.query(db.SensorsData, db.Acceleration)
    if id == 0:
        data = query.join(db.Acceleration).all()
    elif id == -1:
        data = query.join(db.Acceleration).order_by(db.SensorsData.dateTime.desc()).first()
    else:
        data = query.join(db.Acceleration).filter_by(id=id).first()
    if data == None:
        return {"error": "No data found"}
    return data

@app.post("/sensors/")
async def add_sensors_data(sensorsData: SensorsDataModel):
    if len(sensorsData.acceleration) != 3:
        return {"error": "Acceleration must have 3 values (x, y, z)"}
    
    acceleration = db.Acceleration(x=sensorsData.acceleration[0], y=sensorsData.acceleration[1], z=sensorsData.acceleration[2])
    newData = db.SensorsData(dateTime=datetime.now(), acceleration=acceleration, accelerationId=acceleration.id,
                             pressure=sensorsData.pressure, temperature=sensorsData.temperature,
                             humidity=sensorsData.humidity, battery_percentage=sensorsData.battery_percentage)
    session.add(newData)
    session.commit()

    return {"message": "Data added successfully"}
    