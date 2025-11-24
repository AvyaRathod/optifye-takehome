resource "aws_s3_bucket" "inference_output" {
  bucket = "${var.project_name}-annotated-frames"

  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_public_access_block" "inference_output" {
  bucket = aws_s3_bucket.inference_output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "inference_output" {
  bucket = aws_s3_bucket.inference_output.id

  versioning_configuration {
    status = "Enabled"
  }
}
