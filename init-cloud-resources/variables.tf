variable "AWS_ACCESS_KEY" {
    type = string
}

variable "AWS_SECRET_KEY" {
    type = string
}

variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable "AWS_VPC_ID" {
    type = string
}

variable "MUSEUM_DB_USERNAME" {
  type = string
}

variable "MUSEUM_DB_PASSWORD" {
  type = string
}

variable "EC2_KEY_NAME" {
  type = string
}

variable "EC2_SUBNET_ID" {
  type = string
}
