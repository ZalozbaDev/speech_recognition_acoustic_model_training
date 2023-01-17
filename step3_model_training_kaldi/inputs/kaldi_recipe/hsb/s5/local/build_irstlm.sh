#!/usr/bin/env bash

# Copyright 2013   (Authors: Daniel Povey, Bagher BabaAli)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.

set -e # fail on error

srcdir=data/local/lang
dir=data/local/lm

. ./utils/parse_options.sh

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

export LC_ALL=C


mkdir -p $dir

. ./path.sh || exit 1; # for KALDI_ROOT

# Create the phone bigram LM
if [ -z $IRSTLM ] ; then
  export IRSTLM=$KALDI_ROOT/tools/irstlm/
fi
export PATH=${PATH}:$IRSTLM/bin
if ! command -v prune-lm >/dev/null 2>&1 ; then
  echo "$0: Error: the IRSTLM is not available or compiled" >&2
  echo "$0: Error: We used to install it by default, but." >&2
  echo "$0: Error: this is no longer the case." >&2
  echo "$0: Error: To install it, go to $KALDI_ROOT/tools" >&2
  echo "$0: Error: and run extras/install_irstlm.sh" >&2
  exit 1
fi

# Get a wordlist-- keep everything but silence, which should not appear in
# the LM.
awk '{print $1}' $srcdir/lexiconp.txt | grep -v -w '<unk>' > $dir/wordlist.txt

# Get training data with OOV words (w.r.t. our current vocab) replaced with  <UNK>
echo "Getting training data with OOV words replaced with <unk> (unkown word) (train_nounk.gz)"
gunzip -c $dir/cleaned.gz | awk -v w=$dir/wordlist.txt \
  'BEGIN{while((getline<w)>0) v[$1]=1;}
  {for (i=1;i<=NF;i++) if ($i in v) printf $i" ";else printf "<unk> ";print ""}'|sed 's/ $//g' \
  > $dir/train_nounk.txt

cut -d' ' -f2- $dir/train_nounk.txt | sed -e 's:^:<s> :' -e 's:$: </s>:' \
  > $dir/lm_train.text

rm -f $dir/lm_phone_*.ilm.gz

#build-lm.sh -i $dir/lm_train.text -n 1 -o $dir/lm_phone_1.ilm.gz
#compile-lm $dir/lm_phone_1.ilm.gz -t=yes /dev/stdout | grep -v unk | gzip -c > $dir/lm1.arpa.gz 

#build-lm.sh -i $dir/lm_train.text -n 2 -o $dir/lm_phone_2.ilm.gz
#compile-lm $dir/lm_phone_2.ilm.gz -t=yes /dev/stdout | grep -v unk | gzip -c > $dir/lm2.arpa.gz 

build-lm.sh -i $dir/lm_train.text -n 3 -o $dir/lm_phone_3.ilm.gz
compile-lm $dir/lm_phone_3.ilm.gz -t=yes /dev/stdout | sed -e "s/<unk>/<unk>/g" | gzip -c > $dir/lm3.arpa.gz 
#compile-lm $dir/lm_phone_3.ilm.gz -t=yes /dev/stdout | grep -v unk | gzip -c > $dir/lm3.arpa.gz 


#build-lm.sh -i $dir/lm_train.text -n 5 -o $dir/lm_phone_5.ilm.gz
#compile-lm $dir/lm_phone_5.ilm.gz -t=yes /dev/stdout | grep -v unk | gzip -c > $dir/lm5.arpa.gz 

echo "Dictionary & language model preparation succeeded"
