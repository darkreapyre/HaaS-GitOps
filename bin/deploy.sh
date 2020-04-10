#!/bin/bash

echo -n "Enter the AWS Region to use > "
read region
echo -n "Enter CloudFormation stackname to create (lower-case) > "
read stackname
echo -n "Enter the e-mail address for Pipeline Approval > "
read email
echo -n "Enter the GitHub Token > "
read token
DATE=$(date '+%m-%d-%Y')
TIME=$(date '+%H-%M')
bootstrap_bucket="${stackname}-bootstrap-${region}"

echo ""
echo -n "Creating Bootstrap S3 Bucket ..."
echo ""
aws s3 mb "s3://${bootstrap_bucket}" --region $region
aws s3api put-bucket-versioning --bucket $bootstrap_bucket --versioning-configuration Status=Enabled --region $region

echo ""
echo -n "Packaging Pre-Configuration Artifacts ..."
echo ""
cd ./src/pre-config
zip -r ../../staging/horovod-src.zip horovod/* Dockerfile
aws s3 cp ../../staging/horovod-src.zip "s3://${bootstrap_bucket}/artifacts/" --acl public-read --region $region
aws s3 cp ./pre-config-template.yaml "s3://${bootstrap_bucket}/templates/" --acl public-read --region $region
cd ../../

echo ""
echo -n "Packaging Webhook Artifacts ..."
echo ""
aws cloudformation package --region $region --s3-bucket $bootstrap_bucket --template ./src/webhook/webhook-template.yaml --output-template-file ./staging/webhook-template.yaml
aws s3 cp ./staging/webhook-template.yaml "s3://${bootstrap_bucket}/templates/" --acl public-read --region $region

echo ""
echo -n "Packaging Build Artifacts ..."
echo ""
cd ./src/container
zip -r ../../staging/container-src.zip Dockerfile
aws s3 cp ../../staging/container-src.zip "s3://${bootstrap_bucket}/artifacts/" --acl public-read --region $region
aws s3 cp ../templates/*build-template.json "s3://${bootstrap_bucket}/artifacts/" --acl public-read --region $region
cd ../../

echo ""
echo -n "Packaging Data Pre-Processing Artifacts ..."
echo ""
cd ./src
zip -r ../staging/scripts.zip scripts/*
aws s3 cp ../staging/scripts.zip "s3://${bootstrap_bucket}/artifacts/" --acl public-read --region $region
cd ../

echo ""
echo -n "Packaging SageMaker MlOps Artifacts ..."
echo ""
cd ./src/sm-mlops
aws cloudformation package --region $region --s3-bucket $bootstrap_bucket --template ./sm-mlops-template.yaml --output-template-file ../../staging/sm-mlops-template.yaml
aws s3 cp ../../staging/sm-mlops-template.yaml "s3://${bootstrap_bucket}/templates/" --ac public-read --region $region
cd ../../

echo ""
echo -n "Packaging Post-Configuration Artifacts ..."
echo ""
cd ./src/post-config
aws cloudformation package --region $region --s3-bucket $bootstrap_bucket --template ./post-config-template.yaml --output-template-file ../../staging/post-config-template.yaml
aws s3 cp ../../staging/post-config-template.yaml "s3://${bootstrap_bucket}/templates/" --ac public-read --region $region
cd ../../

echo ""
echo -n "Deploying CloudFormation Stack ..."
echo ""
aws cloudformation deploy --stack-name $stackname --template-file ./deployment-template.yaml --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides GitToken=$token EmailAddress=$email S3BootstrapBucket=$bootstrap_bucket --region $region

cat > ./staging/experiment.json <<EOF
{
    "Platform": "sagemaker",
    "Dataset_Name": "fashion",
    "Training_Instance": "ml.p3.8xlarge",
    "Instance_Count": "1",
    "Hyperparameters": "{'epochs': '40', 'batch-size': '32'}"
}
EOF