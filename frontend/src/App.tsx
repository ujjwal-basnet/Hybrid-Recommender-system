import { useState, useRef } from 'react';
import { getRecommendations, getRecommendationsByArtist, getRecommendationsByTags } from './api/recommendations';
import type { Song, SongWithTags } from './api/recommendations';

type Mode = 'song' | 'artist' | 'tags';

interface Track {
  id: string;
  name: string;
  artist: string;
  albumArt?: string;
}

// Fallback images if iTunes doesn't have the song
const getFallbackImage = (index: number): string => {
  const images = [
    'https://images.unsplash.com/photo-1518834107812-67b0a7ba91f8?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1459749411177-0473ef7161ce?w=200&h=200&fit=crop',
  ];
  return images[index % images.length];
};

// Fetch album art from iTunes API (free, no key needed)
const fetchAlbumArtFromiTunes = async (songName: string, artist: string): Promise<string | null> => {
  try {
    const searchTerm = encodeURIComponent(`${songName} ${artist}`);
    const response = await fetch(
      `https://itunes.apple.com/search?term=${searchTerm}&limit=1&media=music&entity=song`
    );
    const data = await response.json();
    if (data.results && data.results.length > 0) {
      return data.results[0].artworkUrl100?.replace('100x100bb', '300x300bb') || null;
    }
  } catch (error) {
    console.error('Error fetching album art:', error);
  }
  return null;
};

