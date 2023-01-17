#!/bin/bash

# This script is adapted from swbd Kaldi run.sh (https://github.com/kaldi-asr/kaldi/blob/master/egs/swbd/s5c/run.sh) and the older s5 (r1) version of this script

# Copyright 2018 Kaldi developers (see: https://github.com/kaldi-asr/kaldi/blob/master/COPYING)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Set bash to 'debug' mode, it prints the commands (option '-x') and exits on :
# -e 'error', -u 'undefined variable', -o pipefail 'error in pipeline',
set -euxo pipefail

# Starting point, when later is necessary to continue the training

stage=-1
[ "$#" -ge 1 ] && stage="$1"


OOV=100         # Randomly selected words from the vocabulary that will be treated as OOVs, for the <unk> usb lex entry 
experiment=hsb  # Code of the experiment
gauss=20000     # Monophone model number of gussians     
sboost=1.25     # Silence boost
power=0.25      # Power parameter for mono train stage

states1=500     # Triphone 1 number of states
senones1=20000  # Triphone 1 number of senones

states2=1000    # Triphone 2 number of states
senones2=40000  # Triphone 2 number of senones


version=sb125p025_nfea

mfccdir=mfcc

## Important directories, to be modified accordingly
work_dir=$UASR_HOME-data/db-hsb-asr/             # Folder of the UASR HSB project
data_dir=${work_dir}/HSB-P3/log/kaldifea         # Kaldi generated features
sig_dir=$UASR_HOME-data/db-hsb-asr/common/sig/   # Original signal folder

lm_ref=$UASR_HOME-data/db-hsb-asr/HSB-P3/lm      # Folder for the pretrained language models
am_ref=$UASR_HOME-data/db-hsb-asr/HSB-P3/model   # Model directory for export
lx_ref=$UASR_HOME-data/db-hsb-asr/HSB-P3/lexicon # Lexicon folder
lx_model=hsb.lex

# Working folders, DO NOT CHANGE!
exp_name=$(dirname $(realpath $0) | tr '/' '\n' | tail -n2 | tr '\n' '_' | sed -e 's/_*$//')
temp_dir=$HOME/temp/kaldi_data/${USER}_${exp_name}

dict_dir=data/local/dict_nosp
local_lang_dir=data/local/lang_nosp
lang_dir=data/lang_nosp
format_lang_out_dir=${lang_dir}_test

for dn in exp data; do
  if [ ! -L ${dn} ]; then
    mkdir -p ${temp_dir}/${dn}
    ln -s ${temp_dir}/${dn} ${dn}
  fi
done


