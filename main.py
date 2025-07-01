import os
import logging
import pandas as pd
from scipy.sparse import load_npz
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager

from content_based_filtering import recommend

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Paths
CLEANED_DATA_PATH = "data/cleaned_data.csv"
TRANSFORMED_DATA_PATH = "data/transformed_data.npz"

# Models
class Song(BaseModel):
    name: str
    artist: str
    spotify_id: str

class RecomdationResponse(BaseModel):
    recommendations: List[Song]

# Globals
songs_metadata_df = None
song_features_matrix = None

# Lifespan
@asynccontextmanager
async def load_data_and_model(app: FastAPI):
    global songs_metadata_df, song_features_matrix

    logger.info("Startup: loading data artifacts...")
    if not os.path.exists(CLEANED_DATA_PATH) or not os.path.exists(TRANSFORMED_DATA_PATH):
        logger.error("❌ Data files missing.")
        raise FileNotFoundError("Missing cleaned or transformed data paths.")

    songs_metadata_df = pd.read_csv(CLEANED_DATA_PATH)
    song_features_matrix = load_npz(TRANSFORMED_DATA_PATH)

    logger.info("✅ Data artifacts loaded successfully.")
    yield
    logger.info("❌ Shutdown: App is stopping.")

# App Init
app = FastAPI(
    title="Song Recommendation API",
    description="Uses a content-based model to recommend songs",
    version="1.0",
    lifespan=load_data_and_model
)

# Routes
@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ok", "message": "Welcome! Go to /docs for API usage."}

@app.get("/recommend", response_model=RecomdationResponse, tags=["Recommendations"])
def get_recommendations(song_name: str, k: int = 10):
    if songs_metadata_df is None or song_features_matrix is None:
        raise HTTPException(status_code=503, detail="Server is initializing. Please try again in a moment.")

    recommendations_df = recommend(
        song_name=song_name,
        songs_data=songs_metadata_df,
        transformed_data=song_features_matrix,
        k=k
    )

    if recommendations_df is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_name}' not found in the dataset.")

    return {"recommendations": recommendations_df.to_dict(orient="records")}
