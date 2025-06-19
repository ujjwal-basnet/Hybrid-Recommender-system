# 🔮 Hybrid Recommender System

A hybrid recommender that mixes:

- ✅ **Collaborative Filtering**  
+  
- ✅ **Content-Based Filtering**

...for a more **personalized** and **dynamic** recommendation system.

---

## ⚙️ Technique Used

**Hybrid → Weighted System**  
`Hybrid Score = w_cb * CB + w_cf * CF`

Example:  
`0.6 * Content-Based + 0.4 * Collaborative`

---

## 📐 Weight Calculation

Weights are based on **similarity scores**, calculated using:

- Euclidean Distance  
- Manhattan Distance  
- **Cosine Similarity** (used here)

---

### ✅ Why Cosine Similarity?

1. Handles the **curse of dimensionality**  
2. Output range: **-1 to 1**  
   - `-1` = completely opposite  
   - `0` = no similarity  
   - `1` = perfect match

---

## 🎯 Project Goals

1. Songs dataset — contains information for all songs on the platform like attributes and metadata (content-based)  
2. User-item interaction — user, song, playcount (collaborative); more playcount means higher preference

**Main goals:**  
- Increase user engagement  
- Increase user subscription retention  
- Develop a more personalized and varied recommendation system

---

## 📁 Dataset

[Million Song Dataset (Spotify + Last.fm)](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm)

---

## 📊 Business Goal Metrics

Spotify revenue streams:  
- Free users (ad-supported)  
- Subscription users (ad-free)

Revenue sources:  
- Ads on free plan  
- Subscription fees on paid plan

### Key metrics:

1. **User Engagement**  
   Free users listen to more songs due to personalized variety.  
   After 3–5 songs, ads are shown; users can upgrade to ad-free subscription.

2. **CTR (Click-Through Rate)**  
   If user is recommended 10 songs and selects the next song, it counts as 1 click.  
   Goal: recommendations are loved and used by users.

3. **User Conversion**  
   Higher engagement in free users leads to higher probability of converting to paid users.

4. **Lower Churn Rate**  
   Retain users by constantly improving recommendations.

---

## 🏗️ Architecture

**Streamlit app** (input → songs)

1. Based on input songs, suggest 10 similar songs and validate  
2. Based on those songs, suggest 10 similar songs others are listening to (item similarity) and validate  
3. Combine weights and build hybrid recommendation

---

## ⚠️ Major Challenges

1. Dataset size: roughly 9.7 million records  
2. User-item matrix size (unique songs × unique users):  
   - ~60k unique songs  
   - ~1 million unique users  
   - Matrix size ~28 GB — too large to load fully into memory

**Solution:**  
- Use **chunking** to process data in parts

3. Weight assignment strategy:  
- For old users, assign higher weight to collaborative filtering  
- For recent users, assign higher weight to content-based filtering

---

