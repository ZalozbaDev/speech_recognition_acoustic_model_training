FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step1 .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step1 . --no-cache

# enable in case you want to install tools from contrib or non-free
# RUN sed -i 's/ main/ main contrib non-free/' /etc/apt/sources.list

RUN apt update

# generic tools install 
RUN apt install -y g++ make git procps nano

############################################
# Generate "classes.txt" file from scratch
############################################

# install tools for running "BASgenerator.py"
RUN apt install -y python3 python3-numpy python3-matplotlib python3-yaml

# clone the repo that contains all data for generating the "classes.txt" file
RUN git clone https://github.com/ZalozbaDev/speech_recognition_corpus_creation.git speech_recognition_corpus_creation
RUN cd speech_recognition_corpus_creation && git checkout 73d51bdb710ba5692f93c93c671e0e4de6710c2d

RUN mkdir corpus_creation/ && cp /speech_recognition_corpus_creation/examples/ex5/input/* corpus_creation/
RUN cd corpus_creation/ && python3 BASgenerator.py HSB.yaml || /bin/true

############################################
# Fetch german acoustic model
############################################

RUN git clone https://github.com/ZalozbaDev/db-hsb-asr.git db-hsb-asr
RUN cd db-hsb-asr && git checkout 8e86fb8171b58cc794e585433e4da7d2ea88a438

##########################################
# Build dlabpro software (python wrapper)
##########################################

RUN git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
RUN cd dLabPro && git checkout 297f1dc7a6b86a7ed786f845e93e327576e913ae

# add a compile fix for Debian Bullseye
#RUN git config --global user.email "daniel.sobe@sorben.com"
#RUN git config --global user.name "Daniel Sobe"
#RUN cd dLabPro && git cherry-pick 29c71b09c61626a30e52c84e9b9ac0586ec2bd0d

# need to build the C++ part first
RUN apt install -y libreadline-dev portaudio19-dev
RUN cd dLabPro && make -C programs/dlabpro RELEASE

# additional python deps for building the wrapper
RUN apt install -y python3-distutils cython3

# now build the python wrapper
RUN cd dLabPro/programs/python && ./setup.py build && ./setup.py install

##########################################################
# Collect all files and actually run the model adaptation
##########################################################

# create folder and copy all files
RUN mkdir /adaptation

ADD hsb.yaml /adaptation
ADD mapAM.py /adaptation

RUN cp corpus_creation/uasr_configurations/info/classes.txt /adaptation/
RUN cp db-hsb-asr/model/default/3_20.hmm                    /adaptation/
RUN cp db-hsb-asr/model/default/feainfo.object              /adaptation/

# now actually run the adaptation
RUN cd /adaptation/ && chmod 755 mapAM.py && UASR_HOME="dummy" ./mapAM.py hsb.yaml

# just a default instruction, might be handy
CMD ["/bin/bash"]

#########################################################
# how to fetch the resulting model from the container
#########################################################

## mkdir -p output && rm -rf ./output/* 
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step1 cp /adaptation/hsb.hmm /output/
