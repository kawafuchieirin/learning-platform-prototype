output "lambda_function_name" {
  description = "Analytics Lambda関数名"
  value       = aws_lambda_function.analytics_lambda.function_name
}

output "lambda_function_arn" {
  description = "Analytics Lambda関数ARN"
  value       = aws_lambda_function.analytics_lambda.arn
}

output "lambda_invoke_arn" {
  description = "Analytics Lambda呼び出しARN（API Gateway用）"
  value       = aws_lambda_function.analytics_lambda.invoke_arn
}

output "lambda_role_arn" {
  description = "Analytics Lambda実行ロールARN"
  value       = aws_iam_role.analytics_lambda_role.arn
}

output "lambda_function_url" {
  description = "Analytics Lambda関数URL（開発環境のみ）"
  value       = var.environment == "dev" ? aws_lambda_function_url.analytics_lambda_url[0].function_url : null
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch Logsグループ名"
  value       = aws_cloudwatch_log_group.analytics_lambda_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch LogsグループARN"
  value       = aws_cloudwatch_log_group.analytics_lambda_logs.arn
}

# モニタリング関連
output "error_alarm_name" {
  description = "エラー率アラーム名"
  value       = aws_cloudwatch_metric_alarm.analytics_error_rate.alarm_name
}

output "duration_alarm_name" {
  description = "実行時間アラーム名"
  value       = aws_cloudwatch_metric_alarm.analytics_duration.alarm_name
}

# デバッグ情報
output "lambda_environment_variables" {
  description = "Lambda環境変数"
  value       = aws_lambda_function.analytics_lambda.environment[0].variables
  sensitive   = true
}

output "service_endpoints" {
  description = "サービスエンドポイント情報"
  value = {
    lambda_name = aws_lambda_function.analytics_lambda.function_name
    lambda_url  = var.environment == "dev" ? aws_lambda_function_url.analytics_lambda_url[0].function_url : null
    region      = var.aws_region
    environment = var.environment
  }
}