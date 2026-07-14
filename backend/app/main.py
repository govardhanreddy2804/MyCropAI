from fastapi import FastAPI

app = FastAPI(
    title="MyCropAI API",
    version="1.0.0",
    description="Backend API for MyCropAI"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to MyCropAI Backend!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/about")
def about():
    return {
        "project": "MyCropAI",
        "backend": "FastAPI",
        "version": "1.0.0"
    }

@app.get("/farms/{farm_id}")
def get_farm(farm_id: int):
    return {
        "farm_id": farm_id
    }

@app.get("/weather")
def get_weather(city: str):
    return {
        "city": city
    }

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id
    }


@app.get("/crop")
def crop(name: str):
    return {
        "crop": name
    }