import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import RecipeRecommendation from './components/RecipeRecommendation';
import Auth from './components/Auth';
import ConfigStatus from './components/ConfigStatus';

import './App.css';

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [configReady, setConfigReady] = useState<boolean>(true);
  const [showConfigDetails, setShowConfigDetails] = useState<boolean>(false);

  // 检查localStorage中的token
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
    }

    // 在开发环境或调试模式中默认显示配置详情
    if (import.meta.env.DEV || import.meta.env.VITE_DEBUG === 'true') {
      setShowConfigDetails(true);
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
          {/* 配置状态显示 */}
          {(showConfigDetails || !configReady) && (
            <ConfigStatus 
              showDetails={showConfigDetails}
              onConfigReady={setConfigReady}
            />
          )}

          {/* 配置状态切换按钮（开发环境或调试模式） */}
          {(import.meta.env.DEV || import.meta.env.VITE_DEBUG === 'true') && (
            <div style={{ textAlign: 'center', marginBottom: '16px' }}>
              <button 
                onClick={() => setShowConfigDetails(!showConfigDetails)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {showConfigDetails ? '隐藏配置状态' : '显示配置状态'}
              </button>
            </div>
          )}

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