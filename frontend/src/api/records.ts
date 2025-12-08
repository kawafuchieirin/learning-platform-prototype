/**
 * 学習記録API クライアント
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8009';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// レスポンスインターセプターでエラーハンドリング
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.code === 'ECONNREFUSED') {
      throw new Error('APIサーバーに接続できません。サーバーが起動していることを確認してください。');
    }
    throw error;
  }
);

// レスポンス共通型
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// 学習記録型定義
export interface StudyRecord {
  record_id: string;
  title: string;
  content: string;
  duration_minutes: number;
  study_date: string;
  tags: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  satisfaction: number; // 1-5
  notes?: string;
  roadmap_id?: string;
  roadmap_item_title?: string;
  status: 'active' | 'deleted';
  created_at: string;
  updated_at: string;
}

// 学習記録作成リクエスト
export interface CreateStudyRecordRequest {
  title: string;
  content: string;
  duration_minutes: number;
  study_date?: string;
  tags?: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
  satisfaction?: number;
  notes?: string;
  roadmap_id?: string;
  roadmap_item_title?: string;
}

// 学習記録更新リクエスト
export interface UpdateStudyRecordRequest {
  title?: string;
  content?: string;
  duration_minutes?: number;
  study_date?: string;
  tags?: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
  satisfaction?: number;
  notes?: string;
}

// 学習記録一覧リクエストパラメータ
export interface StudyRecordListParams {
  limit?: number;
  date_from?: string;
  date_to?: string;
  roadmap_id?: string;
  tags?: string;
}

// 学習記録一覧レスポンス
export interface StudyRecordListResponse {
  records: StudyRecord[];
  statistics: {
    total_duration_minutes: number;
    total_duration_hours: number;
    average_duration_minutes: number;
    total_records: number;
  };
  pagination: {
    limit: number;
    has_more: boolean;
  };
}

// テンプレート型定義
export interface RecordTemplate {
  template_type: 'reading' | 'coding' | 'video' | 'roadmap';
  title: string;
  description: string;
  default_difficulty: 'easy' | 'medium' | 'hard';
  default_tags: string[];
  sample_content: string;
  roadmap_items?: RoadmapItem[];
}

export interface RoadmapItem {
  roadmap_id: string;
  roadmap_title: string;
  item_title: string;
  estimated_hours: number;
  completed_hours: number;
  progress: number;
}

// テンプレート一覧レスポンス
export interface TemplateListResponse {
  templates: RecordTemplate[];
}

// テンプレートから記録作成リクエスト
export interface CreateFromTemplateRequest {
  template_type: 'reading' | 'coding' | 'video' | 'roadmap';
  title: string;
  duration_minutes: number;
  satisfaction?: number;
  notes?: string;
  roadmap_id?: string;
  roadmap_item_title?: string;
}

/**
 * 学習記録API クライアントクラス
 */
export class RecordsAPI {
  /**
   * 学習記録一覧を取得
   */
  static async getRecords(params: StudyRecordListParams = {}): Promise<StudyRecordListResponse> {
    const response = await api.get('/records', { params });
    return response.data;
  }

  /**
   * 学習記録詳細を取得
   */
  static async getRecord(recordId: string): Promise<StudyRecord> {
    const response = await api.get(`/records/${recordId}`);
    return response.data;
  }

  /**
   * 学習記録を作成
   */
  static async createRecord(data: CreateStudyRecordRequest): Promise<StudyRecord> {
    const response = await api.post('/records', data);
    return response.data;
  }

  /**
   * 学習記録を更新
   */
  static async updateRecord(recordId: string, data: UpdateStudyRecordRequest): Promise<StudyRecord> {
    const response = await api.put(`/records/${recordId}`, data);
    return response.data;
  }

  /**
   * 学習記録を削除
   */
  static async deleteRecord(recordId: string): Promise<{ message: string; record_id: string }> {
    const response = await api.delete(`/records/${recordId}`);
    return response.data;
  }

  /**
   * テンプレート一覧を取得
   */
  static async getTemplates(): Promise<TemplateListResponse> {
    const response = await api.get('/records/templates');
    return response.data;
  }

  /**
   * テンプレートから学習記録を作成
   */
  static async createFromTemplate(data: CreateFromTemplateRequest): Promise<StudyRecord> {
    const response = await api.post('/records/from-template', data);
    return response.data;
  }
}

// ヘルスチェック
export const checkHealth = async (): Promise<{ status: string; service: string; environment: string }> => {
  const response = await api.get('/health');
  return response.data;
};

export default RecordsAPI;