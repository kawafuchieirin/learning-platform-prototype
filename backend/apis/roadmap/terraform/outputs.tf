# ロードマップAPI Terraform出力値

output "lambda_function_arn" {
  description = "ARN of the roadmap Lambda function"
  value       = aws_lambda_function.roadmap_api.arn
}

output "lambda_function_name" {
  description = "Name of the roadmap Lambda function"
  value       = aws_lambda_function.roadmap_api.function_name
}

output "api_gateway_rest_api_id" {
  description = "ID of the roadmap API Gateway REST API"
  value       = aws_api_gateway_rest_api.roadmap_api.id
}

output "api_gateway_stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.roadmap_api.stage_name
}

output "api_gateway_invoke_url" {
  description = "Invoke URL for the roadmap API"
  value       = aws_api_gateway_stage.roadmap_api.invoke_url
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.roadmap_api.execution_arn
}