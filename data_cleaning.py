import pandas as pd
import logging

DATA_PATH = "data/Music Info.csv"

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def clean_data(data):

    logger.info(f"Initial data shape: {data.shape}")
    cleaned = (
        data
        .drop_duplicates(subset="track_id")
        .drop(columns=["genre", "spotify_preview_url"], errors="ignore")
        .fillna({"tags": "no_tags"})
        .assign(
            name=lambda x: x["name"].str.lower().str.strip(),
            artist=lambda x: x["artist"].str.lower().str.strip(),
            tags=lambda x: x["tags"].str.lower().str.strip()
        )
        .reset_index(drop=True)
    )
    logger.info(f"After removing duplicates and cleaning: {cleaned.shape}")
    return cleaned

def data_for_content_filtering(data):
    """
    Prepares data for content-based filtering by dropping unnecessary columns.
    """
    logger.info("Dropping columns for content-based filtering.")
    return data.drop(columns=["track_id", "name", "spotify_preview_url"], errors="ignore")

def main(data_path):
    
    logger.info("Loading data...")
    data = pd.read_csv(data_path)
    logger.info(f"Loaded data with shape: {data.shape}")

    cleaned_data = clean_data(data)
    logger.info(f"Saving cleaned data to data/cleaned_data.csv")
    cleaned_data.to_csv("data/cleaned_data.csv", index=False)
    logger.info("Data cleaning complete.")

if __name__ == "__main__":
    main(DATA_PATH)