# Clean up the data from prevous runs
if [ $stage -eq -1 ]; then
  echo "Clean up the data from prevous runs..."
    cd exp 	
    rm -rf *
    cd ..
    rm -rf ./data/*
    rm -rf ./mfcc/*
  echo "Done!"  
fi

lm_dir=data/local/lm
arpa_lm=${lm_dir}/lm3.arpa.gz

# Setting the KALDI environment

[ ! -L "steps" ] && ln -s $KALDI_ROOT/egs/wsj/s5/steps
[ ! -L "utils" ] && ln -s $KALDI_ROOT/egs/wsj/s5/utils
[ ! -L "rnnlm" ] && ln -s $KALDI_ROOT/scripts/rnnlm/

. utils/parse_options.sh

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi


if [ -f $KALDI_ROOT/tools/env.sh ]; then
      source $KALDI_ROOT/tools/env.sh; else
         echo "missing $KALDI_ROOT/tools/env.sh"; exit 1;
fi

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

# Now start preprocessing with KALDI scripts

# Path also sets LC_ALL=C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs. It should be set here, after the python scripts and not at the beginning of this script
if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

echo "Runtime configuration is: nJobs $nJobs, nDecodeJobs $nDecodeJobs. If this is not what you want, edit cmd.sh!"

# Make sure that LC_ALL is C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs
# We set it here, because the Python data preparation scripts need a propoer utf local in LC_ALL
export LC_ALL=C
export LANG=C
export LANGUAGE=C

### READ corpus from HSB flists ####
if [ $stage -le 0 ]; then

  echo "Prepare the data folders and copy the features and config files from the UASR project..."

	if [ ! -d data/wav/ ]; then
      cd data
      ln -s ${sig_dir} wav
      cd ..
  fi

  train=train
  test=test
  dev=dev
	
  rm -rf data/dev/*
	rm -rf data/test/*
	rm -rf data/train/*

  mkdir -p data/{dev,test,train}
  cp ${data_dir}/${dev}/{utt2spk,wav.scp,text,features_sfa.scp,features_sfa.ark} data/dev/
  cp ${data_dir}/${test}/{utt2spk,wav.scp,text,features_sfa.scp,features_sfa.ark} data/test/
  cp ${data_dir}/${train}/{utt2spk,wav.scp,text,features_sfa.scp,features_sfa.ark} data/train/

  utils/fix_data_dir.sh data/dev 
  utils/fix_data_dir.sh data/test 
  utils/fix_data_dir.sh data/train

  utils/utt2spk_to_spk2utt.pl data/dev/utt2spk > data/dev/spk2utt
  utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt
  utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt


  local/get_utt2dur.sh data/dev
  local/get_utt2dur.sh data/test
  local/get_utt2dur.sh data/train

  echo "Done!"
fi


### Overtake HSB lexicon ###
if [ $stage -le 1 ]; then
  
  echo "If not present, overtake the HSB lexicon from the UASR project folder..."
  
  if [ ! -d data/lexicon/ ]
    then
      mkdir data/lexicon
      number=$OOV	# number of unk from the lex
      cp ${lx_ref}/${lx_model} data/lexicon/hsb.lex 
      cat data/lexicon/hsb.lex | sort -u > data/lexicon/temp.lex
      line_count="$(wc -l < data/lexicon/temp.lex)"
      keep="$((line_count-number))"
      shuf -n $keep data/lexicon/temp.lex > data/lexicon/hsb.lex
      echo -e '<unk>\tusb' >> data/lexicon/hsb.lex
    fi
  
  echo "Done!"
fi

if [ $stage -le 2 ]; then
  echo "Prepare the dictionary cofniguration from the lexicon..."
  
  local/prepare_dict.sh data/lexicon/hsb.lex

  echo "Done!"
fi


if [ $stage -le 3 ]; then
  echo "Preparing the ${lang_dir} directory..."

  # Prepare phoneme data for Kaldi
  utils/prepare_lang.sh  --sil-prob 0.0 --num-sil-states 3 --position-dependent-phones false --share-silence-phones false ${dict_dir} "<unk>" ${local_lang_dir} ${lang_dir}

  echo "Done!"
fi

#Could be pfa or sfa
fea=features_sfa

if [ $stage -le 5 ]; then

  echo "Use pre-computed UASR features..."

  # Check and use precomputed features.
  for x in train dev test; do
	  cp data/$x/$fea.scp data/$x/feats.scp
    utils/fix_data_dir.sh data/$x
    steps/compute_cmvn_stats.sh --fake data/$x exp/make_mfcc/$x $mfccdir
  done
  
  echo "Done!"
fi

# check data/train/feats.scp available

if [ -f data/train/feats.scp ]; then
  echo "data/train/feats.scp is available, continuing with AM training."
else
  echo "data/train/feats.scp is not available, something went wrong in feature generation. Not continuing with AM training."
  exit -1
fi

#exit 0

### Monophone Training

if [ $stage -le 6 ]; then

  echo "Start training monophone model..."
   
  local/train_mono.sh --delta-opts "--delta-order=0" --cmvn-opts "--norm-means=false --norm-vars=false" --nj $nJobs --cmd "$train_cmd" \
                      data/train ${lang_dir} exp/mono ${gauss} ${sboost} ${power}

  
 	if [ ! -d ${am_ref}/${experiment}_${gauss}_${version}_mono ] 
 	then
   		mkdir ${am_ref}/${experiment}_${gauss}_${version}_mono
 	fi
  
  # Store the mono model in the UASR Project folder 
 	gmm-copy --binary=false exp/mono/final.mdl ${am_ref}/${experiment}_${gauss}_${version}_mono/hsb_${gauss}_${version}.txt 
 	cp exp/mono/phones.txt ${am_ref}/${experiment}_${gauss}_${version}_mono/phones.txt 
	copy-tree --binary=false exp/mono/tree ${am_ref}/${experiment}_${gauss}_${version}_mono/tree.txt

  echo "Done!"
fi


if [ $stage -le 7 ]; then

  echo "Create LM for evaluation..."

  mkdir -p ${lm_dir}/
  
  # Compile textual corpus for the LM model
  cat data/dev/text data/test/text data/train/text > ${lm_dir}/complete_text

  # Prepare ARPA LM

  if [ ! -f ${lm_dir}/cleaned.gz ]
  then
    dos2unix ${lm_dir}/complete_text
    gzip -k ${lm_dir}/complete_text	      
    mv ${lm_dir}/*.gz ${lm_dir}/cleaned.gz
  fi

  # If you wont to build your own from the text seen in train,dev,test data:
  local/build_irstlm.sh --srcdir ${local_lang_dir} --dir ${lm_dir}
  
  # OR
  
  # Overtake a pretrained LM from the referent folder

    #cp ${lm_ref}/lm3.arpa.gz ${lm_dir}/lm3.arpa.gz
    #cat ${lm_ref}/${lm_model} | gzip -c > ${lm_dir}/lm3.arpa.gz

  # Transform LM into Kaldi LM format 
  local/format_data.sh --arpa_lm $arpa_lm --lang_in_dir $lang_dir --lang_out_dir $format_lang_out_dir

  echo "Done!"
fi


if [ $stage -le 8 ]; then
  
  echo "Evaluate the Mono model..."

   ## Starting evaluation of the Mono model

   graph_dir=exp/mono/graph_nosp
    
   $train_cmd $graph_dir/mkgraph.log \
               utils/mkgraph.sh ${lang_dir}_test exp/mono $graph_dir
    
  for dset in dev test; do
    steps/decode_si.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
         $graph_dir data/${dset} exp/mono/decode_${dset}_nosp
	
    # Store the results in the UASR project folder  
		mkdir -p ${am_ref}/${experiment}_${gauss}_${version}_mono//${dset}
	  cp exp/mono/decode_${dset}_nosp/scoring_kaldi/wer_details/* ${am_ref}/${experiment}_${gauss}_${version}_mono/${dset}
  done

  echo "Done!"
fi

if [ $stage -le 9 ]; then

  echo "Train and evaulate Triphone 1 model..."
  
  # Alignment
  steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
                    data/train ${lang_dir} exp/mono exp/mono_ali

  steps/train_deltas.sh --cmd "$train_cmd" --delta-opts "--delta-order=0" --cmvn-opts "--norm-means=false" \
                        ${states1} ${senones1} data/train ${lang_dir} exp/mono_ali exp/tri1

  # Construct decoding graph
  graph_dir=exp/tri1/graph_nosp
    
  $train_cmd $graph_dir/mkgraph.log \
           utils/mkgraph.sh ${lang_dir}_test exp/tri1 $graph_dir

  # Evaluate dev and test  
  for dset in dev test; do
      steps/decode_si.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
            $graph_dir data/${dset} exp/tri1/decode_${dset}_nosp
  done

  mkdir -p ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/test
  mkdir -p ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/dev

  # Store the TRI1 model in the UASR project folder  
  gmm-copy --binary=false exp/tri1/final.mdl ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/hsb_${states1}_${senones1}_${version}_tri1.txt 
  cp exp/tri1/phones.txt ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/phones.txt 
  copy-tree --binary=false exp/tri1/tree       ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/tree.txt
  
  # Store the results in the UASR project folder  
  cp exp/tri1/decode_test_nosp/scoring_kaldi/wer_details/* ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/test  
  cp exp/tri1/decode_dev_nosp/scoring_kaldi/wer_details/* ${am_ref}/${experiment}_${states1}_${senones1}_${version}_tri1/dev

  echo "Done!"    
fi


if [ $stage -le 10 ]; then

  echo "Train and evaulate Triphone 2 model..."

  # Alignment
  steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
        data/train ${lang_dir} exp/tri1 exp/tri1_ali

  steps/train_deltas.sh --cmd "$train_cmd" --delta-opts "--delta-order=0" --cmvn-opts "--norm-means=false" \
        ${states2} ${senones2} data/train ${lang_dir} exp/tri1_ali exp/tri2

  # Construct decoding graph 
  graph_dir=exp/tri2/graph_nosp
  
  $train_cmd $graph_dir/mkgraph.log \
        utils/mkgraph.sh ${lang_dir}_test exp/tri2 $graph_dir

  # Evaluate dev and test 
  for dset in dev test; do
    steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" --config conf/decode.config \
        $graph_dir data/${dset} exp/tri2/decode_${dset}_nosp
  done

  mkdir -p ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/test
  mkdir -p ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/dev

  # Store the TRI2 model in the UASR project folder 
  gmm-copy --binary=false exp/tri2/final.mdl ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/hsb_${states2}_${senones2}_${version}_tri2.txt 
  cp exp/tri2/phones.txt ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/phones.txt 
  copy-tree --binary=false exp/tri2/tree       ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/tree.txt
  
  # Store the results in the UASR project folder  
  cp exp/tri2/decode_test_nosp/scoring_kaldi/wer_details/* ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/test
  cp exp/tri2/decode_dev_nosp/scoring_kaldi/wer_details/* ${am_ref}/${experiment}_${states2}_${senones2}_${version}_tri2/dev
  echo "Done!" 
fi

echo "Done..." 
exit 0
