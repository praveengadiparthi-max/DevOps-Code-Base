variable "region" {
  description = "AWS region for the backend resources"
  type        = string
  default     = "us-east-1"
}

variable "bucket" {
  description = "Unique S3 bucket name for Terraform state"
  type        = string
}

variable "lock_table_name" {
  description = "DynamoDB table name for Terraform state locking"
  type        = string
  default     = "terraform-lock-table"
}

variable "tags" {
  description = "Tags applied to backend resources"
  type        = map(string)
  default     = {}
}
