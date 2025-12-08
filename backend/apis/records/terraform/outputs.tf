# 学習記録API Terraform出力値

output "lambda_function_arn" {
  description = "ARN of the records Lambda function"
  value       = aws_lambda_function.records_api.arn
}

output "lambda_function_name" {
  description = "Name of the records Lambda function"
  value       = aws_lambda_function.records_api.function_name
}

output "api_gateway_rest_api_id" {
  description = "ID of the records API Gateway REST API"
  value       = aws_api_gateway_rest_api.records_api.id
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.records_api.stage_name
}

output "api_gateway_invoke_url" {
  description = "Invoke URL for the records API"
  value       = aws_api_gateway_stage.records_api.invoke_url
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.records_api.execution_arn
}