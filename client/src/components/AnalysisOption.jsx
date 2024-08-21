import React from "react";

const AnalysisOption = ({ icon, title, description, onClick }) => {
  return (
    <div
      className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md cursor-pointer transition-all duration-300 hover:shadow-lg hover:bg-emerald-50 dark:hover:bg-gray-700"
      onClick={onClick}
    >
      <div className="text-emerald-500 dark:text-emerald-400 mb-4 transition-colors duration-300">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2 text-emerald-800 dark:text-emerald-300 transition-colors duration-300">
        {title}
      </h3>
      <p className="text-emerald-600 dark:text-emerald-400 transition-colors duration-300">
        {description}
      </p>
    </div>
  );
};

export default AnalysisOption;
