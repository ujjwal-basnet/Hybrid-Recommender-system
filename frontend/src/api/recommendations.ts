export interface Song {
  name: string;
  artist: string;
  spotify_id: string;
}

export interface SongWithTags extends Song {
  tags: string | null;
}

export interface RecommendationResponse {
  recommendations: Song[];
}

export interface RecommendationWithTagsResponse {
  recommendations: SongWithTags[];
}

const BASE_URL = '';

export async function getRecommendations(songName: string, k = 10): Promise<Song[]> {
  const res = await fetch(`${BASE_URL}/recommend?song_name=${encodeURIComponent(songName)}&k=${k}`);
  if (!res.ok) throw new Error(`Failed to fetch recommendations: ${res.status}`);
  const data: RecommendationResponse = await res.json();
  return data.recommendations;
}

export async function getRecommendationsByArtist(artistName: string, k = 10): Promise<Song[]> {
  const res = await fetch(`${BASE_URL}/recommend/by-artist?artist_name=${encodeURIComponent(artistName)}&k=${k}`);
  if (!res.ok) throw new Error(`Failed to fetch recommendations: ${res.status}`);
  const data: RecommendationResponse = await res.json();
  return data.recommendations;
}

export async function getRecommendationsByTags(tagQuery: string, k = 10): Promise<SongWithTags[]> {
  const res = await fetch(`${BASE_URL}/recommend/by-tags?tag_query=${encodeURIComponent(tagQuery)}&k=${k}`);
  if (!res.ok) throw new Error(`Failed to fetch recommendations: ${res.status}`);
  const data: RecommendationWithTagsResponse = await res.json();
  return data.recommendations;
}

export async function searchSongs(query: string, limit = 10): Promise<Song[]> {
  const res = await fetch(`${BASE_URL}/songs/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to search songs: ${res.status}`);
  return res.json();
}
