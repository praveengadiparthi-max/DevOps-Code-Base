terraform {
  backend "s3" {
    bucket         = "praveen-tf-state-2026-001"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock-table"
    encrypt        = true
  }
}
