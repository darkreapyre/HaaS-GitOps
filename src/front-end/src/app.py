#!/usr/bin/env python
import boto3, json
from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from sm_form import SMForm
from eks_form import EKSForm
from ami_form import AMIForm
from random import choice
import os

class Config(object):
    SECRET_KEY = '78w0o5tuuGex5Ktk8VvVDF9Pw3jv1MVE'

app = Flask(__name__)
app.config.from_object(Config)

Bootstrap(app)

@app.route('/index.html')
@app.route('/')
def index():
    return render_template('index.html', dashboard=os.environ['DASHBOARD_URL'])

@app.route('/smcreate', methods=['GET', 'POST'])
def create_sm_experiment():
    form = SMForm(request.form)
    if not form.validate_on_submit():
        return render_template('create_sm_experiment.html', form=form)
    if request.method == 'POST':
        S3_BUCKET_NAME = os.environ['S3_BUCKET']
        print(S3_BUCKET_NAME) # Debug
        S3_OBJECT_NAME = "experiment_config.json"
        time_stamp = str(datetime.now()).split(' ')
        date = time_stamp[0]
        time = time_stamp[1].replace(':', '-').split('.')[0]
        experiment = {}
        experiment['Model_Name'] = request.form.get('Model_Name')
        experiment['Version'] = request.form.get('Version')
        experiment['Description'] = 'Experiment created on {} at {}.'.format(date, time)
        experiment['Platform'] = 'sagemaker'
        experiment['Dataset_Name'] = request.form.get('Dataset_Name')
        experiment['GitHub_User'] = request.form.get('Github_User')
        experiment['GitHub_Repo'] = request.form.get('Github_Repo')
        experiment['Dashboard_URL'] = os.environ['DASHBOARD_URL']
        experiment['Training_Instance'] = request.form.get('Training_Instance')
        experiment['Instance_Count'] = request.form.get('Instance_Count')
        experiment['Hyperparameters'] = request.form.get('Hyperparameters')
        S3_OBJECT_JSON = json.dumps(experiment)
        s3 = boto3.resource('s3')
        s3.Object(S3_BUCKET_NAME, S3_OBJECT_NAME).put(Body=S3_OBJECT_JSON)
        return render_template('experiment_created.html', dashboard=os.environ['DASHBOARD_URL'], name=experiment['Model_Name'])

@app.route('/ekscreate', methods=['GET', 'POST'])
def create_eks_experiment():
    form = EKSForm(request.form)
    if not form.validate_on_submit():
        return render_template('create_eks_experiment.html', form=form)
    if request.method == 'POST':
        S3_BUCKET_NAME = os.environ['S3_BUCKET']
        print(S3_BUCKET_NAME) # Debug
        S3_OBJECT_NAME = "experiment_config.json"
        time_stamp = str(datetime.now()).split(' ')
        date = time_stamp[0]
        time = time_stamp[1].replace(':', '-').split('.')[0]
        experiment = {}
        experiment['Model_Name'] = request.form.get('Model_Name')
        experiment['Version'] = request.form.get('Version')
        experiment['Description'] = 'Experiment created on {} at {}.'.format(date, time)
        experiment['Platform'] = 'eks'
        experiment['Dataset_Name'] = request.form.get('Dataset_Name')
        experiment['GitHub_User'] = request.form.get('Github_User')
        experiment['GitHub_Repo'] = request.form.get('Github_Repo')
        experiment['Dashboard_URL'] = os.environ['DASHBOARD_URL']
        experiment['Training_Instance'] = request.form.get('Training_Instance')
        experiment['Instance_Count'] = request.form.get('Instance_Count')
        experiment['Hyperparameters'] = request.form.get('Hyperparameters')
        S3_OBJECT_JSON = json.dumps(experiment)
        s3 = boto3.resource('s3')
        s3.Object(S3_BUCKET_NAME, S3_OBJECT_NAME).put(Body=S3_OBJECT_JSON)
        return render_template('experiment_created.html', dashboard=os.environ['DASHBOARD_URL'], name=experiment['Model_Name'])


@app.route('/amicreate', methods=['GET', 'POST'])
def create_ami_experiment():
    form = AMIForm(request.form)
    if not form.validate_on_submit():
        return render_template('create_ami_experiment.html', form=form)
    if request.method == 'POST':
        S3_BUCKET_NAME = os.environ['S3_BUCKET']
        print(S3_BUCKET_NAME) # Debug
        S3_OBJECT_NAME = "experiment_config.json"
        time_stamp = str(datetime.now()).split(' ')
        date = time_stamp[0]
        time = time_stamp[1].replace(':', '-').split('.')[0]
        experiment = {}
        experiment['Model_Name'] = request.form.get('Model_Name')
        experiment['Version'] = request.form.get('Version')
        experiment['Description'] = 'Experiment created on {} at {}.'.format(date, time)
        experiment['Platform'] = 'dlami'
        experiment['Dataset_Name'] = request.form.get('Dataset_Name')
        experiment['GitHub_User'] = request.form.get('Github_User')
        experiment['GitHub_Repo'] = request.form.get('Github_Repo')
        experiment['Dashboard_URL'] = os.environ['DASHBOARD_URL']
        experiment['Training_Instance'] = request.form.get('Training_Instance')
        experiment['Instance_Count'] = request.form.get('Instance_Count')
        experiment['Hyperparameters'] = request.form.get('Hyperparameters')
        S3_OBJECT_JSON = json.dumps(experiment)
        s3 = boto3.resource('s3')
        s3.Object(S3_BUCKET_NAME, S3_OBJECT_NAME).put(Body=S3_OBJECT_JSON)
        return render_template('experiment_created.html', dashboard=os.environ['DASHBOARD_URL'], name=experiment['Model_Name'])

# Note: The following can be used for multi-user experiments
# @app.route('/user/<user_date>/<user_key>')
# def show_user_data(user_date,user_key):
#     S3_SUB_BUCKET_NAME = user_date
#     S3_OBJECT_NAME = user_key
#     obj = s3.Object(S3_BUCKET_NAME, '{}/{}.json'.format(S3_SUB_BUCKET_NAME, S3_OBJECT_NAME))
#     user_json = obj.get()['Body'].read().decode('utf-8')
#     return render_template( 'show_data_template.html', user_json = json.loads(user_json) )

if __name__ == '__main__':
    app.run()
# Local testing
#    app.run(host='0.0.0.0', port='80', debug=True)