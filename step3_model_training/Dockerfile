FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step3 .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step3 . --no-cache

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
# Collect all files and actually run the labelling
##########################################################

# copy all files required to run labelling
RUN mkdir -p uasr-data/db-hsb-asr/HSB-01/flists uasr-data/db-hsb-asr/HSB-01/grammar uasr-data/db-hsb-asr/HSB-01/log uasr-data/db-hsb-asr/HSB-01/info

COPY uasr-data/db-hsb-asr/HSB-01/info/* uasr-data/db-hsb-asr/HSB-01/info/

COPY inputs/flists/*         uasr-data/db-hsb-asr/HSB-01/flists/
COPY inputs/info/classes.txt uasr-data/db-hsb-asr/HSB-01/info/

# copy the to-be-labelled data (consider doing this differently with big amounts of data!)
RUN mkdir -p uasr-data/db-hsb-asr/common/sig/ADP/ uasr-data/db-hsb-asr/common/lab/ADP/ uasr-data/db-hsb-asr/common/sig/CV/ uasr-data/db-hsb-asr/common/lab/CV/  

COPY inputs/sig/ADP uasr-data/db-hsb-asr/common/sig/ADP/
COPY inputs/sig/CV  uasr-data/db-hsb-asr/common/sig/CV/
COPY inputs/lab/ADP uasr-data/db-hsb-asr/common/lab/ADP/
COPY inputs/lab/CV  uasr-data/db-hsb-asr/common/lab/CV/

# now actually run the labelling
RUN UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp trn uasr-data/db-hsb-asr/HSB-01/info/train.cfg 2>&1 | tee logfile.txt

# just a default instruction, might be handy
CMD ["/bin/bash"]

#########################################################
# how to fetch the labels from the container
#########################################################

## mkdir -p output && rm -rf ./output/* 
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step3 cp -r /uasr-data/db-hsb-asr/HSB-01/model/ /output/
