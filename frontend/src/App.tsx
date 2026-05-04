/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { LandingPage } from './components/LandingPage';
import { AnalysisWorkspace } from './components/AnalysisWorkspace';
import { AnimatePresence, motion } from 'motion/react';
import { useEffect } from 'react';
import { pingHealth } from './services/apiService';

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <LandingPage />
          </motion.div>
        } />
        <Route path="/workspace" element={
          <motion.div
            key="workspace"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <AnalysisWorkspace />
          </motion.div>
        } />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  useEffect(() => {
    // Bangunkan backend Azure saat aplikasi pertama kali dimuat
    pingHealth();
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0A0C10]">
        <AnimatedRoutes />
      </div>
    </BrowserRouter>
  );
}
