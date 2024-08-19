import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import FeatureCard from "./FeatureCard";
import { Search } from "lucide-react";

const Home = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const playlistIdRegex = /playlist\/([^?]+)/;

  const handleSubmit = (e) => {
    e.preventDefault();

    const match = url.match(playlistIdRegex);
    if (match) {
      setError("");
      navigate(`/analysis/${match ? match[1] : null}`);
    } else {
      setError("Invalid playlist URL. Please try again.");
      setUrl("");
    }
  };

  return (
    <div className="min-h-screen bg-emerald-50 flex flex-col justify-center items-center p-4">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-emerald-800 mb-2">SpotiSight</h1>
        <p className="text-xl text-emerald-600">
          Uncover the insights in your Spotify playlists
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <div className="relative">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste your Spotify playlist URL here"
            className="w-full px-4 py-3 rounded-full border-2 border-emerald-300 focus:outline-none focus:border-emerald-500 text-emerald-800 placeholder-emerald-400"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-emerald-500 text-white p-2 rounded-full hover:bg-emerald-600 transition-colors duration-300"
          >
            <Search size={24} />
          </button>
        </div>
      </form>

      {error && ( // Conditional rendering of the error message
        <div
          className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
          role="alert"
        >
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="mt-12 text-emerald-700 text-center">
        <h2 className="text-2xl font-semibold mb-4">
          Discover Your Playlist's DNA
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon="📊"
            title="Deep Analytics"
            description="Get detailed insights into your playlist's mood, genre distribution, and more."
          />
          <FeatureCard
            icon="🎵"
            title="Track Breakdown"
            description="Analyze individual tracks for their audio features and popularity."
          />
          <FeatureCard
            icon="🔍"
            title="Hidden Gems"
            description="Uncover lesser-known tracks that fit perfectly with your playlist's vibe."
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
