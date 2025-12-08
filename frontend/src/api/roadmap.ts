/**
 * ロードマップAPI クライアント
 * 学習ロードマップの CRUD 操作とCSVインポート機能を提供
 */

import axios, { AxiosResponse } from 'axios';

// API基本設定
const API_BASE_URL = 'http://localhost:8007';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエスト/レスポンスインターセプターの設定
apiClient.interceptors.request.use(
  (config) => {
    // 将来的にJWTトークンなどの認証情報を追加
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// 型定義
export interface RoadmapItem {
  title: string;
  estimated_hours: number;
  completed_hours: number;
  progress: number;
}

export interface Roadmap {
  roadmap_id: string;
  title: string;
  description: string;
  items: RoadmapItem[];
  total_hours: number;
  completed_hours: number;
  progress: number;
  status: 'active' | 'completed' | 'deleted';
  created_at: string;
  updated_at: string;
}

export interface RoadmapSummary {
  roadmap_id: string;
  title: string;
  description: string;
  total_hours: number;
  completed_hours: number;
  progress: number;
  items_count: number;
  status: 'active' | 'completed' | 'deleted';
  created_at: string;
  updated_at: string;
}

export interface CreateRoadmapRequest {
  title: string;
  description?: string;
  items: Omit<RoadmapItem, 'progress'>[];
}

export interface UpdateRoadmapRequest {
  title?: string;
  description?: string;
  items?: Omit<RoadmapItem, 'progress'>[];
}

export interface ImportCSVRequest {
  title: string;
  csv_content: string;
}

export interface RoadmapListResponse {
  roadmaps: RoadmapSummary[];
  total_count: number;
}

export interface RoadmapListParams {
  limit?: number;
  status?: 'active' | 'completed' | 'deleted' | 'all';
}

// API関数群
export class RoadmapAPI {
  /**
   * ロードマップ一覧を取得
   */
  static async getRoadmaps(params: RoadmapListParams = {}): Promise<RoadmapListResponse> {
    const response: AxiosResponse<RoadmapListResponse> = await apiClient.get('/roadmap', {
      params,
    });
    return response.data;
  }

  /**
   * ロードマップの詳細を取得
   */
  static async getRoadmap(roadmapId: string): Promise<Roadmap> {
    const response: AxiosResponse<Roadmap> = await apiClient.get(`/roadmap/${roadmapId}`);
    return response.data;
  }

  /**
   * 新しいロードマップを作成
   */
  static async createRoadmap(data: CreateRoadmapRequest): Promise<Roadmap> {
    const response: AxiosResponse<Roadmap> = await apiClient.post('/roadmap', data);
    return response.data;
  }

  /**
   * ロードマップを更新
   */
  static async updateRoadmap(roadmapId: string, data: UpdateRoadmapRequest): Promise<Roadmap> {
    const response: AxiosResponse<Roadmap> = await apiClient.put(`/roadmap/${roadmapId}`, data);
    return response.data;
  }

  /**
   * ロードマップを削除（論理削除）
   */
  static async deleteRoadmap(roadmapId: string): Promise<{ message: string }> {
    const response: AxiosResponse<{ message: string }> = await apiClient.delete(`/roadmap/${roadmapId}`);
    return response.data;
  }

  /**
   * CSVからロードマップをインポート
   */
  static async importFromCSV(data: ImportCSVRequest): Promise<Roadmap> {
    const response: AxiosResponse<Roadmap> = await apiClient.post('/roadmap/import', data);
    return response.data;
  }

  /**
   * CSVテンプレートをダウンロード
   */
  static async downloadCSVTemplate(): Promise<string> {
    const response: AxiosResponse<{ result: string }> = await apiClient.get('/roadmap/template');
    return response.data.result;
  }
}

export default RoadmapAPI;