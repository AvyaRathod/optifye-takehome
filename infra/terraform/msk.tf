resource "aws_kms_key" "msk" {
  description             = "KMS key for ${var.project_name} MSK cluster"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Project = var.project_name
  }
}

resource "aws_kms_alias" "msk" {
  name          = "alias/${var.project_name}-msk"
  target_key_id = aws_kms_key.msk.id
}

resource "aws_msk_configuration" "video_pipeline" {
  name           = "${var.project_name}-msk-config"
  kafka_versions = [var.kafka_version]

  server_properties = <<-EOT
auto.create.topics.enable = true
delete.topic.enable = true
EOT
}

resource "aws_msk_cluster" "video_pipeline" {
  cluster_name           = "${var.project_name}-msk"
  kafka_version          = var.kafka_version
  number_of_broker_nodes = var.number_of_broker_nodes

  broker_node_group_info {
    instance_type   = "kafka.m5.large"
    client_subnets  = module.vpc.private_subnets
    security_groups = [aws_security_group.msk.id]
  }

  encryption_info {
    encryption_at_rest_kms_key_arn = aws_kms_key.msk.arn
  }

  configuration_info {
    arn      = aws_msk_configuration.video_pipeline.arn
    revision = aws_msk_configuration.video_pipeline.latest_revision
  }

  tags = {
    Project = var.project_name
  }

  # TODO: Configure logging_info, monitoring, and open monitoring settings.
}

resource "aws_security_group" "msk" {
  name        = "${var.project_name}-msk-sg"
  description = "Security group for MSK brokers"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "Kafka broker access"
    from_port   = 9094
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = ["10.50.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = var.project_name
  }
}
