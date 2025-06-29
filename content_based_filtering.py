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
logging.basicConfig(Level=logging.INFO , format="%(asctime)s - %(levelname)s - %(message)s")
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
        ("frequency_encode", CountEncoder(normalize=True, return_df=True), frequency_encode_cols),
        ("ohe", OneHotEncoder(handle_unknown="ignore"), ohe_cols),              
        ("tfidf", TfidfVectorizer(max_features=85), tfidf_col),
        ("standard_scale", StandardScaler(), standard_scale_cols),
        ("min_max_scale", MinMaxScaler(), min_max_scale_cols)
    ], remainder='passthrough', n_jobs=-1)
    
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
        input_vector = input_vector.reshpae(1, -1)
    
    similarity_scores= cosine_similarity(input_vector, data)
    return similarity_scores

def recommend(song_name, songs_data, transformed_data, k=10):
    """ recommend top k (say 10) similar songs based on content features """
    song_name= song_name.lower() 
    song_row= songs_data.loc[songs_data['name'].str.lower() == song_name]
    
    if song_row.empty:
        logger.warning(f"song {song_name} not found in dataset")
        return None 
    
    song_index= song_row.index[0]
    input_vector= transformed_data[song_index].reshape(1, -1)
    similarity_scores= calculate_similarity_scores(input_vector , transformed_data)
    
    
    top_k_songs_indices= np.argsort(similarity_scores.ravel()[::-1])
    
    ####### Execute the input songs Itself 
    
    top_k_songs_indices= top_k_songs_indices[top_k_songs_indices != song_index][:k] 
    
    """ 
    say top k songs indicies are [ 4 ,5 1 ,3 ,6] 
    now , our songs indicies is say 3 , and since coisne similarty between same songs are always high so we filter
    filter usign != song_index
    this wil give array true , true ,false , true , true 
    now doing [:k] i.e say we need top 3 number so [:3]
     wil give first 3 true values """
     
     
    top_k_songs_names= songs_data.iloc[top_k_songs_indices]
    top_k_list= top_k_songs_names[['name' , 'artist' , 'spotify_preview_url']].reset_index(drop= True)
    logger.info(f"Top {k} recommendations for {song_name} :\n {top_k_list}")
    return top_k_list 


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
