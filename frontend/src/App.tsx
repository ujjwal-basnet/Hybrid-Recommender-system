import { useState, useRef } from 'react';
import { Search, Music, Mic2, Tag, Disc3, Loader2, AlertCircle } from 'lucide-react';
import { getRecommendations, getRecommendationsByArtist, getRecommendationsByTags } from './api/recommendations';
import type { Song, SongWithTags } from './api/recommendations';
import './App.css';

type Mode = 'song' | 'artist' | 'tags';

function App() {
  const [mode, setMode] = useState<Mode>('song');
  const [query, setQuery] = useState('');
  const [k, setK] = useState(10);
  const [results, setResults] = useState<(Song | SongWithTags)[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const modeConfig = {
    song: { icon: <Music size={18} />, label: 'By Song', placeholder: 'e.g. Wonderwall, Hips Don\'t Lie...', api: getRecommendations },
    artist: { icon: <Mic2 size={18} />, label: 'By Artist', placeholder: 'e.g. Oasis, Radiohead...', api: getRecommendationsByArtist },
    tags: { icon: <Tag size={18} />, label: 'By Tags', placeholder: 'e.g. rock, indie, pop...', api: getRecommendationsByTags },
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
      setResults(data);
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
    <div className="app">
      <div className="noise-overlay" />
      <header className="header">
        <div className="logo">
          <Disc3 size={32} className="logo-icon" />
          <h1>Sonara</h1>
        </div>
        <p className="tagline">Discover your next favorite track</p>
      </header>

      <main className="main">
        <div className="mode-tabs">
          {(Object.keys(modeConfig) as Mode[]).map(m => (
            <button
              key={m}
              className={`mode-tab ${mode === m ? 'active' : ''}`}
              onClick={() => { setMode(m); setResults([]); setError(null); }}
            >
              {modeConfig[m].icon}
              <span>{modeConfig[m].label}</span>
            </button>
          ))}
        </div>

        <form className="search-form" onSubmit={handleSearch}>
          <div className="search-row">
            <Search size={20} className="search-icon" />
            <input
              ref={inputRef}
              type="text"
              placeholder={modeConfig[mode].placeholder}
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="search-input"
            />
            <select
              value={k}
              onChange={e => setK(Number(e.target.value))}
              className="k-select"
            >
              {[5, 10, 15, 20, 30, 50].map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
            <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
              {loading ? <Loader2 size={20} className="spin" /> : 'Discover'}
            </button>
          </div>
        </form>

        {searchHistory.length > 0 && results.length === 0 && (
          <div className="history">
            <span className="history-label">Recent:</span>
            {searchHistory.map(h => (
              <button key={h} className="history-chip" onClick={() => handleHistoryClick(h)}>{h}</button>
            ))}
          </div>
        )}

        {error && (
          <div className="error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {results.length > 0 && (
          <div className="results">
            <div className="results-header">
              <h2>
                {mode === 'song' && `Songs similar to "${query}"`}
                {mode === 'artist' && `Top tracks by "${query}"`}
                {mode === 'tags' && `Tracks tagged "${query}"`}
              </h2>
              <span className="count">{results.length} tracks</span>
            </div>
            <div className="track-list">
              {results.map((song, i) => (
                <div
                  key={`${song.spotify_id}-${i}`}
                  className="track-card"
                  style={{ animationDelay: `${i * 60}ms` }}
                >
                  <div className="track-rank">#{i + 1}</div>
                  <div className="track-info">
                    <div className="track-name">{song.name}</div>
                    <div className="track-artist">{song.artist}</div>
                    {'tags' in song && song.tags && (
                      <div className="track-tags">
                        {String(song.tags).split(',').slice(0, 3).map((tag: string) => (
                          <span key={tag} className="tag-chip">{tag.trim()}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <a
                    href={`https://open.spotify.com/track/${song.spotify_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="spotify-link"
                  >
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
                    </svg>
                    Play
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