function App() {
  const [mode, setMode] = useState<Mode>('song');
  const [query, setQuery] = useState('');
  const [k] = useState(10);
  const [results, setResults] = useState<Track[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const modeConfig = {
    song: { label: 'By Song', placeholder: "What's the mood today?", api: getRecommendations },
    artist: { label: 'By Artist', placeholder: "Which artist speaks to you?", api: getRecommendationsByArtist },
    tags: { label: 'By Tags', placeholder: "Describe the vibe you're after...", api: getRecommendationsByTags },
  };

  const transformResults = async (data: (Song | SongWithTags)[]): Promise<Track[]> => {
    const tracks: Track[] = data.map((song, index) => ({
      id: song.spotify_id || `${song.name}-${index}`,
      name: song.name,
      artist: song.artist,
      albumArt: getFallbackImage(index),
    }));

    // Fetch real album art from iTunes in parallel
    const artPromises = tracks.map(async (track) => {
      const artUrl = await fetchAlbumArtFromiTunes(track.name, track.artist);
      if (artUrl) {
        track.albumArt = artUrl;
      }
      return track;
    });

    return Promise.all(artPromises);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const apiFn = modeConfig[mode].api;
      let data: (Song | SongWithTags)[];
      if (mode === 'tags') {
        data = await (apiFn as (q: string, k: number) => Promise<SongWithTags[]>)(query, k);
      } else {
        data = await (apiFn as (q: string, k: number) => Promise<Song[]>)(query, k);
      }
      const transformed = await transformResults(data);
      setResults(transformed);
      if (!searchHistory.includes(query.toLowerCase())) {
        setSearchHistory(prev => [query.toLowerCase(), ...prev].slice(0, 8));
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.message.includes('404')) {
        setError('Not found — try a different query');
      } else {
        setError('Failed to fetch recommendations. Is the server running on port 8005?');
      }
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (term: string) => {
    setQuery(term);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-on-surface">
      {/* Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass tonal-shift-header">
        <div className="flex justify-between items-center w-full px-8 py-4 max-w-full mx-auto">
          <div className="flex items-center gap-8 flex-1">
            <span className="text-2xl font-black text-primary-container tracking-tighter">Sonara</span>

            {/* Search Container */}
            <div className="flex-grow max-w-xl mx-8 relative">
              <form onSubmit={handleSearch} className="flex items-center bg-surface-container-low rounded-full px-5 py-2 border border-outline-variant/30 focus-within:border-primary-container transition-all">
                <span className="material-symbols-outlined text-outline mr-3 text-xl">search</span>
                <input
                  ref={inputRef}
                  type="text"
                  className="bg-transparent border-none focus:ring-0 text-sm w-full font-medium text-on-surface placeholder-on-surface-variant/50 outline-none"
                  placeholder={modeConfig[mode].placeholder}
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                />
                <div className="flex gap-2 ml-4 border-l border-outline-variant/30 pl-4">
                  <button
                    type="button"
                    onClick={() => setMode('song')}
                    className={`text-[10px] uppercase font-bold tracking-wider px-3 py-1 rounded-full transition-all ${
                      mode === 'song' ? 'bg-primary-container text-white' : 'text-on-surface-variant hover:bg-surface-container'
                    }`}
                  >
                    By Song
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('artist')}
                    className={`text-[10px] uppercase font-bold tracking-wider px-3 py-1 rounded-full transition-all ${
                      mode === 'artist' ? 'bg-primary-container text-white' : 'text-on-surface-variant hover:bg-surface-container'
                    }`}
                  >
                    By Artist
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Results Count */}
          {results.length > 0 && (
            <span className="text-sm font-medium text-on-surface-variant">
              {results.length} tracks
            </span>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-grow pt-32 pb-20 px-8 max-w-7xl mx-auto w-full">
        {/* Empty State */}
        {results.length === 0 && !loading && !error && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="w-24 h-24 mb-8 bg-surface-container-low rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-5xl text-primary-container">music_note</span>
            </div>
            <h2 className="text-4xl font-extrabold text-primary-container tracking-tight mb-4">
              Discover Your Sound
            </h2>
            <p className="text-lg text-on-surface-variant max-w-md">
              Search for songs, artists, or vibes to find your next musical obsession.
            </p>

            {/* Search History */}
            {searchHistory.length > 0 && (
              <div className="mt-12 flex flex-wrap gap-3 justify-center">
                <span className="text-xs font-bold text-outline uppercase tracking-widest self-center">Recent:</span>
                {searchHistory.map((h) => (
                  <button
                    key={h}
                    onClick={() => handleHistoryClick(h)}
                    className="px-4 py-2 bg-surface-container-low hover:bg-surface-container-high rounded-full text-sm font-medium text-on-surface-variant transition-colors"
                  >
                    {h}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="w-12 h-12 border-4 border-primary-container/20 border-t-primary-container rounded-full animate-spin mb-4"></div>
            <p className="text-on-surface-variant font-medium">Curating your playlist...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <span className="material-symbols-outlined text-5xl text-error mb-4">error_outline</span>
            <p className="text-lg text-on-surface mb-2">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-4 px-6 py-2 bg-primary-container text-white rounded-full font-medium hover:opacity-90 transition-opacity"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <>
            {/* Header Section */}
            <header className="mb-16">
              <div className="flex flex-col gap-2">
                <span className="text-secondary font-bold tracking-widest text-xs uppercase">Curated Discovery</span>
                <h1 className="text-5xl md:text-7xl font-extrabold text-primary-container tracking-tighter leading-tight max-w-3xl">
                  {mode === 'song' && `Songs similar to "${query}"`}
                  {mode === 'artist' && `Top tracks by "${query}"`}
                  {mode === 'tags' && `Tracks tagged "${query}"`}
                </h1>
              </div>
            </header>

            {/* Results List */}
            <section className="flex flex-col gap-8">
              {results.map((track) => (
                <div
                  key={track.id}
                  className="group flex flex-col md:flex-row items-start md:items-center justify-between gap-6 p-4 -mx-4 rounded-xl transition-all duration-300 hover:bg-surface-container-low"
                >
                  <div className="flex items-center gap-8 w-full md:w-auto">
                    {/* Album Art */}
                    <div className="relative w-24 h-24 flex-shrink-0">
                      <img
                        src={track.albumArt}
                        alt={`${track.name} cover`}
                        className="w-full h-full object-cover rounded-lg shadow-sm"
                      />
                    </div>

                    {/* Track Info */}
                    <div className="flex flex-col gap-1">
                      <h2 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight group-hover:text-primary-container transition-colors">
                        {track.name}
                      </h2>
                      <p className="text-lg text-on-surface-variant font-medium">{track.artist}</p>
                    </div>
                  </div>

                  {/* Spotify Link */}
                  <div className="flex items-center w-full md:w-auto justify-end px-4 md:px-0">
                    <a
                      href={`https://open.spotify.com/track/${track.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center rounded-full bg-[#1DB954] text-white hover:opacity-90 transition-all hover-scale-102 w-14 h-14"
                      title="Open in Spotify"
                    >
                      <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                        <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                      </svg>
                    </a>
                  </div>
                </div>
              ))}
            </section>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-low py-12 px-8 flex flex-col md:flex-row justify-between items-center w-full gap-4 mt-auto">
        <div className="flex flex-col items-center md:items-start gap-2">
          <span className="font-bold text-primary-container text-xl">Sonara Muse</span>
          <p className="text-sm tracking-wide text-on-surface/70">© 2024 Sonara Muse. All rights reserved.</p>
        </div>
        <div className="flex gap-8">
          <a href="#" className="text-sm tracking-wide text-on-surface/70 hover:text-primary-container transition-colors">Privacy</a>
          <a href="#" className="text-sm tracking-wide text-on-surface/70 hover:text-primary-container transition-colors">Terms</a>
          <a href="#" className="text-sm tracking-wide text-on-surface/70 hover:text-primary-container transition-colors">API</a>
        </div>
      </footer>
    </div>
  );
}

export default App;
