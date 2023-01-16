FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step4 .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step4 . --no-cache

# enable in case you want to install tools from contrib or non-free
# RUN sed -i 's/ main/ main contrib non-free/' /etc/apt/sources.list

RUN apt update

# generic tools install 
RUN apt install -y g++ make git procps nano

##########################################
# Build dlabpro software (python wrapper)
##########################################

RUN git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
RUN cd dLabPro && git checkout 8b8a01b973356f974c4083510fa0275a4e53cf40

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
# Collect all files and actually run the adaptation
##########################################################

# copy all files required to run adaptation
RUN mkdir -p uasr-data/db-hsb-asr/HSB-01/flists uasr-data/db-hsb-asr/HSB-01/log uasr-data/db-hsb-asr/HSB-01/info uasr-data/db-hsb-asr/HSB-01/lexicon uasr-data/db-hsb-asr/HSB-01/model

COPY uasr-data/db-hsb-asr/HSB-01/info/* uasr-data/db-hsb-asr/HSB-01/info/

COPY inputs/flists/*         uasr-data/db-hsb-asr/HSB-01/flists/
COPY inputs/info/classes.txt uasr-data/db-hsb-asr/HSB-01/info/
COPY inputs/lexicon/*        uasr-data/db-hsb-asr/HSB-01/lexicon/
COPY inputs/model/*          uasr-data/db-hsb-asr/HSB-01/model/

# copy the adaptation/test data (consider doing this differently with big amounts of data!)
RUN mkdir -p uasr-data/db-hsb-asr/common/sig/ADP/ uasr-data/db-hsb-asr/common/lab/ADP/  uasr-data/db-hsb-asr/common/trl/ADP/  

COPY inputs/sig/ADP  uasr-data/db-hsb-asr/common/sig/ADP/
COPY inputs/lab/ADP  uasr-data/db-hsb-asr/common/lab/ADP/
COPY inputs/trl/ADP  uasr-data/db-hsb-asr/common/trl/ADP/

# now actually run the adaptation
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp adp uasr-data/db-hsb-asr/HSB-01/info/adapt.cfg

# eval before/after with lexicon
RUN echo "=================================================================="
RUN echo "=================================================================="
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/adapt.cfg -Puasr.am.eval.mode="0" -Puasr.am.model="3_7"  | sed -n -e '/Evaluation result/,$p'
RUN echo "=================================================================="
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/adapt.cfg -Puasr.am.eval.mode="0" -Puasr.am.model="3_7_A"  | sed -n -e '/Evaluation result/,$p'


# eval before/after with free phoneme recognition
RUN echo "=================================================================="
RUN echo "=================================================================="
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/eval.cfg -Puasr.am.model="3_7"  | sed -n -e '/Evaluation result/,$p'
RUN echo "=================================================================="
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/eval.cfg -Puasr.am.model="3_7_A"  | sed -n -e '/Evaluation result/,$p'


#COPY eval/* /

# just a default instruction, might be handy
CMD ["/bin/bash"]

#########################################################
# how to fetch the trained models from the container
#########################################################

## mkdir -p output && rm -rf ./output/* 
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step4 cp -r /uasr-data/db-hsb-asr/HSB-01/model/ /output/

#########################################################
# how to run evaluation of model(s)
#########################################################

## evaluate model X_Y.hmm
## docker run -it speech_recognition_acoustic_model_training_step4  /run_evaluation.sh X_Y

## evaluate model A_B.hmm and write label files
## mkdir -p labels && rm -rf ./labels/*
## docker run --mount type=bind,source="$(pwd)"/labels,target=/uasr-data/db-hsb-asr/HSB-01/log/ -it speech_recognition_acoustic_model_training_step4  /run_evaluation.sh X_Y LABELFILES


