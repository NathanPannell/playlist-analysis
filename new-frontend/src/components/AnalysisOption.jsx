import React from "react";

const AnalysisOption = ({ icon, title, description, onClick }) => {
  return (
    <div
      className="bg-white p-6 rounded-lg shadow-md cursor-pointer transition-all duration-300 hover:shadow-lg hover:bg-emerald-50"
      onClick={onClick}
    >
      <div className="text-emerald-500 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-emerald-800">{title}</h3>
      <p className="text-emerald-600">{description}</p>
    </div>
  );
};

export default AnalysisOption;
