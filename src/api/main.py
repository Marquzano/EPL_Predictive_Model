from contextlib import asynccontextmanager
from data_transform import make_features_and_labels
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from fastapi import FastAPI
from api.routes import predict as predict_routes
import sqlite3

@asynccontextmanager
async def lifespan(app: FastAPI):
    model = load_model('models/epl_1_0_4.keras')
    con = sqlite3.connect('data/processed/EPL_data.db')
    training_features, *_ = make_features_and_labels(con)
    scaler = StandardScaler().fit(training_features)

    yield {'model': model, 'con': con, 'scaler': scaler}

    con.close()

app = FastAPI(lifespan=lifespan)

app.include_router(predict_routes.router)