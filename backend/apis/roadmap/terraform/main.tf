# ロードマップAPI Lambda関数とAPI Gateway設定

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# データソース
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Lambda実行ロール
resource "aws_iam_role" "roadmap_lambda_role" {
  name = "roadmap-lambda-role"

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

  tags = var.tags
}

# Lambda基本実行権限
resource "aws_iam_role_policy_attachment" "roadmap_lambda_basic" {
  role       = aws_iam_role.roadmap_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB アクセス権限
resource "aws_iam_role_policy" "roadmap_lambda_dynamodb" {
  name = "roadmap-lambda-dynamodb-policy"
  role = aws_iam_role.roadmap_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan"
        ]
        Resource = [
          var.dynamodb_table_arn,
          "${var.dynamodb_table_arn}/index/*"
        ]
      }
    ]
  })
}

# Lambda関数用のZIPファイル作成
data "archive_file" "roadmap_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda"
  output_path = "${path.module}/roadmap_lambda.zip"
  excludes    = ["__pycache__", "*.pyc", ".pytest_cache", "tests"]
}

# Lambda関数
resource "aws_lambda_function" "roadmap_api" {
  filename         = data.archive_file.roadmap_lambda_zip.output_path
  function_name    = "roadmap-api"
  role            = aws_iam_role.roadmap_lambda_role.arn
  handler         = "main.lambda_handler"
  runtime         = "python3.13"
  timeout         = 30
  memory_size     = 256

  source_code_hash = data.archive_file.roadmap_lambda_zip.output_base64sha256

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = var.dynamodb_table_name
      LOG_LEVEL          = "INFO"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.roadmap_lambda_basic,
    aws_cloudwatch_log_group.roadmap_lambda_logs
  ]

  tags = var.tags
}

# CloudWatch Logs
resource "aws_cloudwatch_log_group" "roadmap_lambda_logs" {
  name              = "/aws/lambda/roadmap-api"
  retention_in_days = 14

  tags = var.tags
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "roadmap_api" {
  name = "roadmap-api"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = var.tags
}

# API Gateway リソース - /roadmap
resource "aws_api_gateway_resource" "roadmap" {
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id
  parent_id   = aws_api_gateway_rest_api.roadmap_api.root_resource_id
  path_part   = "roadmap"
}

# API Gateway リソース - /roadmap/{roadmapId}
resource "aws_api_gateway_resource" "roadmap_id" {
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id
  parent_id   = aws_api_gateway_resource.roadmap.id
  path_part   = "{roadmapId}"
}

# API Gateway リソース - /roadmap/import
resource "aws_api_gateway_resource" "roadmap_import" {
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id
  parent_id   = aws_api_gateway_resource.roadmap.id
  path_part   = "import"
}

# API Gateway リソース - /roadmap/template
resource "aws_api_gateway_resource" "roadmap_template" {
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id
  parent_id   = aws_api_gateway_resource.roadmap.id
  path_part   = "template"
}

# API Gateway メソッド - GET /roadmap
resource "aws_api_gateway_method" "roadmap_get" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id

  request_parameters = {
    "method.request.querystring.limit"  = false
    "method.request.querystring.status" = false
  }
}

# API Gateway メソッド - POST /roadmap
resource "aws_api_gateway_method" "roadmap_post" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id
}

# API Gateway メソッド - GET /roadmap/{roadmapId}
resource "aws_api_gateway_method" "roadmap_id_get" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap_id.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id

  request_parameters = {
    "method.request.path.roadmapId" = true
  }
}

# API Gateway メソッド - PUT /roadmap/{roadmapId}
resource "aws_api_gateway_method" "roadmap_id_put" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap_id.id
  http_method   = "PUT"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id

  request_parameters = {
    "method.request.path.roadmapId" = true
  }
}

# API Gateway メソッド - DELETE /roadmap/{roadmapId}
resource "aws_api_gateway_method" "roadmap_id_delete" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap_id.id
  http_method   = "DELETE"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id

  request_parameters = {
    "method.request.path.roadmapId" = true
  }
}

# API Gateway メソッド - POST /roadmap/import
resource "aws_api_gateway_method" "roadmap_import_post" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap_import.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = var.cognito_authorizer_id
}

