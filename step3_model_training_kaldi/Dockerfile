FROM debian:bullseye-slim
MAINTAINER Daniel Sobe <daniel.sobe@sorben.com>

# normal call
# docker build -t speech_recognition_acoustic_model_training_step3_kaldi .

# rebuild from scratch
# docker build -t speech_recognition_acoustic_model_training_step3_kaldi . --no-cache

# enable in case you want to install tools from contrib or non-free
RUN sed -i 's/ main/ main contrib non-free/' /etc/apt/sources.list

RUN apt update

RUN apt install -y g++ make git procps nano

############################################
# Install Kaldi
############################################

RUN git clone https://github.com/ZalozbaDev/kaldi.git

RUN apt install -y zlib1g-dev automake autoconf bzip2 unzip wget sox gfortran libtool subversion python2.7 python3 

RUN DEBIAN_FRONTEND=noninteractive apt install -y intel-mkl

# install tools
RUN cd kaldi/tools/ && ./extras/check_dependencies.sh

RUN cd kaldi/tools/ && make -j 8 

# install additional irstlm
RUN cd kaldi/tools/ && ./extras/install_irstlm.sh

RUN apt install -y pip python3-numpy 

# no, not kaldi_io (!!!)
# RUN cd kaldi/tools/ && ./extras/install_kaldi_io.sh
RUN pip install kaldiio

# install Kaldi itself
RUN /bin/bash -c 'source /kaldi/tools/env.sh && cd /kaldi/src/ && ./configure --shared' 

RUN /bin/bash -c 'source /kaldi/tools/env.sh && cd /kaldi/src/ && make depend -j 8'

RUN /bin/bash -c 'source /kaldi/tools/env.sh && cd /kaldi/src/ && make -j 8'

##########################################
# Build dlabpro software (incl. python wrapper)
##########################################

RUN git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
RUN cd dLabPro && git checkout ec4d0ab71d50b061471feebc02f27333c52b1ca6

# cherry-picking needs identity first
RUN git config --global user.email "you@example.com"
RUN git config --global user.name "Your Name"

# fix building issue due to changed make syntax
RUN cd dLabPro && git cherry-pick 297f1dc7a6b86a7ed786f845e93e327576e913ae

# need to build the C++ part first
RUN apt install -y libreadline-dev portaudio19-dev
RUN cd dLabPro && make -C programs/dlabpro RELEASE

# the python wrapper probably needs these deps anyway
RUN apt install -y python3 python3-numpy python3-matplotlib python3-yaml

# additional python deps for building the wrapper
RUN apt install -y python3-distutils cython3

# now build the python wrapper
RUN cd dLabPro/programs/python && make

############################################
# Fetch UASR tooling
############################################

RUN git clone https://github.com/ZalozbaDev/UASR.git uasr
RUN cd uasr && git checkout 2452801de688d0843edd718e5cd1a9c41c8fc90c

############################################
# Collect all necessary files
############################################

# kaldi recipe
RUN mkdir -p /kaldi/egs/hsb/
COPY inputs/kaldi_recipe/hsb/ /kaldi/egs/hsb/
# RUN ls -l /kaldi/egs/hsb/

# training & eval data
RUN mkdir -p /uasr-data/db-hsb-asr/common/sig
RUN mkdir -p /uasr-data/db-hsb-asr/common/trl
RUN mkdir -p /uasr-data/db-hsb-asr/common/lab
COPY inputs/sig/ /uasr-data/db-hsb-asr/common/sig/
COPY inputs/trl/ /uasr-data/db-hsb-asr/common/trl/
COPY inputs/lab/ /uasr-data/db-hsb-asr/common/lab/

# copy config data
RUN mkdir -p /uasr-data/db-hsb-asr/HSB-P3/flists
RUN mkdir -p /uasr-data/db-hsb-asr/HSB-P3/info
RUN mkdir -p /uasr-data/db-hsb-asr/HSB-P3/lexicon
COPY inputs/flists/  /uasr-data/db-hsb-asr/HSB-P3/flists/
COPY inputs/info/    /uasr-data/db-hsb-asr/HSB-P3/info/
COPY inputs/lexicon/ /uasr-data/db-hsb-asr/HSB-P3/lexicon/

# copy conversion scripts
COPY inputs/scripts/ /uasr-data/db-hsb-asr/

############################################
# Convert UASR-style project to Kaldi
############################################

# not necessary but nice to have around
RUN apt install -y mc

# prepare some folders that must exist
RUN mkdir -p /uasr-data/db-hsb-asr/HSB-P3/log/uasrfea/train/

# run the conversion
RUN cd /uasr-data/db-hsb-asr/ && touch a && export PATH=$PATH:/dLabPro/bin.release/ && export UASR_HOME=/uasr && \
python3 fea_uasr2kaldi.py HSB-P3/info/default.cfg -Puasr.flists=train,dev,test
# "dev" list is sort of informational only

############################################
# Start Kaldi training
############################################

RUN apt install -y dos2unix
RUN chmod 755 /kaldi/egs/hsb/s5/local/*.sh

# make /bin/sh symlink to bash instead of dash:
RUN echo "dash dash/sh boolean false" | debconf-set-selections
RUN DEBIAN_FRONTEND=noninteractive dpkg-reconfigure dash

RUN /bin/bash -c 'cd /kaldi/egs/hsb/s5/ && source ./path.sh && export UASR_HOME=/uasr &&  export USER=kaldiuser && \
chmod 755 ./run.sh && ./run.sh'

############################################
# Convert Kaldi results to UASR compatible format
############################################

RUN cd /uasr-data/db-hsb-asr/ && DLABPRO_HOME=/dLabPro UASR_HOME=/uasr python3 am_kaldi2uasr.py /uasr-data/db-hsb-asr/HSB-P3/model/hsb_20000_sb125p025_nfea_mono/hsb_20000_sb125p025_nfea.txt                /model_mono.hmm
RUN cd /uasr-data/db-hsb-asr/ && DLABPRO_HOME=/dLabPro UASR_HOME=/uasr python3 am_kaldi2uasr.py /uasr-data/db-hsb-asr/HSB-P3/model/hsb_500_20000_sb125p025_nfea_tri1/hsb_500_20000_sb125p025_nfea_tri1.txt   /model_tri1.hmm
RUN cd /uasr-data/db-hsb-asr/ && DLABPRO_HOME=/dLabPro UASR_HOME=/uasr python3 am_kaldi2uasr.py /uasr-data/db-hsb-asr/HSB-P3/model/hsb_1000_40000_sb125p025_nfea_tri2/hsb_1000_40000_sb125p025_nfea_tri2.txt /model_tri2.hmm


RUN mkdir /output

CMD ["/bin/bash"]

# fetch the Kaldi models
## mkdir -p output
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step3_kaldi cp -r /uasr-data/db-hsb-asr/HSB-P3/model /output

# fetch the UASR converted models
## mkdir -p output
## docker run --mount type=bind,source="$(pwd)"/output,target=/output/ -it speech_recognition_acoustic_model_training_step3_kaldi cp /model_mono.hmm /model_tri1.hmm /model_tri2.hmm /output
