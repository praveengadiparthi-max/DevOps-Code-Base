provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source              = "./modules/vpc"
  cidr_block          = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  availability_zones  = var.availability_zones
  tags                = var.vpc_tags
}

module "Module_Example" {
  source       = "./modules/ec2_instance"
  ami_id       = var.ami_id
  instance_type = var.instance_type
  key_name     = var.key_name
  subnet_id    = element(module.vpc.public_subnet_ids, 0)
}
