from contextlib import asynccontextmanager
from pipeline.data_transform import make_features_and_labels
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from fastapi import FastAPI
from app.api import predict as predict_routes
import sqlite3
DB_PATH = 'data/processed/EPL_data.db'

# create the lifespan of the app
# to provide necessary objects at
# startup and to break it down at
# shutdown
# make it to handle requests and
# responses asynchronously
@asynccontextmanager
async def lifespan(app: FastAPI):
    model = load_model('models/epl_1_0_4.keras')
    con = sqlite3.connect(DB_PATH)
    try:
        training_features, *_ = make_features_and_labels(con)
        scaler = StandardScaler().fit(training_features)
    finally:
        con.close()

    yield {'model': model, 'db_path': DB_PATH, 'scaler': scaler}

# make the app instance
app = FastAPI(lifespan=lifespan)

# include the current routes for the app
app.include_router(predict_routes.router)