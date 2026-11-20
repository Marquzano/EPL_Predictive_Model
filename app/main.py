from contextlib import asynccontextmanager
from keras.models import load_model
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import predict as predict_routes
from app.api import teams as teams_routes
import joblib
DB_PATH = 'data/processed/EPL_data.db'
FRONTEND_ORIGINS = ['http://localhost:5173']
MODEL_PATH = 'models/epl_2_0_0.keras'
SCALER_PATH = 'models/epl_2_0_0_scaler.joblib'

# create the lifespan of the app
# to provide necessary objects at
# startup and to break it down at
# shutdown
# make it to handle requests and
# responses asynchronously
@asynccontextmanager
async def lifespan(app: FastAPI):
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    yield {'model': model, 'db_path': DB_PATH, 'scaler': scaler}

# make the app instance
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type']
)

# include the current routes for the app
app.include_router(predict_routes.router)
app.include_router(teams_routes.router)