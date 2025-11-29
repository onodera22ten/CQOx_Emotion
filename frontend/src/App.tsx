import React from "react";
import { BrowserRouter, Routes, Route, NavLink, Navigate } from "react-router-dom";
import { EmotionEpisodeCreatePage } from "@/pages/emotion/EmotionEpisodeCreatePage";
import { EmotionOutcomeLogPage } from "@/pages/emotion/EmotionOutcomeLogPage";
import { EmotionDashboardPage } from "@/pages/emotion/EmotionDashboardPage";

const navItems = [
  { to: "/emotion/create", label: "Episode Draft" },
  { to: "/emotion/outcome", label: "Outcome Log" },
  { to: "/emotion/dashboard", label: "Dashboard" },
];

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-green-50">
        <header className="bg-white border-b">
          <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Emotion CQOx</h1>
              <p className="text-sm text-gray-500">
                感情の波を「データと因果」で理解する Episode ログ
              </p>
            </div>
            <nav className="flex gap-3">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `px-4 py-2 rounded-lg text-sm font-semibold ${
                      isActive ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/emotion/create" replace />} />
            <Route path="/emotion/create" element={<EmotionEpisodeCreatePage />} />
            <Route path="/emotion/outcome" element={<EmotionOutcomeLogPage />} />
            <Route path="/emotion/dashboard" element={<EmotionDashboardPage />} />
          </Routes>
        </main>
        <footer className="bg-white border-t text-center py-6 text-sm text-gray-500">
          Emotional Episode Optimizer © {new Date().getFullYear()}
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
