import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { BarChart, Music, Lightbulb, Moon, Sun, Home } from "lucide-react";
import AnalysisOption from "./AnalysisOption";

const decodeText = (text) => {
  const tempElement = document.createElement("textarea");
  tempElement.innerHTML = text;
  return tempElement.value;
};

const Analysis = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [playlist, setPlaylist] = useState({
    title: "",
    description: "",
    followerCount: "",
    trackCount: "",
    imageUrl: "",
    duration: "",
    topGenres: [{ name: "" }],
    topArtists: [{ name: "" }],
  });
  const [darkMode, setDarkMode] = useState(() => {
    const savedMode = localStorage.getItem("darkMode");
    return savedMode ? JSON.parse(savedMode) : false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };

  useEffect(() => {
    const fetchPlaylist = async () => {
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: id }),
      };
      const response = await fetch(`http://127.0.0.1:5000/playlist`, options);
      const response_body = await response.json();
      if (!response.ok) {
        alert(response_body.message);
      } else {
        setPlaylist(response_body.data);
      }
    };

    fetchPlaylist();
  }, [id]);

  const parseDuration = (duration) => {
    const minutes = Math.floor(duration / 60) % 60;
    const hours = Math.floor(duration / 3600);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="min-h-screen bg-emerald-50 dark:bg-gray-900 flex flex-col items-center p-8 transition-colors duration-300">
      <Link
        to="/"
        className="absolute top-4 left-4 p-2 rounded-full bg-emerald-200 dark:bg-gray-700 text-emerald-800 dark:text-emerald-200 transition-colors duration-300"
      >
        <Home size={24} />
      </Link>
      <button
        onClick={toggleDarkMode}
        className="absolute top-4 right-4 p-2 rounded-full bg-emerald-200 dark:bg-gray-700 text-emerald-800 dark:text-emerald-200 transition-colors duration-300"
      >
        {darkMode ? <Sun size={24} /> : <Moon size={24} />}
      </button>
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-emerald-800 dark:text-emerald-300 mb-2 transition-colors duration-300">
          SpotiSight
        </h1>
        <p className="text-xl text-emerald-600 dark:text-emerald-400 transition-colors duration-300">
          Playlist Analysis
        </p>
      </div>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 max-w-4xl w-full transition-colors duration-300">
        <div className="flex flex-col md:flex-row gap-8">
          <img
            src={playlist.imageUrl}
            alt="Playlist Cover"
            className="w-64 h-64 object-cover rounded-lg shadow-md"
          />
          <div className="flex flex-col justify-center">
            <h2 className="text-3xl font-bold text-emerald-800 dark:text-emerald-300 mb-2 transition-colors duration-300">
              {decodeText(playlist.title)}
            </h2>
            <p className="text-emerald-600 dark:text-emerald-400 mb-4 transition-colors duration-300">
              {decodeText(playlist.description)}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <InfoItem label="Tracks" value={playlist.trackCount} />
              <InfoItem label="Followers" value={playlist.followerCount} />
              <InfoItem
                label="Duration"
                value={parseDuration(playlist.duration)}
              />
              <InfoItem
                label="Top Artist"
                value={playlist.topArtists[0].name}
              />
              <InfoItem label="Top Genre" value={playlist.topGenres[0].name} />
            </div>
          </div>
        </div>
      </div>
      <div className="mt-12 text-emerald-700 dark:text-emerald-300 text-center w-full max-w-4xl transition-colors duration-300">
        <h2 className="text-2xl font-semibold mb-4">Choose Your Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <AnalysisOption
            icon={<BarChart className="w-12 h-12" />}
            title="Deep Analytics"
            description="Get detailed insights into your playlist's mood, genre distribution, and more."
            onClick={() => navigate(`/deep-analytics/${id}`)}
          />
          <AnalysisOption
            icon={<Music className="w-12 h-12" />}
            title="Track Breakdown"
            description="Analyze individual tracks for their audio features and popularity."
            onClick={() => navigate(`/track-breakdown/${id}`)}
          />
          <AnalysisOption
            icon={<Lightbulb className="w-12 h-12" />}
            title="Hidden Gems"
            description="Uncover lesser-known tracks that fit perfectly with your playlist's vibe."
            onClick={() => navigate(`/hidden-gems/${id}`)}
          />
        </div>
      </div>
    </div>
  );
};

const InfoItem = ({ label, value }) => (
  <div>
    <p className="text-sm text-emerald-500 dark:text-emerald-400 transition-colors duration-300">
      {label}
    </p>
    <p className="text-lg font-semibold text-emerald-800 dark:text-emerald-200 transition-colors duration-300">
      {value}
    </p>
  </div>
);

export default Analysis;
