resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-full-access-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "sagemaker_full_access_policy" {
  name = "sagemaker-full-access-policy"

  description = "Full access to SageMaker resources"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "sagemaker:*",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "attach_full_access_policy" {
  name       = "sagemaker-full-access-attachment"
  policy_arn = aws_iam_policy.sagemaker_full_access_policy.arn
  roles      = [aws_iam_role.sagemaker_role.name]
}

resource "aws_iam_policy" "s3_full_access_policy" {
  name = "s3-full-access-policy"

  description = "Full access to Amazon S3 resources"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "s3:*",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "attach_s3_full_access_policy" {
  name       = "s3-full-access-attachment"
  policy_arn = aws_iam_policy.s3_full_access_policy.arn
  roles      = [aws_iam_role.sagemaker_role.name]
}