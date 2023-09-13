/******************************************
  AWS provider configuration
 *****************************************/

provider "aws" {
  region = var.region
}

/******************************************
  Variables
 *****************************************/

variable "account" {
  description = "AWS account name"
  type        = string
}

variable "region" {
  description = "Default AWS region for resources"
  type        = string
}

/******************************************
  VPC configuration
 *****************************************/

module "vpc-network" {
  source             = "../modules/vpc"
  availability_zones = 2
}

module "aws-sagemaker-role" {
  source = "../modules/sagemaker"
}

module "ecr" {
  source = "../modules/ecr"
}

module "ecs" {
  source          = "../modules/ecs"
  vpc_id          = module.vpc-network.network_id
  container_port  = 80
  public_subnet   = module.vpc-network.public_subnet
  private_subnet  = module.vpc-network.private_subnet
  container_image = "${var.account}.dkr.ecr.${var.region}.amazonaws.com/qa-app:latest"
  name            = "qa-app-ecs"
}