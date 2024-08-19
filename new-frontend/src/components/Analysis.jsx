import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import AnalysisOption from "./AnalysisOption";
import { BarChart, Music, Lightbulb } from "lucide-react";

const Analysis = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Placeholder data - replace with actual API calls
  const playlistData = {
    name: "Awesome Playlist",
    description: "A collection of my favorite tracks",
    trackCount: 50,
    followerCount: 1000,
    imageUrl: "https://picsum.photos/400",
  };

  return (
    <div className="min-h-screen bg-emerald-50 flex flex-col items-center p-8">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-emerald-800 mb-2">SpotiSight</h1>
        <p className="text-xl text-emerald-600">Playlist Analysis</p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl w-full">
        <div className="flex flex-col md:flex-row gap-8">
          <img
            src={playlistData.imageUrl}
            alt="Playlist Cover"
            className="w-64 h-64 object-cover rounded-lg shadow-md"
          />
          <div className="flex flex-col justify-center">
            <h2 className="text-3xl font-bold text-emerald-800 mb-2">
              {playlistData.name}
            </h2>
            <p className="text-emerald-600 mb-4">{playlistData.description}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-emerald-500">Tracks</p>
                <p className="text-2xl font-semibold">
                  {playlistData.trackCount}
                </p>
              </div>
              <div>
                <p className="text-sm text-emerald-500">Followers</p>
                <p className="text-2xl font-semibold">
                  {playlistData.followerCount}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-12 text-emerald-700 text-center w-full max-w-4xl">
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

export default Analysis;
