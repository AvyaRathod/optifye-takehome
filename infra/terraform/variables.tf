variable "region" {
  description = "AWS region for the Optifye take-home stack"
  type        = string
  default     = "ap-south-2"
}

variable "project_name" {
  description = "Project tag/prefix for naming resources"
  type        = string
  default     = "optifye-takehome"
}

variable "number_of_broker_nodes" {
  description = "MSK broker count"
  type        = number
  default     = 2
}

variable "kafka_version" {
  description = "Kafka version for MSK cluster"
  type        = string
  default     = "3.5.1"
}
