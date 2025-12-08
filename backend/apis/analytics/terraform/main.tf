terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# データソース
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Lambda実行ロール
resource "aws_iam_role" "analytics_lambda_role" {
  name = "${var.service_name}-analytics-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Lambda基本実行ポリシーをアタッチ
resource "aws_iam_role_policy_attachment" "analytics_lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.analytics_lambda_role.name
}

# DynamoDB アクセスポリシー
resource "aws_iam_role_policy" "analytics_dynamodb_policy" {
  name = "${var.service_name}-analytics-dynamodb-policy"
  role = aws_iam_role.analytics_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:GetItem",
          "dynamodb:BatchGetItem",
          "dynamodb:Scan"
        ]
        Resource = [
          var.users_table_arn,
          var.timer_table_arn,
          var.records_table_arn,
          var.roadmap_table_arn,
          "${var.users_table_arn}/index/*",
          "${var.timer_table_arn}/index/*",
          "${var.records_table_arn}/index/*",
          "${var.roadmap_table_arn}/index/*"
        ]
      }
    ]
  })
}

# Lambda関数用のZIPファイル作成
data "archive_file" "analytics_lambda_zip" {
  type        = "zip"
  source_dir  = "../lambda"
  output_path = "analytics_lambda.zip"
  
  excludes = [
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "tests",
    ".git",
    ".gitignore",
    "README.md"
  ]
}

# Analytics Lambda関数
resource "aws_lambda_function" "analytics_lambda" {
  function_name = "${var.service_name}-analytics"
  role         = aws_iam_role.analytics_lambda_role.arn
  handler      = "src.main.handler"
  runtime      = "python3.11"
  timeout      = 30
  memory_size  = 256

  filename         = data.archive_file.analytics_lambda_zip.output_path
  source_code_hash = data.archive_file.analytics_lambda_zip.output_base64sha256

  environment {
    variables = {
      ENV                      = var.environment
      AWS_REGION              = var.aws_region
      USERS_TABLE             = var.users_table_name
      TIMER_TABLE             = var.timer_table_name
      RECORDS_TABLE           = var.records_table_name
      ROADMAP_TABLE           = var.roadmap_table_name
      ENABLE_CACHE            = var.enable_cache
      CACHE_TTL_SECONDS       = var.cache_ttl_seconds
      LOG_LEVEL               = var.log_level
      JWT_SECRET_KEY          = var.jwt_secret_key
      MAX_ANALYSIS_PERIOD_DAYS = var.max_analysis_period_days
    }
  }

  tags = {
    Name        = "${var.service_name}-analytics"
    Environment = var.environment
    Service     = "analytics"
  }
}

# CloudWatch Logs グループ
resource "aws_cloudwatch_log_group" "analytics_lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.analytics_lambda.function_name}"
  retention_in_days = var.log_retention_days
}

# API Gateway 統合用のリソース作成
resource "aws_lambda_permission" "analytics_api_gateway" {
  count = var.create_api_gateway ? 1 : 0
  
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${var.api_gateway_execution_arn}/*/*"
}

# Lambda 関数 URL （開発環境用）
resource "aws_lambda_function_url" "analytics_lambda_url" {
  count = var.environment == "dev" ? 1 : 0
  
  function_name      = aws_lambda_function.analytics_lambda.function_name
  authorization_type = "NONE"
  
  cors {
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers     = ["Content-Type", "Authorization"]
    expose_headers    = ["X-Request-ID"]
    max_age          = 300
  }
}

# Analytics Lambda のモニタリング
resource "aws_cloudwatch_metric_alarm" "analytics_error_rate" {
  alarm_name          = "${var.service_name}-analytics-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors analytics lambda error rate"
  alarm_actions       = var.alarm_topic_arn != "" ? [var.alarm_topic_arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.analytics_lambda.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "analytics_duration" {
  alarm_name          = "${var.service_name}-analytics-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = "25000"  # 25秒
  alarm_description   = "This metric monitors analytics lambda duration"
  alarm_actions       = var.alarm_topic_arn != "" ? [var.alarm_topic_arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.analytics_lambda.function_name
  }
}