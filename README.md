# Scalable Machine Learning Experiments using a Managed MlOps Pipeline (MMP) with GitOps integration

## Overview

The MMP solution allows you to create Machine Learning Experiments by leveraging a GitOps to train Machine Learning models at scale. To address your **complexity**, **cost**, and **span of control** requirements, the solution leverages a selection of back-end training frameworks, such as Amazon SageMaker, allowing you the flexibility to choose the right model training solution to fit your business objectives. The service further allows you manage these experiments through an Experiment Dashboard and makes it easier for you analyze each trained machine learning model and compare them individually, before deploying the best one into production.

## Requirements

### General Requirements
1. AWS Account.
2. Necessary Limits for GPU/CPU training instances in the appropriate AWS Region.
3. AWS CLI installed and configured.
4. Create a GitHub personal access [token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).

>__Note:__ This solution has only been tested in the *us-west-2* AWS Region.

### Training Requirements

The following list of requirements need to be implemented in the model training code before it can be leveraged by the MlOps Pipeline.
1. Fully configured and Horovod-optimized model **must** be called `train.py` and copied to the "root" of the source GitHub or CodeCommit repository.
2. Should any code from the GitHub/CodeCommit repository be installed, the repository must include a `setup.py` or a `requirements.txt`. The Horovod container includes commands to install these.
3. Make sure to import the Horovod library in the `train.py` script, for example:
    ```python
    import horovod
    ```
4. The `train.py` file **must** leverage Python `argparse()` functionality and must include the following mandatory parameters:
    - `--output-path`: This will automatically point to the "local" path where any model training checkpoints (i.e. if using `keras.callbacks.ModelCheckpoint()`) are stored. If SageMaker is leveraged as the training platform, this path will automatically point to the SageMaker output path and will store the fully strained (or check-pointed model) to Amazon S3.
    - `--dataset-path`: If using SageMaker as the training platform, this will automatically point to the local copy of the training/validation datasets copied from S3 during training instance deployment. Alternatively, if either the Deep Learning AMI or Kubernetes are used as the training platform, this will point to the FSx mount point.
    - `--dataset`: This is the name of the training/validation dataset that is populated from the experiment configuration's list of supported datasets.
    - For example:
        ```python
        # MlOps/Horovod Framework specific command line parameters
        parser.add_argument('--dataset-path', help='Path to the training dataset.', dest='dataset_path', type=str)
        parser.add_argument('--output-path', help='Path to the trained model output.', dest='output_path', type=str)
        parser.add_argument('--dataset', help='Training dataset Name.', dest='dataset_type')
        ```
5. All command line parameters Hyper-parameters, that will be executed by the `train.py` script must be configured in the `experiment_config.json` configuration file as a **JSON string** for example:
    ```json
    "Hyperparameters": "{'epochs': '40', 'batch_size': '32'}"
    ```
6. If any "local" directories need to be created, for example the `snapshot_path`, the directories need to be created within the `train.py` script.

## Deployment

1. A pre-packaged script has been provided to automatically deploy the solution into AWS. To execute this script, run the following command:
    ```bash
    bin/deploy
    ```
2. When prompted, enter the following:
    - The AWS Region you wish to deploy the solution in >
    - The name of the solution deployment > (__Note:__ This must be lower case!)
    - An e-mail address to send training updates >
    - Enter the GitHub Token > 
3. The `deploy` script will perform the following:
    - Create a "bootstrap" bucket on S3 to store the artifacts (i.e. CloudFormation templates, Lambda Source etc.).
    - Package and upload the __GitHub Webhook__ artifacts to S3.
    - Package and upload the _Experiment Management_ platform (MlFlow) artifacts to S3.
    - Package and upload the _MlOps Pipeline_ artifacts for each supported training platform (i.e. SageMaker) to S3.
    - Package and upload the _Launch Configuration_ artifacts (i.e. Lambda function to trigger the pipeline) to S3.
    - Create the master CloudFormation Stack that will deploy the various nested stacks for each component of the solution.
4. Once the entire stack has been deployed, wait for around **35 Minutes** for the master build container to complete, then click on the **Outputs** tab in the **CloudFormation Console**. Copy on the __WebHookApi__ link to create a GitHub Webhook.
5. Create a Webhook:
    1. Open the GitHub console for your Machine Learning code repository and click **Settings** and then **Webhooks** in the navigation panel.
    2. Click the **Add Webhook** button.
    3. Update as follows:
        - **Payload URL:** Enter the URL copied from the CloudFormation Outputs tab.
        - **Content type:** Select `application/json`.
        - Leave the defaults for the other fields and click **Add webhook**.

## Running the Machine Learning Experiment

1. To create a Machine Learning Experiment, create a file called `experiment.json` in your Machine Learning code repository, with the foillwing contents:
```json
{
    "Platform": "sagemaker",
    "Dataset_Name": "fashion",
    "Training_Instance": "ml.p3.16xlarge",
    "Instance_Count": "1",
    "Hyperparameters": "{'epochs': '40', 'batch-size': '32'}"
}
```
>__NOTE:__ A sample is provided in the `staging` directory after the deployment is finished.
2. Enter the desired configuration, specific to the experiment as follows:
    - __Platform:__ Currently only `sagemaker` is supported.
    - __Dataset_Name:__ The name of the dataset, e.g. `fashion` or `coco`.
    - __Training Instance Type:__ Select the type of CPU or GPU training instance required to run the experiment.
    - __Training Instance Count:__ Enter the number of CPU or GPU instances to be used to run the experiment.
    - __Training Hyper-parameters:__ Enter the experiment specific Hyper-parameters in the form of a JSON string.
3. Update and `commit` the experiment configuration to the Machine Learning code repository in the typical fashion, to trigger the GitOps Machine Learning Pipeline.
