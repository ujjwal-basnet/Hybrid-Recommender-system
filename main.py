import os
import logging
import pandas as pd
from scipy.sparse import load_npz
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from contextlib import asynccontextmanager

from content_based_filtering import recommend, recommend_by_artist, recommend_by_tags

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CLEANED_DATA_PATH = "data/cleaned_data.csv"
TRANSFORMED_DATA_PATH = "data/transformed_data.npz"

songs_metadata_df = None
song_features_matrix = None


class Song(BaseModel):
    name: str
    artist: str
    spotify_id: str


class SongWithTags(Song):
    tags: str | None = None


class RecommendationResponse(BaseModel):
    recommendations: List[Song]


class RecommendationWithTagsResponse(BaseModel):
    recommendations: List[SongWithTags]


@asynccontextmanager
async def load_data_and_model(app: FastAPI):
    global songs_metadata_df, song_features_matrix
    logger.info("Loading data artifacts...")
    if not os.path.exists(CLEANED_DATA_PATH) or not os.path.exists(TRANSFORMED_DATA_PATH):
        logger.error("Required data files missing.")
        raise FileNotFoundError("Missing cleaned or transformed data files.")
    songs_metadata_df = pd.read_csv(CLEANED_DATA_PATH)
    song_features_matrix = load_npz(TRANSFORMED_DATA_PATH)
    logger.info("Data artifacts loaded successfully.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Song Recommendation API",
    description="Content-based song recommendation API",
    version="1.0",
    lifespan=load_data_and_model,
)


@app.get("/", tags=["Status"])
def read_root():
    return {"status": "ok", "message": "Welcome! Go to /docs for API usage."}


@app.get("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations(song_name: str, k: int = 10):
    """Get top-k songs similar to the given song."""
    if songs_metadata_df is None or song_features_matrix is None:
        raise HTTPException(status_code=503, detail="Server is initializing. Please try again.")
    if k < 1 or k > 100:
        raise HTTPException(status_code=400, detail="k must be between 1 and 100.")
    recommendations_df = recommend(song_name, songs_metadata_df, song_features_matrix, k)
    if recommendations_df is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_name}' not found in dataset.")
    return {"recommendations": recommendations_df.to_dict(orient="records")}


@app.get("/recommend/by-artist", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations_by_artist(artist_name: str, k: int = 10):
    """Get top-k songs similar to the given artist."""
    if songs_metadata_df is None or song_features_matrix is None:
        raise HTTPException(status_code=503, detail="Server is initializing. Please try again.")
    if k < 1 or k > 100:
        raise HTTPException(status_code=400, detail="k must be between 1 and 100.")
    recommendations_df = recommend_by_artist(artist_name, songs_metadata_df, song_features_matrix, k)
    if recommendations_df is None:
        raise HTTPException(status_code=404, detail=f"Artist '{artist_name}' not found in dataset.")
    return {"recommendations": recommendations_df.to_dict(orient="records")}


@app.get("/recommend/by-tags", response_model=RecommendationWithTagsResponse, tags=["Recommendations"])
def get_recommendations_by_tags(tag_query: str, k: int = 10):
    """Get top-k songs matching the given tag(s). Comma-separated for multiple tags."""
    if songs_metadata_df is None or song_features_matrix is None:
        raise HTTPException(status_code=503, detail="Server is initializing. Please try again.")
    if k < 1 or k > 100:
        raise HTTPException(status_code=400, detail="k must be between 1 and 100.")
    recommendations_df = recommend_by_tags(tag_query, songs_metadata_df, song_features_matrix, k)
    if recommendations_df is None:
        raise HTTPException(status_code=404, detail=f"No songs found matching tags '{tag_query}'.")
    return {"recommendations": recommendations_df.to_dict(orient="records")}


@app.get("/songs/search", response_model=List[Song], tags=["Search"])
def search_songs(q: str, limit: int = 10):
    """Search songs by name (partial match)."""
    if songs_metadata_df is None:
        raise HTTPException(status_code=503, detail="Server is initializing.")
    q = q.lower().strip()
    matches = songs_metadata_df[songs_metadata_df['name'].str.lower().str.contains(q, na=False)]
    results = matches[['name', 'artist', 'spotify_id']].head(limit).to_dict(orient="records")
    return results
