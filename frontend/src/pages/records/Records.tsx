/**
 * 学習記録ページ
 */

import React, { useState, useEffect } from 'react';
import {
  RecordsAPI,
  StudyRecord,
  StudyRecordListParams,
  StudyRecordListResponse,
  CreateStudyRecordRequest,
  UpdateStudyRecordRequest,
  RecordTemplate,
  CreateFromTemplateRequest
} from '../../api/records';

const Records: React.FC = () => {
  // State管理
  const [records, setRecords] = useState<StudyRecord[]>([]);
  const [statistics, setStatistics] = useState<StudyRecordListResponse['statistics'] | null>(null);
  const [templates, setTemplates] = useState<RecordTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // フィルター・検索関連
  const [filters, setFilters] = useState<StudyRecordListParams>({});
  const [searchTerm, setSearchTerm] = useState('');

  // モーダル・フォーム関連
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingRecord, setEditingRecord] = useState<StudyRecord | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<StudyRecord | null>(null);

  // フォームデータ
  const [formData, setFormData] = useState<CreateStudyRecordRequest>({
    title: '',
    content: '',
    duration_minutes: 0,
    study_date: new Date().toISOString().split('T')[0],
    tags: [],
    difficulty: 'medium',
    satisfaction: 3,
    notes: ''
  });

  const [templateFormData, setTemplateFormData] = useState<CreateFromTemplateRequest>({
    template_type: 'reading',
    title: '',
    duration_minutes: 0,
    satisfaction: 3,
    notes: ''
  });

  // データ取得
  const fetchRecords = async () => {
    try {
      setLoading(true);
      const response = await RecordsAPI.getRecords(filters);
      setRecords(response.records);
      setStatistics(response.statistics);
      setError(null);
    } catch (err) {
      setError('学習記録の取得に失敗しました');
      console.error('Error fetching records:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await RecordsAPI.getTemplates();
      setTemplates(response.templates);
    } catch (err) {
      console.error('Error fetching templates:', err);
    }
  };

  // 初期データ取得
  useEffect(() => {
    fetchRecords();
    fetchTemplates();
  }, []);

  // フィルター変更時の再取得
  useEffect(() => {
    fetchRecords();
  }, [filters]);

  // フィルターされた記録
  const filteredRecords = records.filter(record =>
    record.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    record.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // 学習記録作成
  const handleCreateRecord = async () => {
    try {
      await RecordsAPI.createRecord(formData);
      setShowCreateModal(false);
      setFormData({
        title: '',
        content: '',
        duration_minutes: 0,
        study_date: new Date().toISOString().split('T')[0],
        tags: [],
        difficulty: 'medium',
        satisfaction: 3,
        notes: ''
      });
      fetchRecords();
    } catch (err) {
      setError('学習記録の作成に失敗しました');
      console.error('Error creating record:', err);
    }
  };

  // テンプレートから学習記録作成
  const handleCreateFromTemplate = async () => {
    try {
      await RecordsAPI.createFromTemplate(templateFormData);
      setShowTemplateModal(false);
      setTemplateFormData({
        template_type: 'reading',
        title: '',
        duration_minutes: 0,
        satisfaction: 3,
        notes: ''
      });
      fetchRecords();
    } catch (err) {
      setError('テンプレートからの作成に失敗しました');
      console.error('Error creating from template:', err);
    }
  };

  // 学習記録更新
  const handleUpdateRecord = async () => {
    if (!editingRecord) return;

    try {
      const updateData: UpdateStudyRecordRequest = {
        title: formData.title,
        content: formData.content,
        duration_minutes: formData.duration_minutes,
        tags: formData.tags,
        difficulty: formData.difficulty,
        satisfaction: formData.satisfaction,
        notes: formData.notes
      };

      await RecordsAPI.updateRecord(editingRecord.record_id, updateData);
      setEditingRecord(null);
      setShowCreateModal(false);
      fetchRecords();
    } catch (err) {
      setError('学習記録の更新に失敗しました');
      console.error('Error updating record:', err);
    }
  };

  // 学習記録削除
  const handleDeleteRecord = async (recordId: string) => {
    if (!confirm('この学習記録を削除しますか？')) return;

    try {
      await RecordsAPI.deleteRecord(recordId);
      fetchRecords();
    } catch (err) {
      setError('学習記録の削除に失敗しました');
      console.error('Error deleting record:', err);
    }
  };

  // 編集開始
  const startEdit = (record: StudyRecord) => {
    setEditingRecord(record);
    setFormData({
      title: record.title,
      content: record.content,
      duration_minutes: record.duration_minutes,
      study_date: record.study_date,
      tags: record.tags,
      difficulty: record.difficulty,
      satisfaction: record.satisfaction,
      notes: record.notes || ''
    });
    setShowCreateModal(true);
  };

  // 詳細表示
  const showDetail = async (record: StudyRecord) => {
    try {
      const detailRecord = await RecordsAPI.getRecord(record.record_id);
      setSelectedRecord(detailRecord);
      setShowDetailModal(true);
    } catch (err) {
      setError('記録詳細の取得に失敗しました');
      console.error('Error fetching record detail:', err);
    }
  };

  // タグの表示色
  const getTagColor = (tag: string) => {
    const colors = [
      'bg-blue-100 text-blue-800',
      'bg-green-100 text-green-800',
      'bg-yellow-100 text-yellow-800',
      'bg-red-100 text-red-800',
      'bg-purple-100 text-purple-800',
      'bg-indigo-100 text-indigo-800'
    ];
    return colors[tag.length % colors.length];
  };

  // 難易度の表示
  const getDifficultyBadge = (difficulty: string) => {
    const badges = {
      easy: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      hard: 'bg-red-100 text-red-800'
    };
    return badges[difficulty as keyof typeof badges] || badges.medium;
  };

  // 満足度の星表示
  const renderStars = (satisfaction: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={i < satisfaction ? 'text-yellow-400' : 'text-gray-300'}>
        ★
      </span>
    ));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">読み込み中...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">学習記録</h1>
        <p className="text-gray-600">あなたの学習活動を記録・管理します</p>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* 統計表示 */}
      {statistics && (
        <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow border-gray-200 border">
            <div className="text-sm font-medium text-gray-500">総学習時間</div>
            <div className="text-2xl font-bold text-blue-600">{statistics.total_duration_hours.toFixed(1)}時間</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-gray-200 border">
            <div className="text-sm font-medium text-gray-500">記録数</div>
            <div className="text-2xl font-bold text-green-600">{statistics.total_records}件</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-gray-200 border">
            <div className="text-sm font-medium text-gray-500">平均学習時間</div>
            <div className="text-2xl font-bold text-yellow-600">{Math.round(statistics.average_duration_minutes)}分</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow border-gray-200 border">
            <div className="text-sm font-medium text-gray-500">今月の総時間</div>
            <div className="text-2xl font-bold text-purple-600">{statistics.total_duration_minutes}分</div>
          </div>
        </div>
      )}

      {/* 操作ボタン */}
      <div className="mb-6 flex flex-wrap gap-4">
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium"
        >
          新規作成
        </button>
        <button
          onClick={() => setShowTemplateModal(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium"
        >
          テンプレートから作成
        </button>
      </div>

      {/* 検索・フィルター */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow border-gray-200 border">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              検索
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="タイトル、内容、タグで検索"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              開始日
            </label>
            <input
              type="date"
              value={filters.date_from || ''}
              onChange={(e) => setFilters(prev => ({ ...prev, date_from: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              終了日
            </label>
            <input
              type="date"
              value={filters.date_to || ''}
              onChange={(e) => setFilters(prev => ({ ...prev, date_to: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => setFilters({})}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md"
            >
              クリア
            </button>
          </div>
        </div>
      </div>

      {/* 学習記録一覧 */}
      <div className="space-y-4">
        {filteredRecords.map((record) => (
          <div key={record.record_id} className="bg-white p-6 rounded-lg shadow border-gray-200 border hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{record.title}</h3>
                <p className="text-gray-600 text-sm mb-2">{record.content}</p>
                
                {/* タグ・難易度・満足度 */}
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  {record.tags.map((tag, index) => (
                    <span
                      key={index}
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTagColor(tag)}`}
                    >
                      {tag}
                    </span>
                  ))}
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyBadge(record.difficulty)}`}>
                    {record.difficulty}
                  </span>
                  <div className="flex items-center">
                    {renderStars(record.satisfaction)}
                  </div>
                </div>
                
                {/* メタデータ */}
                <div className="text-sm text-gray-500">
                  学習時間: {record.duration_minutes}分 | 
                  学習日: {record.study_date} | 
                  作成: {new Date(record.created_at).toLocaleDateString()}
                  {record.roadmap_item_title && (
                    <span> | ロードマップ: {record.roadmap_item_title}</span>
                  )}
                </div>
              </div>
              
              {/* 操作ボタン */}
              <div className="flex gap-2 ml-4">
                <button
                  onClick={() => showDetail(record)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  詳細
                </button>
                <button
                  onClick={() => startEdit(record)}
                  className="text-green-600 hover:text-green-800 text-sm"
                >
                  編集
                </button>
                <button
                  onClick={() => handleDeleteRecord(record.record_id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  削除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 記録が空の場合 */}
      {filteredRecords.length === 0 && !loading && (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">学習記録がありません</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium"
          >
            最初の学習記録を作成
          </button>
        </div>
      )}

      {/* 新規作成・編集モーダル */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                {editingRecord ? '学習記録を編集' : '新しい学習記録を作成'}
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    タイトル*
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="学習内容のタイトル"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    学習内容*
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="学習した内容を詳しく記録してください"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      学習時間（分）*
                    </label>
                    <input
                      type="number"
                      value={formData.duration_minutes}
                      onChange={(e) => setFormData(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      min="1"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      学習日
                    </label>
                    <input
                      type="date"
                      value={formData.study_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, study_date: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      難易度
                    </label>
                    <select
                      value={formData.difficulty}
                      onChange={(e) => setFormData(prev => ({ ...prev, difficulty: e.target.value as 'easy' | 'medium' | 'hard' }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="easy">易しい</option>
                      <option value="medium">普通</option>
                      <option value="hard">難しい</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      満足度 (1-5)
                    </label>
                    <select
                      value={formData.satisfaction}
                      onChange={(e) => setFormData(prev => ({ ...prev, satisfaction: parseInt(e.target.value) }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value={1}>1 - 不満</option>
                      <option value={2}>2 - やや不満</option>
                      <option value={3}>3 - 普通</option>
                      <option value={4}>4 - 満足</option>
                      <option value={5}>5 - とても満足</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    タグ（カンマ区切り）
                  </label>
                  <input
                    type="text"
                    value={formData.tags?.join(', ') || ''}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag) 
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="javascript, react, frontend"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    メモ
                  </label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="追加のメモがあれば記録してください"
                  />
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingRecord(null);
                  }}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={editingRecord ? handleUpdateRecord : handleCreateRecord}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingRecord ? '更新' : '作成'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* テンプレート作成モーダル */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">テンプレートから作成</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    テンプレート種類
                  </label>
                  <select
                    value={templateFormData.template_type}
                    onChange={(e) => setTemplateFormData(prev => ({ 
                      ...prev, 
                      template_type: e.target.value as 'reading' | 'coding' | 'video' | 'roadmap'
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="reading">読書</option>
                    <option value="coding">コーディング</option>
                    <option value="video">動画学習</option>
                    <option value="roadmap">ロードマップ</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    タイトル*
                  </label>
                  <input
                    type="text"
                    value={templateFormData.title}
                    onChange={(e) => setTemplateFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="学習内容のタイトル"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      学習時間（分）*
                    </label>
                    <input
                      type="number"
                      value={templateFormData.duration_minutes}
                      onChange={(e) => setTemplateFormData(prev => ({ 
                        ...prev, 
                        duration_minutes: parseInt(e.target.value) || 0 
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      min="1"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      満足度 (1-5)
                    </label>
                    <select
                      value={templateFormData.satisfaction}
                      onChange={(e) => setTemplateFormData(prev => ({ 
                        ...prev, 
                        satisfaction: parseInt(e.target.value) 
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value={1}>1 - 不満</option>
                      <option value={2}>2 - やや不満</option>
                      <option value={3}>3 - 普通</option>
                      <option value={4}>4 - 満足</option>
                      <option value={5}>5 - とても満足</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    メモ
                  </label>
                  <textarea
                    value={templateFormData.notes}
                    onChange={(e) => setTemplateFormData(prev => ({ ...prev, notes: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="追加のメモがあれば記録してください"
                  />
                </div>

                {/* テンプレートプレビュー */}
                {templates.find(t => t.template_type === templateFormData.template_type) && (
                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-medium mb-2">テンプレートプレビュー</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {templates.find(t => t.template_type === templateFormData.template_type)?.description}
                    </p>
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                      {templates.find(t => t.template_type === templateFormData.template_type)?.sample_content}
                    </pre>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowTemplateModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  キャンセル
                </button>
                <button
                  onClick={handleCreateFromTemplate}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  作成
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 詳細表示モーダル */}
      {showDetailModal && selectedRecord && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">学習記録詳細</h2>
              
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg">{selectedRecord.title}</h3>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    学習内容
                  </label>
                  <div className="bg-gray-50 p-3 rounded-md text-sm whitespace-pre-wrap">
                    {selectedRecord.content}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">学習時間:</span> {selectedRecord.duration_minutes}分
                  </div>
                  <div>
                    <span className="font-medium">学習日:</span> {selectedRecord.study_date}
                  </div>
                  <div>
                    <span className="font-medium">難易度:</span> 
                    <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyBadge(selectedRecord.difficulty)}`}>
                      {selectedRecord.difficulty}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className="font-medium mr-2">満足度:</span>
                    {renderStars(selectedRecord.satisfaction)}
                  </div>
                </div>
                
                {selectedRecord.tags.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      タグ
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {selectedRecord.tags.map((tag, index) => (
                        <span
                          key={index}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTagColor(tag)}`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedRecord.notes && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      メモ
                    </label>
                    <div className="bg-gray-50 p-3 rounded-md text-sm whitespace-pre-wrap">
                      {selectedRecord.notes}
                    </div>
                  </div>
                )}
                
                {selectedRecord.roadmap_item_title && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      ロードマップ
                    </label>
                    <div className="bg-blue-50 p-3 rounded-md text-sm">
                      {selectedRecord.roadmap_item_title}
                    </div>
                  </div>
                )}
                
                <div className="text-xs text-gray-500 pt-4 border-t">
                  作成: {new Date(selectedRecord.created_at).toLocaleString()} | 
                  更新: {new Date(selectedRecord.updated_at).toLocaleString()}
                </div>
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  閉じる
                </button>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    startEdit(selectedRecord);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  編集
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Records;