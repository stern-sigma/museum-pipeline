# MUSEUM PIPELINE

This is a lightweight module designed to establish an [RDS database](https://aws.amazon.com/rds/), then pipe museum kiosk data to it via an [AWS EC2](https://aws.amazon.com/ec2/).

It was designed for the __Liverpool Museum of Natural History__, and handles:
  - Database initialisation and configuration
  - Database seeding
  - Data uploads to the database 

## Setup and installation

### What you will need:
  - [AWS security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html) with permissions to create and update databases
  - An [AWS VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html) with an accessable [PostgreSQL RDS instance](https://aws.amazon.com/rds/postgresql/) spun up 
  - An [AWS EC2 key pair](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
  - For .csv version:
    - An [AWS S3 bucket](https://aws.amazon.com/s3/) with .csv files formatted as expected (see below).
  - For Kafka version:
    - A [Kafka Stream](https://www.confluent.io/learn/kafka-streams/https://www.confluent.io/learn/kafka-streams/) with the [topic](https://developer.confluent.io/courses/apache-kafka/topics/) `lmnh`, and messages formatted as below.
  - For automated deployment:
    - A GitHub account

### Requirements:
  - Python >=3.13
    (The required packages can be installed in a [venv](https://docs.python.org/3/library/venv.html) using `pip install -r pipeline/requirements.txt`)
  - [psql](https://www.postgresql.org/docs/current/app-psql.html)
  - [terraform](https://www.terraform.io/)

### Expected `.csv` structure:
filename: `lmnh_hist_data_<int:02>.csv`
```
at          | site  | val   | type 
============|=======|=======|========
<timestamp> | <int> | <int> | <float>
```
### Expected message structure:
```
{
  'at': <str: ISO8601 datetime>,
  'site': <str: int of exhibition public id>,
  'val': <int: int of rating value, or -1 if event is a request>,
  'type': <optional[int]: int of request value>
}
```

### Create the database
1. In the `cloud-stuff` directory, create a file named `terraform.tfvars`
2. Configure `terraform.tfvars` as follows:
```
AWS_ACCESS_KEY = "<your AWS access key>"
AWS_SECRET_KEY = "<your AWS secret key>"
AWS_VPC_ID = "<your aws VPC ID>"
MUSEUM_DB_USERNAME = "<the username you want to use for your database>"
MUSEUM_DB_PASSWORD = "<the password you want to use for your database>"
EC2_KEY_NAME = "<the name of your EC2 key pair>"
EC2_SUBNET_ID = "<the id of the subnet you want you EC2 instance to be initialised on>"
```
3. Still in the `cloud-stuff`, run `terraform apply`, answering `yes` and storing the URLs it returns after it runs 
  (Warning: this takes about 6 minutes, but this is normal; just let the command run.)

### Configure environment variables
1. In the `pipeline` directory, create a file named `.env`
2. Configure `.env` as follows:
```
AWS_ACCESS_KEY=<your AWS access key>
AWS_SECRET_KEY=<your AWS secret key>
PIPELINE_TARGET_HOST=<the DB URL returned by the terraform apply command>
PIPELINE_TARGET_USER=<MUSEUM_DB_USERNAME>
PIPELINE_TARGET_PASSWORD=<MUSEUM_DB_PASSWORD>
PIPELINE_TARGET_DBNAME=museum
PIPELINE_TARGET_PORT=5432
EC2_DNS=<the URL returned by the terraform apply command>

```
  - If uploading from `.csv` on S3:
```
S3_BUCKET=<the name of your S3 bucket>
```

  - If uploading from Kafka:
```
KAFKA_BOOTSTRAP_SERVERS=<kafka bootstrap sever url>
KAFKA_SECURITY_PROTOCOL=<kafka secuirty protocol name>
KAFKA_SASL_MECHANISMS=<kafka sasl mechanisms>
KAFKA_SASL_USERNAME=<kafka sasl username>
KAFKA_SASL_PASSWORD=<kafka sasl password>
KAFKA_GROUP_ID=<arbitary consumer group name>
```

### Seed the database
1. In the `pipeline` directory, run the following command:
```
bash scripts/init-db.sh
```


## Deploy
### S3 bucket
Uploading from an S3 bucket is simple. You should have already configured the name in your environment variables. After that there is only one command to run from the `pipeline` directory:
```
python3 pipeline.py [
  -config_logging (enable command-line configuration of logging)
    -stdout [true/false] (log to console, false by default)
    -file [true/false] (log to pipeline/logs/pipeline.jsonl, true by default)
  -bucket <str> (name of S3 bucket to load from, default to S3_BUCKET)
  -rows (maximum number of rows to upload to the database, default none)
] 
```

### Kafka
Uploading from Kafka is similarly simple. From the `pipeline` directory, simply execute this command instead:
```
python3 kafka_pipeline.py [
  -store (switch output stream from stdout to logs/pipeline.jsonl)
]
```

### EC2
Execute the following command from the `pipeline` directory:
```
bash scripts/init-ec2.sh
```
This will build the application and deploy the Kafka pipelines for LMS and LMNH.
## Dev info
### CI/CD 
This repository supports a CI/CD workflow.
### Advanced logging configuration
  - For most use cases, adjusting the handlers used by the `queue_handler` in `pipeline/conf_logging.json` should be sufficient.
  - Also feel free to modify the file more generally to your needs.
    (Note: custom handlers should be listed with `queue_handler`, not `root`, in order to prevent blocking).
  - For more advanced loggers, scripts and objects should be stored in `pipeline/pipeline_logger.py`

### Anatomy
  - All functions to bring in data are handled by `extract.py`
  - All functions to modify data are handled by `transform.py`
  - All functions to upload data are handled by `load.py`
  - `pipeline.py` itself imports these functions and adds CLI functionality.
  - Kafka behaviour is almost entirely described in `kafka_pipeline.py`

### Database exploration
On account of the fact that `psql` is long-winded, devs wishing to interrogate the database may avail themselves of the `connect-db.sh` script in the `pipeline` directory.
