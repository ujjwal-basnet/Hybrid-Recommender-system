import numpy as np 
import pandas as pd 
import joblib 
from sklearn.preprocessing import MinMaxScaler, StandardScaler, OneHotEncoder 
from category_encoders.count import CountEncoder 
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.compose import ColumnTransformer 
from sklearn.metrics.pairwise import cosine_similarity 
from data_cleaning import data_for_content_filtering  
from scipy.sparse import save_npz 
import logging 
import os 

#logger setup 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger= logging.getLogger(__name__) 

CLEANED_DATA_PATH= "data/cleaned_data.csv" 
TRANSFORMER_PATH = "transformer.joblib"
TRANSFORMED_DATA_PATH = "data/transformed_data.npz"

# Columns to transform 
frequency_encode_cols = ['year']
ohe_cols = ['artist', 'time_signature', 'key']
tfidf_col = 'tags'
standard_scale_cols = ["duration_ms", "loudness", "tempo"]
min_max_scale_cols = ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]   



def train_transformer(data):
    logger.info("Training trasformer... ") 
    
    
    transformer = ColumnTransformer(transformers=[
        ("frequency_encode", CountEncoder(normalize=True), frequency_encode_cols),
        ("ohe", OneHotEncoder(handle_unknown="ignore"), ohe_cols),              
        ("tfidf", TfidfVectorizer(max_features=85), tfidf_col),
        ("standard_scale", StandardScaler(), standard_scale_cols),
        ("min_max_scale", MinMaxScaler(), min_max_scale_cols)
    ], remainder='drop', n_jobs=-1)
    
    transformer.fit(data)
    joblib.dump(transformer , TRANSFORMER_PATH)
    logger.info(f"Transformer saved to {TRANSFORMER_PATH}")
    return transformer 

def transform_data(data):
    logger.info("Loading transformer and transforming data... ") 
    transformer= joblib.load(TRANSFORMER_PATH)
    transformed_data =transformer.transform(data)
    logger.info(f"Transformed data shape: {getattr(transformed_data, 'shape', None)}")
    return transformed_data 

def save_transformed_data(transformed, save_path):
    logger.info(f"Saving transformed data to {save_path}")
    save_npz(save_path, transformed)
    logger.info("Transformed data saved")
    
    
def calculate_similarity_scores(input_vector, data):
    logger.info(f"calculating similarity scores ...")
    if input_vector.ndim== 1:
        input_vector = input_vector.reshape(1, -1)
    
    similarity_scores= cosine_similarity(input_vector, data)
    return similarity_scores

def recommend(song_name, songs_data, transformed_data, k=10):
    """recommend top k similar songs based on content features.

    Args:
        song_name: name of the song to find recommendations for
        songs_data: DataFrame with song metadata (must have 'name', 'artist', 'spotify_id' columns)
        transformed_data: sparse matrix of transformed song features
        k: number of recommendations to return

    Returns:
        DataFrame with top k recommended songs (name, artist, spotify_id), or None if song not found
    """
    song_name = song_name.lower().strip()
    song_row = songs_data[songs_data['name'].str.lower().str.strip() == song_name]

    if song_row.empty:
        logger.warning(f"Song '{song_name}' not found in dataset")
        return None

    song_idx = song_row.index[0]
    input_vector = transformed_data[song_idx].reshape(1, -1)
    similarity_scores = cosine_similarity(input_vector, transformed_data).ravel()

    # argsort ascending, take top k AFTER excluding the input song itself
    # to ensure we get exactly k distinct recommendations
    sorted_indices = np.argsort(similarity_scores)[::-1]  # descending = highest sim first
    mask = sorted_indices != song_idx
    filtered_indices = sorted_indices[mask][:k]

    recommendations = songs_data.iloc[filtered_indices][['name', 'artist', 'spotify_id']].reset_index(drop=True)
    logger.info(f"Top {k} recommendations for '{song_name}':\n{recommendations}")
    return recommendations


def recommend_by_artist(artist_name, songs_data, transformed_data, k=10):
    """Recommend top k songs by the same or similar artist."""
    artist_name = artist_name.lower().strip()
    artist_songs = songs_data[songs_data['artist'].str.lower().str.strip() == artist_name]

    if artist_songs.empty:
        logger.warning(f"Artist '{artist_name}' not found in dataset")
        return None

    song_idx = artist_songs.index[0]
    input_vector = transformed_data[song_idx].reshape(1, -1)
    similarity_scores = cosine_similarity(input_vector, transformed_data).ravel()

    sorted_indices = np.argsort(similarity_scores)[::-1]
    mask = sorted_indices != song_idx
    filtered_indices = sorted_indices[mask][:k]

    recommendations = songs_data.iloc[filtered_indices][['name', 'artist', 'spotify_id']].reset_index(drop=True)
    logger.info(f"Top {k} songs similar to artist '{artist_name}':\n{recommendations}")
    return recommendations


def recommend_by_tags(tag_query, songs_data, transformed_data, k=10):
    """Recommend top k songs matching a tag query (comma-separated).

    Example: recommend_by_tags("rock, indie", songs_data, transformed_data)
    """
    tag_query = tag_query.lower().strip()
    query_tags = set(t.strip() for t in tag_query.split(','))

    song_row = songs_data[songs_data['tags'].str.lower().str.contains('|'.join(query_tags), na=False)]

    if song_row.empty:
        logger.warning(f"No songs found with tags matching '{tag_query}'")
        return None

    song_idx = song_row.index[0]
    input_vector = transformed_data[song_idx].reshape(1, -1)
    similarity_scores = cosine_similarity(input_vector, transformed_data).ravel()

    sorted_indices = np.argsort(similarity_scores)[::-1]
    mask = sorted_indices != song_idx
    filtered_indices = sorted_indices[mask][:k]

    recommendations = songs_data.iloc[filtered_indices][['name', 'artist', 'spotify_id', 'tags']].reset_index(drop=True)
    logger.info(f"Top {k} songs matching tags '{tag_query}':\n{recommendations}")
    return recommendations 


def main(data_path, song_name, k=10):
    """ main function to run the content filtering pipeline"""
    
    logger.info(f"Loading data from {data_path}")
    
    #check data path is valid or not 
    if not os.path.exists(data_path):
        logger.error(f"Data file {data_path} does't exists ")
        return 
    
    data = pd.read_csv(data_path)
    logger.info(f"Loaded data with shape: {data.shape}")
    data_content_filtering = data_for_content_filtering(data)
    train_transformer(data_content_filtering)
    transformed_data = transform_data(data_content_filtering)
    save_transformed_data(transformed_data, TRANSFORMED_DATA_PATH)
    recommendations = recommend(song_name, data, transformed_data, k)
    if recommendations is not None:
        print(recommendations)  #optional: could save to file or return

if __name__ == "__main__":
    main(CLEANED_DATA_PATH, "Hips Don't Lie")
