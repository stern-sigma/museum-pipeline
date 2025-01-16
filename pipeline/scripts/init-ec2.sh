source .env
ssh -i ec2-key.pem ubuntu@${EC2_DNS}
sudo apt update
sudo apt upgrade
sudo apt install software-properties-common
sudo add-apt-repository ppa/deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-pip python3.13-venv git
