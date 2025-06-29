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
    """
    Cleans the input DataFrame by performing the following operations:
    1. Removes duplicate rows based on the 'track_id' column.
    2. Drops the 'genre' and 'spotify_id' columns.
    3. Fills missing values in the 'tags' column with the string 'no_tags'.
    4. Converts the 'name', 'artist', and 'tags' columns to lowercase and strips whitespace.
    5. Removes songs with duration_ms > 20 minutes (optional).
    """
    logger.info(f"Initial data shape: {data.shape}")
    cleaned = (
        data
        .drop_duplicates(subset="track_id")
        .drop(columns=["genre", "spotify_id"], errors="ignore")
        .fillna({"tags": "no_tags"})
        .assign(
            name=lambda x: x["name"].str.lower().str.strip(),
            artist=lambda x: x["artist"].str.lower().str.strip(),
            tags=lambda x: x["tags"].str.lower().str.strip()
        )
        .reset_index(drop=True)
    )
    logger.info(f"After removing duplicates and cleaning: {cleaned.shape}")
    # Optional: Remove songs longer than 20 minutes
    if "duration_ms" in cleaned.columns:
        before = cleaned.shape[0]
        cleaned = cleaned[cleaned["duration_ms"] < 20 * 60 * 1000]
        after = cleaned.shape[0]
        logger.info(f"Removed {before - after} songs with duration > 20 min. New shape: {cleaned.shape}")
    return cleaned

def data_for_content_filtering(data):
    """
    Prepares data for content-based filtering by dropping unnecessary columns.
    """
    logger.info("Dropping columns for content-based filtering.")
    return data.drop(columns=["track_id", "name", "spotify_preview_url"], errors="ignore")

def main(data_path):
    """
    Main function to load, clean, and save data.
    """
    logger.info("Loading data...")
    data = pd.read_csv(data_path)
    logger.info(f"Loaded data with shape: {data.shape}")

    cleaned_data = clean_data(data)
    logger.info(f"Saving cleaned data to data/cleaned_data.csv")
    cleaned_data.to_csv("data/cleaned_data.csv", index=False)
    logger.info("Data cleaning complete.")

if __name__ == "__main__":
    main(DATA_PATH)