# API Gateway メソッド - GET /roadmap/template
resource "aws_api_gateway_method" "roadmap_template_get" {
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  resource_id   = aws_api_gateway_resource.roadmap_template.id
  http_method   = "GET"
  authorization = "NONE"
}

# Lambda統合設定（全メソッド共通）
locals {
  integration_methods = [
    {
      method_id = aws_api_gateway_method.roadmap_get.id
      http_method = "GET"
      resource_id = aws_api_gateway_resource.roadmap.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_post.id
      http_method = "POST"
      resource_id = aws_api_gateway_resource.roadmap.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_id_get.id
      http_method = "GET"
      resource_id = aws_api_gateway_resource.roadmap_id.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_id_put.id
      http_method = "PUT"
      resource_id = aws_api_gateway_resource.roadmap_id.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_id_delete.id
      http_method = "DELETE"
      resource_id = aws_api_gateway_resource.roadmap_id.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_import_post.id
      http_method = "POST"
      resource_id = aws_api_gateway_resource.roadmap_import.id
    },
    {
      method_id = aws_api_gateway_method.roadmap_template_get.id
      http_method = "GET"
      resource_id = aws_api_gateway_resource.roadmap_template.id
    }
  ]
}

# API Gateway 統合
resource "aws_api_gateway_integration" "roadmap_lambda_integration" {
  count = length(local.integration_methods)
  
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id
  resource_id = local.integration_methods[count.index].resource_id
  http_method = local.integration_methods[count.index].http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.roadmap_api.invoke_arn
}

# Lambda実行権限
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.roadmap_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.roadmap_api.execution_arn}/*/*"
}

# CORS設定
module "cors" {
  source = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.roadmap_api.id
  api_resource_id = aws_api_gateway_resource.roadmap.id
}

module "cors_id" {
  source = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.roadmap_api.id
  api_resource_id = aws_api_gateway_resource.roadmap_id.id
}

module "cors_import" {
  source = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.roadmap_api.id
  api_resource_id = aws_api_gateway_resource.roadmap_import.id
}

module "cors_template" {
  source = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.roadmap_api.id
  api_resource_id = aws_api_gateway_resource.roadmap_template.id
}

# API Gateway デプロイメント
resource "aws_api_gateway_deployment" "roadmap_api" {
  rest_api_id = aws_api_gateway_rest_api.roadmap_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.roadmap.id,
      aws_api_gateway_resource.roadmap_id.id,
      aws_api_gateway_resource.roadmap_import.id,
      aws_api_gateway_resource.roadmap_template.id,
      aws_api_gateway_method.roadmap_get.id,
      aws_api_gateway_method.roadmap_post.id,
      aws_api_gateway_method.roadmap_id_get.id,
      aws_api_gateway_method.roadmap_id_put.id,
      aws_api_gateway_method.roadmap_id_delete.id,
      aws_api_gateway_method.roadmap_import_post.id,
      aws_api_gateway_method.roadmap_template_get.id,
      aws_api_gateway_integration.roadmap_lambda_integration
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_integration.roadmap_lambda_integration,
    module.cors,
    module.cors_id,
    module.cors_import,
    module.cors_template
  ]
}

# API Gateway ステージ
resource "aws_api_gateway_stage" "roadmap_api" {
  deployment_id = aws_api_gateway_deployment.roadmap_api.id
  rest_api_id   = aws_api_gateway_rest_api.roadmap_api.id
  stage_name    = var.api_stage_name

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.roadmap_api_logs.arn
    format = jsonencode({
      requestId      = "$requestId"
      ip            = "$requestId"
      caller        = "$caller"
      user          = "$user"
      requestTime   = "$requestTime"
      httpMethod    = "$httpMethod"
      resourcePath  = "$resourcePath"
      status        = "$status"
      error         = "$error"
      responseLength = "$responseLength"
    })
  }

  tags = var.tags
}

# API Gateway CloudWatch Logs
resource "aws_cloudwatch_log_group" "roadmap_api_logs" {
  name              = "/aws/apigateway/roadmap-api"
  retention_in_days = 14

  tags = var.tags
}