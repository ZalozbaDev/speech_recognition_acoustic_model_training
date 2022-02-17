FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step2 .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step2 . --no-cache

# enable in case you want to install tools from contrib or non-free
# RUN sed -i 's/ main/ main contrib non-free/' /etc/apt/sources.list

RUN apt update

# generic tools install 
RUN apt install -y g++ make git procps nano

##########################################
# Build dlabpro software (python wrapper)
##########################################

RUN git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
RUN cd dLabPro && git checkout 297f1dc7a6b86a7ed786f845e93e327576e913ae

# need to build the C++ part first
RUN apt install -y libreadline-dev portaudio19-dev
RUN cd dLabPro && make -C programs/dlabpro RELEASE

# the python wrapper probably needs these deps anyway
RUN apt install -y python3 python3-numpy python3-matplotlib python3-yaml

# additional python deps for building the wrapper
RUN apt install -y python3-distutils cython3

# now build the python wrapper
RUN cd dLabPro/programs/python && ./setup.py build && ./setup.py install

############################################
# Fetch UASR tooling
############################################

RUN git clone https://github.com/ZalozbaDev/UASR.git UASR
RUN cd UASR && git checkout 8ff6eb727dc303fff4c5556574caa0dae204a3e6

##########################################################
# Collect all files and actually run the labelling
##########################################################

# copy all files required to run labelling
ADD uasr-data /

RUN mkdir -p uasr-data/db-hsb-asr/HSB-01/flists uasr-data/db-hsb-asr/HSB-01/grammar uasr-data/db-hsb-asr/HSB-01/model uasr-data/db-hsb-asr/HSB-01/log

COPY inputs/flists           uasr-data/db-hsb-asr/HSB-01/flists
COPY inputs/grammar          uasr-data/db-hsb-asr/HSB-01/grammar
COPY inputs/info/classes.txt uasr-data/db-hsb-asr/HSB-01/info
COPY inputs/model            uasr-data/db-hsb-asr/HSB-01/model

# copy the to-be-labelled data (consider doing this differently with big amounts of data!)
RUN mkdir -p uasr-data/db-hsb-asr/common/sig uasr-data/db-hsb-asr/common/trl uasr-data/db-hsb-asr/common/lab

COPY inputs/sig uasr-data/db-hsb-asr/common/sig
COPY inputs/trl uasr-data/db-hsb-asr/common/trl

# now actually run the labelling
RUN /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp lab uasr-data/db-hsb-asr/HSB-01/info/label.cfg

# just a default instruction, might be handy
CMD ["/bin/bash"]

#########################################################
# how to fetch the labels from the container
#########################################################

## mkdir -p output && rm -rf ./output/* 
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step2 cp -r /uasr-data/db-hsb-asr/common/lab /output/
