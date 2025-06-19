# 🔮 Hybrid Recommender System

A simple hybrid recommender that mixes:

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

1. Handles **curse of dimensionality**  
2. Output range: **-1 to 1**  
   - `-1` = completely opposite  
   - `0` = no similarity  
   - `1` = perfect match

