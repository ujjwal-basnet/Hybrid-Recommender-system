# Hybrid Recommender System

A music recommendation system with a beautiful glassmorphic UI.

![Sonara Screenshot](screenshot.jpg)

![Search by song](screenshot2.jpg)

![Search by artist](screenshot3.jpg)

## About

Hybrid recommender system combining collaborative and content-based filtering to suggest songs based on:
- Similar songs
- Artists
- Tags/moods

## Project Structure

```
├── frontend/              # React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── App.tsx
│   │   └── api/
│   └── package.json
├── main.py                # FastAPI backend
├── content_based_filtering.py
└── data/                  # Dataset files
```

## Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS v4
- **Backend**: FastAPI + Python
- **Data**: Million Song Dataset (Spotify + Last.fm)
- **Images**: iTunes API (free, no key)

## How to Run

### 1. Backend

```bash
source recom-env/bin/activate
uvicorn main:app --port 8005 --reload
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

## Features

- Search by song, artist, or tags
- Real album artwork from iTunes
- Direct Spotify links
- Glassmorphic emerald UI
