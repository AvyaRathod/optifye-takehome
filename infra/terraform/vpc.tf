module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = "10.50.0.0/16"

  azs             = ["${var.region}a", "${var.region}b"]
  public_subnets  = ["10.50.1.0/24", "10.50.2.0/24"]
  private_subnets = ["10.50.11.0/24", "10.50.12.0/24"]

  enable_nat_gateway         = true
  single_nat_gateway         = true
  enable_dns_hostnames       = true
  manage_default_route_table = false

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
    Name                     = "${var.project_name}-public"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
    Name                              = "${var.project_name}-private"
  }

  tags = {
    Project     = var.project_name
    Environment = "development"
  }
}
