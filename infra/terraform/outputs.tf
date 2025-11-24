output "vpc_id" {
  description = "ID of the primary VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "msk_bootstrap_brokers" {
  description = "TLS bootstrap brokers for MSK"
  value       = aws_msk_cluster.video_pipeline.bootstrap_brokers_tls
}


output "s3_bucket_name" {
  description = "Artifact bucket for annotated frames"
  value       = aws_s3_bucket.inference_output.bucket
}
