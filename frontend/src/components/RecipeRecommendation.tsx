import React, { useState } from 'react';
import { recipeApi } from '../api';
import type { RecommendRequest, Recipe } from '../api';

const RecipeRecommendation: React.FC = () => {
  const [ingredientsInput, setIngredientsInput] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [recommendations, setRecommendations] = useState<Recipe[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const split = (v: string) =>
        v
          .split(/[,\uFF0C\u3001;\s]+/)
          .map(x => x.trim())
          .filter(Boolean);

      const ingredients = split(ingredientsInput);
      const tags = split(tagsInput);

      if (ingredients.length === 0) {
        setError('请至少输入一种食材');
        setIsLoading(false);
        return;
      }

      const requestData: RecommendRequest = {
        ingredients,
        tags: tags.length > 0 ? tags : undefined,
      };

      const response = await recipeApi.recommend(requestData);
      setRecommendations(response.recommendations);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('获取食谱推荐失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="recipe-recommendation">
      <h1>AI食谱推荐</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="ingredients">食材（用逗号分隔）</label>
          <input
            type="text"
            id="ingredients"
            value={ingredientsInput}
            onChange={(e) => setIngredientsInput(e.target.value)}
            placeholder="例如：番茄, 鸡蛋, 挂面"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="tags">标签（可选，用逗号分隔）</label>
          <input
            type="text"
            id="tags"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="例如：低脂, 快手"
          />
        </div>

        <button type="submit" disabled={isLoading}>
          {isLoading ? '正在推荐...' : '获取推荐'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {recommendations.length > 0 && (
        <div className="results">
          <h2>推荐结果 ({recommendations.length}个)</h2>
          <div className="recipe-list">
            {recommendations.map((recipe) => (
              <div key={recipe.id} className="recipe-card">
                <h3>{recipe.name}</h3>
                <div className="recipe-info">
                  <div className="match-rate">
                    匹配度: {Math.round(recipe.match_rate * 100)}%
                  </div>
                  <div className="time">
                    烹饪时间: {recipe.time}分钟
                  </div>
                </div>
                <div className="tags">
                  {recipe.tags.map((tag: string, index: number) => (
                    <span key={index} className="tag">{tag}</span>
                  ))}
                </div>
                <div className="missing-ingredients">
                  <h4>缺少的食材:</h4>
                  <ul>
                    {recipe.missing_ingredients.map((ing: string, index: number) => (
                      <li key={index}>{ing}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {!isLoading && !error && recommendations.length === 0 && (
        <div className="no-results">没有找到推荐，请输入能匹配的食材（至少两种），或去掉过多标签筛选。</div>
      )}
    </div>
  );
};

export default RecipeRecommendation;
