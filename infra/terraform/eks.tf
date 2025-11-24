module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project_name}-cluster"
  cluster_version = "1.29"

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = concat(module.vpc.public_subnets, module.vpc.private_subnets)
  control_plane_subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  eks_managed_node_groups = {
  main = {
    desired_size = 1
    min_size     = 1
    max_size     = 1

    instance_types = ["t3.small"]

    iam_role_arn = aws_iam_role.eks_node.arn

    subnet_ids = module.vpc.private_subnets

    tags = {
      Project = var.project_name
    }
  }
}

  tags = {
    Project = var.project_name
  }
}
