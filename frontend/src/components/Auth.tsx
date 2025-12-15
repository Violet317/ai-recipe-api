import React, { useState } from 'react';
import { recipeApi } from '../api';
import type { UserCreate, UserLogin } from '../api';

interface AuthProps {
  onAuthSuccess: (token: string) => void;
}

const Auth: React.FC<AuthProps> = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      if (isLogin) {
        // 登录
        const loginData: UserLogin = { username, password };
        const response = await recipeApi.login(loginData);
        onAuthSuccess(response.access_token);
        setSuccess('登录成功！');
      } else {
        // 注册
        const registerData: UserCreate = { username, email, password };
        await recipeApi.register(registerData);
        setSuccess('注册成功！请登录');
        setIsLogin(true);
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      setError(err.response?.data?.detail || '认证失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? '用户登录' : '用户注册'}</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">用户名</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        {!isLogin && (
          <div className="form-group">
            <label htmlFor="email">邮箱</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="password">密码</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? '处理中...' : (isLogin ? '登录' : '注册')}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="auth-toggle">
        <button
          type="button"
          onClick={() => setIsLogin(!isLogin)}
          className="toggle-btn"
        >
          {isLogin ? '没有账号？点击注册' : '已有账号？点击登录'}
        </button>
      </div>
    </div>
  );
};

export default Auth;