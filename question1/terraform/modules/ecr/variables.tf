variable "ecr_name" {
  description = "ECR name"
  type        = string
  default     = "gradio-qa-app"
}
variable "tags" {
  description = "The key-value maps for tagging"
  type        = map(string)
  default     = {}
}
variable "image_mutability" {
  description = "Provide image mutability"
  type        = string
  default     = "MUTABLE"
}