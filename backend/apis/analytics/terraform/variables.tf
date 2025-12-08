variable "service_name" {
  description = "サービス名"
  type        = string
  default     = "learning-platform"
}

variable "environment" {
  description = "環境名"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

# DynamoDB テーブル関連
variable "users_table_name" {
  description = "ユーザーテーブル名"
  type        = string
  default     = "Users"
}

variable "users_table_arn" {
  description = "ユーザーテーブルARN"
  type        = string
}

variable "timer_table_name" {
  description = "タイマーテーブル名"
  type        = string
  default     = "Timer"
}

variable "timer_table_arn" {
  description = "タイマーテーブルARN"
  type        = string
}

variable "records_table_name" {
  description = "学習記録テーブル名"
  type        = string
  default     = "Records"
}

variable "records_table_arn" {
  description = "学習記録テーブルARN"
  type        = string
}

variable "roadmap_table_name" {
  description = "ロードマップテーブル名"
  type        = string
  default     = "Roadmap"
}

variable "roadmap_table_arn" {
  description = "ロードマップテーブルARN"
  type        = string
}

# Lambda設定
variable "lambda_timeout" {
  description = "Lambda タイムアウト（秒）"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda メモリサイズ（MB）"
  type        = number
  default     = 256
}

variable "lambda_runtime" {
  description = "Lambda ランタイム"
  type        = string
  default     = "python3.11"
}

# キャッシュ設定
variable "enable_cache" {
  description = "キャッシュ有効化フラグ"
  type        = bool
  default     = false
}

variable "cache_ttl_seconds" {
  description = "キャッシュTTL（秒）"
  type        = number
  default     = 300
}

# 分析設定
variable "max_analysis_period_days" {
  description = "最大分析期間（日数）"
  type        = number
  default     = 365
}

# API Gateway設定
variable "create_api_gateway" {
  description = "API Gateway作成フラグ"
  type        = bool
  default     = true
}

variable "api_gateway_execution_arn" {
  description = "API Gateway実行ARN"
  type        = string
  default     = ""
}

# ログ設定
variable "log_level" {
  description = "ログレベル"
  type        = string
  default     = "INFO"
  
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "ログレベルは DEBUG, INFO, WARNING, ERROR, CRITICAL のいずれかである必要があります。"
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs保持期間（日数）"
  type        = number
  default     = 14
}

# セキュリティ設定
variable "jwt_secret_key" {
  description = "JWT署名用秘密鍵"
  type        = string
  sensitive   = true
}

# モニタリング設定
variable "alarm_topic_arn" {
  description = "CloudWatch Alarm通知用SNSトピックARN"
  type        = string
  default     = ""
}

variable "enable_enhanced_monitoring" {
  description = "拡張モニタリング有効化"
  type        = bool
  default     = false
}

# タグ設定
variable "common_tags" {
  description = "共通タグ"
  type        = map(string)
  default = {
    Project   = "learning-platform"
    Service   = "analytics"
    ManagedBy = "terraform"
  }
}