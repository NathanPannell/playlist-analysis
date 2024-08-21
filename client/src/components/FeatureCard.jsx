import React from "react";

const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-colors duration-300">
    <div className="text-4xl mb-2">{icon}</div>
    <h3 className="text-xl font-semibold mb-2 text-emerald-800 dark:text-emerald-300">
      {title}
    </h3>
    <p className="text-emerald-600 dark:text-emerald-400">{description}</p>
  </div>
);
export default FeatureCard;
