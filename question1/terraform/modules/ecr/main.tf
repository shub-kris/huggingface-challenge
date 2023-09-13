resource "aws_ecr_repository" "app_ecr_repo" {
  name                 = var.ecr_name # Replace with your desired repository name
  image_tag_mutability = var.image_mutability
  tags                 = var.tags
  image_scanning_configuration {
    scan_on_push = true
  } # Enable image scanning on push
}

resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.app_ecr_repo.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "keep last 10 images"
      action = {
        type = "expire"
      }
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
    }]
  })
}
