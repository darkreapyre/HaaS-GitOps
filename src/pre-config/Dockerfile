FROM 763104351884.dkr.ecr.us-west-2.amazonaws.com/tensorflow-training:1.14.0-gpu-py36-cu100-ubuntu16.04

ENV HOROVOD_VERSION=0.18.1

RUN pip install --upgrade pip

# Install Horovod, temporarily using CUDA stubs
RUN ldconfig /usr/local/cuda-10.0/targets/x86_64-linux/lib/stubs && \
    HOROVOD_GPU_ALLREDUCE=NCCL HOROVOD_WITH_TENSORFLOW=1 pip install --no-cache-dir horovod==${HOROVOD_VERSION} && \
    ldconfig
    
# Install OpenSSH for MPI to communicate between containers
RUN apt-get install -y --no-install-recommends openssh-client openssh-server
RUN mkdir -p /var/run/sshd && \
  sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

RUN rm -rf /root/.ssh/ && \
  mkdir -p /root/.ssh/ && \
  ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa && \
  cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys && \
  printf "Host *\n  StrictHostKeyChecking no\n" >> /root/.ssh/config

RUN pip install awscli
RUN pip install boto3
RUN pip install ujson==1.35
RUN pip install opencv-python==4.1.0.25
RUN pip install Cython==0.28.4
RUN git clone https://github.com/cocodataset/cocoapi.git
RUN cd /cocoapi && git fetch origin 8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9
RUN cd /cocoapi && git reset --hard 8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9
RUN cd  /cocoapi/PythonAPI && make
RUN pip install -e /cocoapi/PythonAPI
RUN pip install matplotlib==3.0.3
RUN pip install markdown==3.1
RUN pip install numpy==1.17.5
RUN pip install git+https://www.github.com/keras-team/keras-contrib.git

##########################################################################################
# SageMaker requirements
##########################################################################################

COPY horovod/launch.py /launch.py 
COPY horovod/changehostname.c /changehostname.c 
COPY horovod/change-hostname.sh /usr/local/bin/change-hostname.sh 
# RUN cp /tmp/code/train.py /train.py 
 
RUN chmod +x /usr/local/bin/change-hostname.sh 

# ENTRYPOINT ["python3", "/launch.py"]