output "DB_URL" {
    value = aws_db_instance.museum-db.address
}

output "EC2_DNS" {
  value = aws_instance.kafka-pipeline-ec2.public_dns
}
