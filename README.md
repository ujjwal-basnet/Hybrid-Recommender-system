# 🔮 Hybrid Recommender System

A hybrid recommender based on 

- ✅ **Collaborative Filtering**  
  ➕➕➕➕
- ✅ **Content-Based Filtering**

...for a more **personalized** and **dynamic** recommendation system.


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

## ⚠️ Major Challenges

1. Dataset size: roughly 9.7 million records  
 User-item matrix size (unique songs × unique users):  
   - ~60k unique songs  
   - ~1 million unique users  
   - Matrix size ~28 GB — too large to load fully into memory

    **Solution:**  
    - Use **chunking** to process data in parts

2. **weight Assigment** 
- For old users, how to  assign higher weight to collaborative filtering  
 -recent users,how to assign higher weight to content-based filtering
