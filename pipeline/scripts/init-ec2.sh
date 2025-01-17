source .env
ssh -t -i ec2-key.pem ubuntu@${EC2_DNS} "
  sudo apt update -y
  sudo apt upgrade -y
  sudo apt install software-properties-common -y
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt update -y
  sudo apt install python3.13 python3.13-venv git -y
  rm -rf museum-pipeline
  git clone https://github.com/stern-sigma/museum-pipeline --no-checkout
  cd museum-pipeline
  git sparse-checkout init --cone
  git sparse-checkout set pipeline/pyproject.toml pipeline/src pipeline/conf_logging.json
  git checkout main
  git pull origin main
  cd pipeline
  mkdir logs
  python3.13 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -e .
"
scp -i ec2-key.pem .env ubuntu@${EC2_DNS}:museum-pipeline/pipeline
ssh -t -i ec2-key.pem ubuntu@${EC2_DNS} "
  cd museum-pipeline/pipeline
  pwd
  pkill -15 python3.13
  source .venv/bin/activate
  nohup python3.13 -m museum_pipeline.lms_kafka_pipeline -store >> logs/pipeline.jsonl 2>&1 & disown
  nohup python3.13 -m museum_pipeline.lmnh_kafka_pipeline -store >> logs/pipeline.jsonl 2>&1 & disown
  echo 'Initialsed kafka pipeline'
  cat logs/pipeline.jsonl
"
git sparse-checkout disable
