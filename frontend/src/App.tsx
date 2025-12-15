import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import RecipeRecommendation from './components/RecipeRecommendation';
import Auth from './components/Auth';
import './App.css';

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);

  // 检查localStorage中的token
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const handleAuthSuccess = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <div className="header-content">
            <h1>AI食谱推荐系统</h1>
            <nav className="nav-links">
              <Link to="/">首页</Link>
              {token ? (
                <button onClick={handleLogout} className="logout-btn">退出登录</button>
              ) : (
                <Link to="/auth">登录/注册</Link>
              )}
            </nav>
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<RecipeRecommendation />} />
            <Route 
              path="/auth" 
              element={token ? <Navigate to="/" /> : <Auth onAuthSuccess={handleAuthSuccess} />} 
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>&copy; 2025 AI食谱推荐系统 - 让烹饪更简单</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;