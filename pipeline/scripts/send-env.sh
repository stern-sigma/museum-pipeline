source .env
scp -i ec2-key.pem .env ubuntu@${EC2_DNS}:~/museum-pipeline/pipeline/
