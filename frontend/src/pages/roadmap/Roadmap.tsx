/**
 * ロードマップページ
 * 学習ロードマップの一覧表示、作成、編集、CSVインポート機能を提供
 */

import React, { useState, useEffect } from 'react';
import { Plus, Upload, Download, Trash2, Edit, BarChart3 } from 'lucide-react';
import { RoadmapAPI, RoadmapSummary, CreateRoadmapRequest, ImportCSVRequest } from '../../api/roadmap';

const Roadmap: React.FC = () => {
  const [roadmaps, setRoadmaps] = useState<RoadmapSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);

  // ロードマップ一覧を読み込み
  const loadRoadmaps = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await RoadmapAPI.getRoadmaps({ status: 'all', limit: 50 });
      setRoadmaps(response.roadmaps);
    } catch (err) {
      setError('ロードマップの読み込みに失敗しました');
      console.error('Failed to load roadmaps:', err);
    } finally {
      setLoading(false);
    }
  };

  // コンポーネントマウント時にデータを読み込み
  useEffect(() => {
    loadRoadmaps();
  }, []);

  // CSVテンプレートのダウンロード
  const downloadTemplate = async () => {
    try {
      const template = await RoadmapAPI.downloadCSVTemplate();
      const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'roadmap_template.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError('CSVテンプレートのダウンロードに失敗しました');
    }
  };

  // ロードマップ削除
  const deleteRoadmap = async (roadmapId: string, title: string) => {
    if (!window.confirm(`「${title}」を削除してもよろしいですか？`)) {
      return;
    }

    try {
      await RoadmapAPI.deleteRoadmap(roadmapId);
      await loadRoadmaps(); // 一覧を再読み込み
    } catch (err) {
      setError('ロードマップの削除に失敗しました');
    }
  };

  // 進捗率バーの色を決定
  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-yellow-500';
    if (progress >= 20) return 'bg-blue-500';
    return 'bg-gray-300';
  };

  // ローディング表示
  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* ページヘッダー */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">学習ロードマップ</h1>
          <p className="text-gray-600 mt-2">学習計画を管理し、進捗を追跡しましょう</p>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={downloadTemplate}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="h-4 w-4 mr-2" />
            CSVテンプレート
          </button>
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Upload className="h-4 w-4 mr-2" />
            CSVインポート
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            新規作成
          </button>
        </div>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="mb-6 bg-red-50 border-gray-200 border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* ロードマップ一覧 */}
      {roadmaps.length === 0 ? (
        <div className="text-center py-16">
          <BarChart3 className="h-24 w-24 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            ロードマップがありません
          </h3>
          <p className="text-gray-600 mb-6">
            新しいロードマップを作成するか、CSVファイルからインポートしてください
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            最初のロードマップを作成
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roadmaps.map((roadmap) => (
            <div
              key={roadmap.roadmap_id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {roadmap.title}
                  </h3>
                  <p className="text-gray-600 text-sm line-clamp-2">
                    {roadmap.description || '説明がありません'}
                  </p>
                </div>
                <div className="flex space-x-1 ml-4">
                  <button 
                    className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                    title="編集"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button 
                    onClick={() => deleteRoadmap(roadmap.roadmap_id, roadmap.title)}
                    className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                    title="削除"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* 進捗情報 */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">進捗</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {Math.round(roadmap.progress)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(roadmap.progress)}`}
                    style={{ width: `${Math.min(roadmap.progress, 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{roadmap.completed_hours}h 完了</span>
                  <span>全{roadmap.total_hours}h</span>
                </div>
              </div>

              {/* 統計情報 */}
              <div className="flex justify-between items-center text-sm text-gray-600">
                <div>
                  <span className="font-medium">{roadmap.items_count}</span> アイテム
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  roadmap.status === 'active' 
                    ? 'bg-green-100 text-green-700'
                    : roadmap.status === 'completed'
                    ? 'bg-blue-100 text-blue-700' 
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {roadmap.status === 'active' ? 'アクティブ' :
                   roadmap.status === 'completed' ? '完了' : '無効'}
                </div>
              </div>

              <div className="text-xs text-gray-400 mt-3">
                作成: {new Date(roadmap.created_at).toLocaleDateString('ja-JP')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 新規作成モーダル */}
      {showCreateModal && (
        <CreateRoadmapModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            loadRoadmaps();
          }}
        />
      )}

      {/* CSVインポートモーダル */}
      {showImportModal && (
        <ImportCSVModal
          onClose={() => setShowImportModal(false)}
          onSuccess={() => {
            setShowImportModal(false);
            loadRoadmaps();
          }}
        />
      )}
    </div>
  );
};

// 新規作成モーダルコンポーネント
const CreateRoadmapModal: React.FC<{
  onClose: () => void;
  onSuccess: () => void;
}> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState<CreateRoadmapRequest>({
    title: '',
    description: '',
    items: [{ title: '', estimated_hours: 0, completed_hours: 0 }]
  });
  const [submitting, setSubmitting] = useState(false);

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { title: '', estimated_hours: 0, completed_hours: 0 }]
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index)
    });
  };

  const updateItem = (index: number, field: keyof typeof formData.items[0], value: string | number) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      alert('タイトルを入力してください');
      return;
    }

    if (formData.items.length === 0 || formData.items.every(item => !item.title.trim())) {
      alert('少なくとも1つのアイテムを追加してください');
      return;
    }

    try {
      setSubmitting(true);
      await RoadmapAPI.createRoadmap(formData);
      onSuccess();
    } catch (err) {
      alert('ロードマップの作成に失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">新しいロードマップを作成</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              タイトル *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="React学習ロードマップ"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              説明
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
              placeholder="このロードマップの概要を入力してください..."
            />
          </div>

          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-gray-700">
                学習項目
              </label>
              <button
                type="button"
                onClick={addItem}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                + 項目を追加
              </button>
            </div>

            {formData.items.map((item, index) => (
              <div key={index} className="flex gap-3 mb-3 items-end">
                <div className="flex-1">
                  <input
                    type="text"
                    value={item.title}
                    onChange={(e) => updateItem(index, 'title', e.target.value)}
                    className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="学習項目のタイトル"
                    required
                  />
                </div>
                <div className="w-32">
                  <input
                    type="number"
                    value={item.estimated_hours}
                    onChange={(e) => updateItem(index, 'estimated_hours', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="予定時間"
                    min="0"
                    step="0.5"
                    required
                  />
                </div>
                <div className="w-32">
                  <input
                    type="number"
                    value={item.completed_hours}
                    onChange={(e) => updateItem(index, 'completed_hours', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="完了時間"
                    min="0"
                    step="0.5"
                  />
                </div>
                {formData.items.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeItem(index)}
                    className="p-2 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border-gray-200 border-gray-300 rounded-lg hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {submitting ? '作成中...' : '作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// CSVインポートモーダルコンポーネント
const ImportCSVModal: React.FC<{
  onClose: () => void;
  onSuccess: () => void;
}> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState<ImportCSVRequest>({
    title: '',
    csv_content: ''
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      alert('タイトルを入力してください');
      return;
    }

    if (!formData.csv_content.trim()) {
      alert('CSVデータを入力してください');
      return;
    }

    try {
      setSubmitting(true);
      await RoadmapAPI.importFromCSV(formData);
      onSuccess();
    } catch (err) {
      alert('CSVインポートに失敗しました');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">CSVからインポート</h2>
        
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>CSVフォーマット:</strong> タイトル,予定時間,完了時間<br />
            例: React基礎,20,5
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ロードマップタイトル *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="インポートするロードマップのタイトル"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CSVデータ *
            </label>
            <textarea
              value={formData.csv_content}
              onChange={(e) => setFormData({ ...formData, csv_content: e.target.value })}
              className="w-full px-3 py-2 border-gray-200 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={8}
              placeholder="React基礎,20,5&#10;Hooks学習,15,0&#10;状態管理,10,0"
              required
            />
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border-gray-200 border-gray-300 rounded-lg hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'インポート中...' : 'インポート'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Roadmap;