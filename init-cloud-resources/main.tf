#define cloud resources

provider "aws" {
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
  region = var.AWS_REGION
}

#resource aws_s3_bucket "s3_bucket" {
#  bucket = "c15-stern-bucket-azure"
#  force_destroy = true
#}
data "aws_vpc" "c15-vpc" {
  id = var.AWS_VPC_ID
}

data "aws_db_subnet_group" "c15-public-group" {
  name = "c15-public-subnet-group"
}

resource "aws_security_group" "db_security_group" {
  name = "c15-stern-db-sg"
  vpc_id = data.aws_vpc.c15-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "allow_5432" {
  security_group_id = aws_security_group.db_security_group.id
  from_port = 5432
  to_port = 5432
  ip_protocol = "tcp" 
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_db_instance" "museum-db" {
  allocated_storage            = 10
  db_name                      = "museum"
  identifier                   = "c15-stern-museum-db"
  engine                       = "postgres"
  engine_version               = "16"
  instance_class               = "db.t3.micro"
  publicly_accessible          = true
  performance_insights_enabled = false
  skip_final_snapshot          = true
  db_subnet_group_name         = data.aws_db_subnet_group.c15-public-group.name
  vpc_security_group_ids       = [
    aws_security_group.db_security_group.id
  ]
  username                     = var.MUSEUM_DB_USERNAME
  password                     = var.MUSEUM_DB_PASSWORD
}

data "aws_ami" "al" {
  most_recent = true
  filter {
    name   = "image-id"
    values = ["ami-05c172c7f0d3aed00"]
  }
}

resource "aws_security_group" "ec2_security_group" {
  name = "c15-stern-ec2-sg"
  vpc_id = data.aws_vpc.c15-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 22 
  to_port = 22 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "db_recieve" {
  security_group_id = aws_security_group.ec2_security_group.id 
  from_port = 5432 
  to_port = 5432 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "db_send" {
  security_group_id = aws_security_group.ec2_security_group.id 
  from_port = 5432 
  to_port = 5432 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "http_recieve" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 80 
  to_port = 80 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "http_send" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 80 
  to_port = 80 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "https_recieve" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 443 
  to_port = 443 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "https_send" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 443 
  to_port = 443 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "kafka_recieve" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 9092 
  to_port = 9092 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "kafka_send" {
  security_group_id = aws_security_group.ec2_security_group.id
  from_port = 9092 
  to_port = 9092 
  ip_protocol = "tcp"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_instance" "kafka-pipeline-ec2" {
  ami                          = data.aws_ami.al.id
  instance_type                = "t2.micro"
  key_name                     = var.EC2_KEY_NAME
  associate_public_ip_address  = true
  subnet_id                    = var.EC2_SUBNET_ID
  vpc_security_group_ids       = [
    aws_security_group.ec2_security_group.id
  ]


  tags = {
    Name = "c15-stern-kafka-pipeline"
  }
}
