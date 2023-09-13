variable "vpc_id" {
  description = "VPC id"
  type        = string
}

variable "container_port" {
  description = "Container Port"
  type        = number
}

variable "name" {
  description = "Name for ECS Service"
  type        = string
}

variable "container_image" {
  description = "Name for ECS Service"
  type        = string
}

variable "private_subnet" {
  description = "value of private subnet id"
  type        = list(any)
}

variable "public_subnet" {
  description = "value of public subnet id"
  type        = list(any)
}

