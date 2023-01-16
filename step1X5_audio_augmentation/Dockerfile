FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step1x5 .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step1x5 . --no-cache

# enable in case you want to install tools from contrib or non-free
# RUN sed -i 's/ main/ main contrib non-free/' /etc/apt/sources.list

RUN apt update

RUN apt install -y g++ make git procps nano

#################################################
# install augmentation tooling and dependencies
#################################################

RUN apt install -y python3 pip python3-numpy 

# use a fixed version of this library, later releases should work as well
RUN pip install audiomentations==0.28.0

