 variable "ami_id" {
    description = "The AMI ID to use for the EC2 instance"
    type        = string    
}

variable "instance_type" {
    description = "The instance type for the EC2 instance"
    type        = string
}

variable "subnet_id" {
  description = "Optional subnet id to place the instance into"
  type        = string
  default     = null
}

variable "key_name" {
  description = "The key pair name to use for SSH access"
  type        = string
  default     = null
}