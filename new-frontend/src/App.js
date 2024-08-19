import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./components/Home";
import Analysis from "./components/Analysis";
import DeepAnalytics from "./components/DeepAnalytics";
import TrackBreakdown from "./components/TrackBreakdown";
import HiddenGems from "./components/HiddenGems";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/analysis/:id" element={<Analysis />} />
        <Route path="/deep-analytics/:id" element={<DeepAnalytics />} />
        <Route path="/track-breakdown/:id" element={<TrackBreakdown />} />
        <Route path="/hidden-gems/:id" element={<HiddenGems />} />
      </Routes>
    </Router>
  );
};

export default App;
