""" Created on Mon Jun 5 11:40:19 2023

    TEXT CORPUS TO BAS PROJECT GENERATOR
    WITH RICH (DI,TRI)-PHONE TEXT SELECTION ALGORITHM

    @author: ivan

Copyright (c) 2023 Fraunhofer IKTS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=W0105
# pylint: disable=C0301
# pylint: disable=C0201
# pylint: disable=C0206

import os
import sys

import random as rn
import re
import shutil
from datetime import datetime
import uuid
import itertools
import yaml
import numpy as np
from typing import Dict, Generator, List, Tuple

from templates import SCRIPT_BACK, SCRIPT_FRONT, CLASS_HEADER, PROJECT_XML, UASR_HEADER, DEFAULT_ITP
from utils import print_progress_bar, load_data

class Configuration():
    """
    Class for configuration parameters.

    Attributes:
        cfile
        vars
        defcfg
    """
    def __init__(self, cfile):
        """
        Initializes some attributes.

        Args:
            cfile (str):    configuration file name
        """
        self.cfile = cfile

        self.defcfg = {
            'input_txts' : ['corpus.dsb'],
            'exceptions_file' : 'exceptions.txt',
            'phoneme_inventory' : 'phonmap.txt',
            'mode' : 'sampa',  # "sampa" or "uasr" phoneme sets
            'basic_type' : 'diphones',
            'split' : 3,
            'case' : "uc",
            'offset' : 0,  # speaker id starting number
            'num_sentences' : 100,
            'no_speakers' : 1,
            'min_duration' : 3,  # seconds of speech
            'names' : ["phones", "diphones", "triphones"],
            'scoring_type' : 3,  # 1, 2 or 3; choose 2 for negative log-prob weights, #3 for sentence weights
            'user_vocab' : ["user.vocab"],
            'output_dir' : 'experiment',
            'project_name' : 'default',
            'database' : 'db-asr',
            'wclass_delimiters'   : ['{','}'],
            'subword_delimiter'   : '#',
            'hcraft_lex' : None,
            'hcraft_lex_map' : None,
            }
        self.vars = self.read_configuration()

    def read_configuration(self):
        """
        Read configuration file and update the default configurations.

        Args:
            Class instance.

        Returns:
            Nothing.

        Raises:
            Warning if no configuration file is found. Uses the default parameters.
        """
        defcfg=self.defcfg

        try:
            with open(self.cfile, 'r', encoding='utf8') as stream:
                config = yaml.safe_load(stream)
            defcfg.update(config)
        except Exception as exc:
            raise Warning('No yaml config file. Using default configuration') from exc

        return defcfg

class CorpusDataset():
    """
    Class for creation of text dataset.

    Attributes:
        cfg
        text
        graphemes
        phonemes
        vowels
        exceptions
        removed
        norm_text
        vocabulary
        phonemized
        propmpts
        ideal_stats
        selected_sentence_ids
        split_ids
        explog
    """

    def __init__(self, configfile):
        self.cfg = Configuration(configfile)
        self.text = self.read_documents()
        self.graphemes, self.phonemes, self.vowels = self.read_phonemes()
        self.exceptions = self.read_exceptions()
        self.user_vocab = self.read_vocabulary()
        self.lexicon = self.read_lexicon()
        self.removed = None
        self.norm_text = None
        self.vocabulary = None
        self.phonemized = None
        self.prompts = None
        self.ideal_stats = None
        self.selected_sentence_ids = None
        self.split_ids = None
        self.explog = None

    def write_corpus(self):
        """
        Write corpus files.
        """

        corpus_n=self.norm_text
        output_dir=self.cfg.vars['output_dir']
        # projectname=self.cfg.cfile.split('.')[0]
        projectname=self.cfg.vars['project_name']
        removed=self.removed
        vocabulary=self.vocabulary

        top = np.unique(' '.join(corpus_n).split(' '), return_counts=True)
        count_sort_ind = np.argsort(-top[1])

        freq = zip(top[0][count_sort_ind], top[1][count_sort_ind])

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)

        wrk_dir=os.path.join(os.getcwd(), output_dir, 'corpus')
        os.mkdir(wrk_dir)

        with open(os.path.join(wrk_dir, projectname.lower() + '.freq'), "w", encoding='utf-8') as freq_file:
            for word in freq:
                freq_file.write(word[0] + '\t' + str(word[1]) + '\n')
            freq_file.close()

        with open(os.path.join(wrk_dir, projectname.lower() + '.corp'), "w", encoding='utf-8') as corp_file:
            corp_file.write("\n".join(corpus_n))
            corp_file.close()

        with open(os.path.join(wrk_dir, projectname.lower() + '.rmvd'), "w", encoding='utf-8') as rmv_file:
            for rmv in removed:
                rmv_file.write(str(rmv[0]) + '\t' + rmv[1] + '\n')
            rmv_file.close()

        with open(os.path.join(wrk_dir, projectname.lower() + '.vocab'), "w", encoding='utf-8') as vocab_file:
            vocab_file.write("\n".join(vocabulary))
            vocab_file.close()

    def write_bas(self):
        """
        Write BAS Project template files files.
        """

        if self.prompts is None and self.phonemized is None:
            raise SystemError('Prompts and phonemized text are missing.')

        output_dir=self.cfg.vars['output_dir']

        if os.path.exists(output_dir):
            wrk_dir=os.path.join(os.getcwd(), output_dir)
        else:
            raise SystemError('Folder missing.')

        if os.path.exists(os.path.join(wrk_dir,'sentences')):
            shutil.rmtree(os.path.join(wrk_dir,'sentences'))
        os.mkdir(os.path.join(wrk_dir,'sentences'))

        if os.path.exists(os.path.join(wrk_dir,'transliterations')):
            shutil.rmtree(os.path.join(wrk_dir,'transliterations'))
        os.mkdir(os.path.join(wrk_dir,'transliterations'))

        if os.path.exists(os.path.join(wrk_dir,'speechrecorder')):
            shutil.rmtree(os.path.join(wrk_dir,'speechrecorder'))
        os.mkdir(os.path.join(wrk_dir,'speechrecorder'))

        def speakers(num_speakers):
            """
            Generate BAS speakers template for a given number of speakers

            Args:
                num_speakers:   Number for the speakers for the template

            Returns:
                Formated string for the given number of speakers

            Raises:
                Nothing
            """

            output = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <speakers>"""

            spk_body = """
                <speakers>
                    <personId>$PERSON$</personId>
                    <registered>$TIME$</registered>
                    <uuid>$UUID$</uuid>
                    <informedConsentInPaperFormSigned>false</informedConsentInPaperFormSigned>
                </speakers>
                """
            spk_end = """
            </speakers>
            """
            for spk in range(num_speakers):
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%dT%H:%M:%f%z")
                spk_body = spk_body.replace('$UUID$', str(uuid.uuid4()))
                spk_body = spk_body.replace('$TIME$', date_time)
                spk_body = spk_body.replace('$PERSON$', str(spk + 1))
                output = output + spk_body

            output = output + spk_end
            return output

        def partition(list_in, nset):
            """
            Partition list of sentences in n-sets
            """
            rn.shuffle(list_in)
            return [list_in[i::nset] for i in range(nset)]

        # Split the datasets
        self.split_ids = partition(list(self.selected_sentence_ids), self.cfg.vars['split'])

        # Write the BAS Project
        basic_type = self.cfg.vars['basic_type']
        scoring_type = self.cfg.vars['scoring_type']
        mode = self.cfg.vars['mode']
        # projectname = self.cfg.cfile.split('.')[0]
        projectname=self.cfg.vars['project_name']
        no_speakers = self.cfg.vars['no_speakers']
        offset = self.cfg.vars['offset']
        split = self.cfg.vars['split']
        num_sentences=self.cfg.vars['num_sentences']

        sentences=self.prompts
        utterances=self.phonemized

        for i, idx in enumerate(self.split_ids):
            out_file = 'sentsel_' + basic_type + '_' + str(scoring_type) + '_' + mode + '_' + str(i + 1) + '.txt'
            part_folder = 'speechrecorder/' + projectname + '-' + str(i + 1)

            if os.path.exists(os.path.join(wrk_dir,part_folder)):
                shutil.rmtree(os.path.join(wrk_dir,part_folder))
            os.mkdir(os.path.join(wrk_dir,part_folder))

            with open(os.path.join(wrk_dir, part_folder, projectname + '-' + str(i + 1) + '_speakers.xml'),
                      "w", encoding='utf-8') as sxml_file:
                sxml_file.write(speakers(no_speakers))
                sxml_file.close()

            with open(os.path.join(wrk_dir, part_folder, projectname + '-' + str(i + 1) + '_project.prj'),
                      "w", encoding='utf-8') as pxml_file:
                pxml_file.write(PROJECT_XML.replace('$PROJECT$', projectname + '-' + str(i + 1)))
                pxml_file.close()

            with (  open(os.path.join(wrk_dir, 'sentences', out_file), "w", encoding='utf-8') as sentsel,
                    open(os.path.join(wrk_dir, part_folder, projectname + '-' + str(i + 1) + '.prt'),
                        "w", encoding='utf-8') as basprojectfile,
                    open(os.path.join(wrk_dir, part_folder, projectname + '-' + str(i + 1) + '_script.xml'),
                        "w", encoding='utf-8') as scxml_file):

                scxml_file.write(SCRIPT_FRONT.replace('$PROJECT$', projectname + '-' + str(i + 1)))

                for k, sm_id in enumerate(idx):
                    header = projectname + '_' + str(i + 1) + '_' + str(k).zfill(3) + '\t'
                    sentsel.write(header + sentences[sm_id] + '\n')
                    sentsel.write(header + ' '.join(utterances[sm_id]) + '\n')

                    for spk in range(no_speakers):
                        drname = os.path.join(wrk_dir, 'transliterations', projectname + '-' + str(i + 1), 'RECS',
                                            str(spk + 1 + offset).zfill(4))
                        os.makedirs(drname, exist_ok=True)
                        trlfile = open(drname + '/' + str(spk + 1 + offset).zfill(4) + header[:-1] + '.trl', "w",
                                    encoding='utf-8')

                        words = list(filter(None, sentences[sm_id].split()))

                        trlfile.write('\n'.join(words) + '\n')
                        trlfile.close()

                    basprojectfile.write(header + sentences[sm_id] + '\n')
                    scxml_file.write('<recording itemcode="' + header[:-1] +
                                    '" postrecdelay="500" prerecdelay="2" recduration="25000">' +
                                    '<recprompt><mediaitem>"' + sentences[sm_id] +
                                    '"</mediaitem></recprompt></recording>' + '\n')

                basprojectfile.close()
                scxml_file.write(SCRIPT_BACK)
                scxml_file.close()
                sentsel.close()

            # Phonemic unit analysis
            utt_sel = list(np.array(utterances, dtype='object')[idx])
            sent_sel = list(np.array(sentences, dtype='object')[idx])

            wrd_cnt = len((' '.join([''.join(s) for s in sent_sel])).split(' '))
            char_cnt = len((' '.join([' '.join(u) for u in utt_sel]).split(' ')))

            sel_stats = self.get_stats(utt_sel, show_bar=False)
            whtspc = sel_stats['phones']['.']

            if len(utterances) <= num_sentences:
                num_sentences = len(utterances)
            rnd_sent = rn.sample(utterances, int(num_sentences / split))
            rnd_stats = self.get_stats(rnd_sent)

            print(f'\n\nSet Nr.: {i + 1}')
            print(f'sentences: {int(num_sentences / split)}')
            print(f'sell word count: {wrd_cnt}')
            # Fonagy, I.; K. Magdics (1960). "Speed of utterance in phrases of different length". Language and Speech. 3 (4): 179–192. doi:10.1177/002383096000300401.
            pps_min = 10  # 9.4  # reading poetry
            pps_max = 15  # 13.83  # commenting sport
            print(
                f'estimated duration by phoneme units (min): {((char_cnt - whtspc) / pps_max) / 60} - {((char_cnt - whtspc) / pps_min) / 60}')
            # http://prosodia.upf.edu/home/arxiu/publicacions/rodero/rodero_a-comparative-analysis-of-speech-rate-and-perception-in-radio-bulletins.pdf
            wpm_min = 100  # 168  # Englisch BBC
            wpm_max = 160  # 210  # Spanish RNE
            print(f'estimated duration by number of words (min): {(wrd_cnt / wpm_max)} - {(wrd_cnt / wpm_min)}')

            for b_type in self.cfg.vars['names']:
                total_tokens = list(self.ideal_stats[b_type].keys())
                sel_tokens = list(sel_stats[b_type].keys())
                rnd_tokens = list(rnd_stats[b_type].keys())
                print(f'\ntype: {b_type}')
                print(f'total tokens: {len(total_tokens)}')
                print(f'random ratio: {len(rnd_tokens) / len(total_tokens)}')
                #print(f'rand diff: {set(total_tokens).difference(set(sel_tokens))}')
                print(f'selected ratio: {len(sel_tokens) / len(total_tokens)}')
                #print(f'sell diff: {set(total_tokens).difference(set(sel_tokens))}')

        print('Done')

    def write_uasr(self):
        """
        Write UASR project configuration files
        """
        def generate_combinations(input_string):
            # Find all alternatives within parentheses
            alternatives = [a[1:-1].replace('_',' ').split('|') for a in input_string if '(' in a and ')' in a ]
            indices = [i for i, a in enumerate(input_string) if '(' in a and ')' in a ]

            if len(alternatives)==0:
                return [' '.join(input_string)]

            # Generate all combinations using itertools.product
            combinations = []
            for pattern in itertools.product(*alternatives):
                for index, value in zip(indices, pattern):
                        #if value=='*':
                        #    value=''
                    input_string[index] = value

                combinations.append(' '.join(input_string))
            return combinations

        output_dir=self.cfg.vars['output_dir']

        if os.path.exists(output_dir):
            wrk_dir=os.path.join(os.getcwd(), output_dir)
        else:
            raise SystemError('Folder missing.')

        if os.path.exists(os.path.join(wrk_dir,'uasr_configurations')):
            if os.path.exists(os.path.join(wrk_dir,'uasr_configurations','info')):
                shutil.rmtree(os.path.join(wrk_dir,'uasr_configurations','info'))
            if os.path.exists(os.path.join(wrk_dir,'uasr_configurations','lexicon')):
                shutil.rmtree(os.path.join(wrk_dir,'uasr_configurations','lexicon'))
            if os.path.exists(os.path.join(wrk_dir,'uasr_configurations','grammar')):
                shutil.rmtree(os.path.join(wrk_dir,'uasr_configurations','grammar'))
            shutil.rmtree(os.path.join(wrk_dir,'uasr_configurations'))
        os.mkdir(os.path.join(wrk_dir,'uasr_configurations'))
        os.mkdir(os.path.join(wrk_dir,'uasr_configurations','info'))
        os.mkdir(os.path.join(wrk_dir,'uasr_configurations','lexicon'))
        os.mkdir(os.path.join(wrk_dir,'uasr_configurations','grammar'))

        # projectname=self.cfg.cfile.split('.')[0]
        projectname=self.cfg.vars['project_name']
        mode=self.cfg.vars['mode']
        lexicon=self.lexicon
        expl=self.explog
        vowels=self.vowels
        database=self.cfg.vars['database']

        # Write lexicon debug file
        with open(os.path.join(wrk_dir, 'uasr_configurations', 'lexicon', projectname.lower() + '_' + mode + '.dbg'), "w",
                        encoding='utf-8') as dbg_file:
            for key in lexicon.keys():
                for pvar in lexicon[key]:
                    patt = ' '.join(expl.get(key,['EXTERNAL'])).replace('+','')
                    out = ' '.join(pvar).replace(self.cfg.vars['subword_delimiter'],'')
                    dbg_file.write(key + '\t(' + out + ')\t\t(' + patt +')\n')
            dbg_file.close()

        # Write UASR lexicon file
        with open(os.path.join(wrk_dir, 'uasr_configurations', 'lexicon', projectname.lower() + '_' + mode + '.ulex'), "w",
                        encoding='utf-8') as ulex_file:
            for key in lexicon.keys():
                for pvar in lexicon[key]:
                    pvar=''.join(pvar)
                    pvar = re.sub(r'[^\w\s\d\|\(\)]', '', pvar).replace('_','')
                    ulex_file.write(key + '\t' + '(.|#|)' + pvar + '(.|#|)' + '\n')
            ulex_file.close()

        # Write UASR grammar file
        with open(os.path.join(wrk_dir, 'uasr_configurations','grammar', projectname.lower() +'.grm'), "w",
                  encoding='utf-8') as fagrm_file:

            fagrm_file.write('LEX: ' + '<PAU>' + '\t' + '#' + '\n')
            fagrm_file.write('LEX: ' + '<PAU>' + '\t' + '.' + '\n')
            for key in lexicon.keys():
                for pvar in lexicon[key]:
                    pvar=''.join(pvar)
                    pvar = re.sub(r'[^\w\s\d\|\(\)]', '', pvar).replace('_','')
                    fagrm_file.write('LEX: ' + key + '\t' + '(.|#|)' + pvar + '(.|#|)' + '\n')

            fagrm_file.write('\n')
            fagrm_file.write('GRM: ' + '(S) <PAU>: (S)' + '\n')
            fagrm_file.write('GRM: ' + '(F) <PAU>: (F)' + '\n')
            for key in lexicon.keys():
                fagrm_file.write('GRM: ' + '(S) ' + key + ':' + key + ' (S)' + '\n')
            fagrm_file.write('GRM: ' + '(S) (F)')
            fagrm_file.close()

        # Write sampa and kaldi lexicons
        with open(os.path.join(wrk_dir, 'uasr_configurations', 'lexicon', projectname.lower() + '_' + mode + '.lex'), "w",
                        encoding='utf-8') as lex_file, open(os.path.join(wrk_dir, 'uasr_configurations', 'lexicon', projectname.lower() + '_' + mode + '.klex'), "w",
                        encoding='utf-8') as klex_file:

            lex_file.write('<unk>' + '\t' + '#' + '\n')
            klex_file.write('<unk>' + '\t' + '<usb>' + '\n')
            phmodels = set()
            for key in lexicon.keys():
                for pvar in lexicon[key]:
                    for comb in generate_combinations(pvar):
                        out = re.sub(r'[^\w\s\d]', '', comb)
                        out = re.sub(' +', ' ', out).strip()
                        if out in ('',' '):
                            print(f'No pronounciation for word: {key}')
                            continue
                        lex_file.write(key + '\t' + out + '\n')
                        klex_file.write(key + '\t. ' + out + ' .\n')
                        phmodels.update(out.split())
            klex_file.close()
            lex_file.close()

        # Write phoneme classes seen in the corpus
        with open(os.path.join(wrk_dir, 'uasr_configurations','info', 'classes.txt'), "w", encoding='utf-8') as phm_file:
            #labmap_file = open(os.path.join(os.getcwd(), 'uasr_configurations','info', 'labmap.txt'), "w", encoding='utf-8')
            phm_file.write(CLASS_HEADER)
            for clp in sorted(list(phmodels)):
                if clp in vowels:
                    ver = '1.0'
                else:
                    ver = '0.0'
                if clp in ('',' '):
                    print('Empty class')
                    continue
                phm_file.write(' '+clp+'\t'+'3'+'\t'+ver+'\t'+'[spe]\n')
                #labmap_file.write(cl+'\t'+cl)
            phm_file.close()
            #labmap_file.close()

        # Write default UASR ITP script
        with open(os.path.join(wrk_dir, 'uasr_configurations', 'info', 'default.itp'), "w", encoding='utf-8') as defitp_file:
            defitp_file.write(DEFAULT_ITP)
            defitp_file.close()

        # Write default UASR configuration file
        with open(os.path.join(wrk_dir, 'uasr_configurations','info', 'default.cfg'), "w", encoding='utf-8') as uasr_file:
            uasr_file.write(UASR_HEADER)
            uasr_file.write('uasr.db =\t' + '"' + database+'";'+'\n')
            uasr_file.write('uasr.exp =\t'  + '"' + projectname.upper()+'";'+'\n')
            uasr_file.write('uasr.customize =\t' + '"$UASR_HOME-data/' + database + '/' + projectname.upper()+'/info/default.itp";'+'\n')

            uasr_file.write('uasr.sig.srate =\t' + '16000' +';'+'\n')
            uasr_file.write('uasr.pfa =\t' + '"UPFA";'+'\n')
            uasr_file.write('uasr.flist.test =\t' + '"all.flst";'+'\n')

            uasr_file.write('uasr.from =\t' + '"T";'+'\n')
            uasr_file.write('uasr.out =\t' + '"lab";'+'\n')
            uasr_file.write('uasr.type =\t' + '"phn";'+'\n')
            uasr_file.write('uasr.lm =\t' + '"fsg";'+'\n')
            uasr_file.write('uasr.dir.sig =\t' + '"$UASR_HOME-data/' + database + '/common/sig";'+'\n')
            uasr_file.write('uasr.dir.lab =\t' + '"$UASR_HOME-data/' + database + '/common/lab";'+'\n')
            uasr_file.write('uasr.am.classes =\t' + '"$UASR_HOME-data/' + database + '/' + projectname.upper() + '/info/classes.txt";'+'\n')
            #uasr_file.write('uasr.lab.map =\t' + '"$UASR_HOME-data/' + database + '/' + projectname.upper() + '/info/labmap.txt";'+'\n')
            uasr_file.write('uasr.lm.fsg =\t' + '"$UASR_HOME-data/' + database + '/' + projectname.upper() + '/grammar/' + projectname.lower() +'.grm";'+'\n')
            uasr_file.write('uasr.lx =\t' + '"$UASR_HOME-data/' + database + '/' + projectname.upper() + '/lexicon/' + projectname.lower() + '_' + mode + '.ulex";' + '\n')
            uasr_file.write('uasr.dir.out =\t' + '"$UASR_HOME-data/' + database + '/common/lab";'+'\n')
            uasr_file.write('uasr.dir.trl =\t' + '"$UASR_HOME-data/' + database + '/common/trl";'+'\n')
            uasr_file.write('uasr.lab.ext =\t' + '"lab";'+'\n')
            uasr_file.write('uasr.trl.ext =\t' + '"trl";'+'\n')
            uasr_file.write('uasr.am.model =\t' + '"' + projectname + '";'+'\n')
            uasr_file.write('uasr.am.sig =\t' + '0;'+'\n')
            uasr_file.write('uasr.am.gbg =\t' + '1;'+'\n')
            uasr_file.write('\n'+'## EOF'+'\n')
            uasr_file.close()

    def read_documents(self):
        """
        Corpus processing
        """
        return load_data(self.cfg.vars['input_txts'])

    def read_exceptions(self):
        """
        Read pronounciation exception files.
        """
        exceptions = {}
        if self.cfg.vars['exceptions_file'] is not None:
            try:
                with open(os.path.join(os.getcwd(), self.cfg.vars['exceptions_file']), 'r', encoding='utf8') as expfile:
                    for line in expfile:
                        part = line.strip().split('\t')
                        if len(part) >= 2 and part[0][0]!=';':
                            if part[0][0]=='_':
                                if exceptions.get('#V'+part[0]) is None:
                                    exceptions['#V'+part[0]] = [[part[1],part[2]]]
                                else:
                                    exceptions['#V'+part[0]].append([part[1],part[2]])
                                if exceptions.get('#C'+part[0]) is None:
                                    exceptions['#C'+part[0]] = [[part[1],part[2]]]
                                else:
                                    exceptions['#C'+part[0]].append([part[1],part[2]])
                                if exceptions.get('$'+part[0]) is None:
                                    exceptions['$'+part[0]] = [[part[1],part[2]]]
                                else:
                                    exceptions['$'+part[0]].append([part[1],part[2]])

                            elif part[0][-1]=='_':
                                if exceptions.get(part[0]+'#V') is None:
                                    exceptions[part[0]+'#V'] = [[part[1],part[2]]]
                                else:
                                    exceptions[part[0]+'#V'].append([part[1],part[2]])
                                if exceptions.get(part[0]+'#C') is None:
                                    exceptions[part[0]+'#C'] = [[part[1],part[2]]]
                                else:
                                    exceptions[part[0]+'#C'].append([part[1],part[2]])
                                if exceptions.get(part[0]+'$') is None:
                                    exceptions[part[0]+'$'] = [[part[1],part[2]]]
                                else:
                                    exceptions[part[0]+'$'].append([part[1],part[2]])
                            else:
                                if exceptions.get(part[0]) is None:
                                    exceptions[part[0]] = [[part[1],part[2]]]
                                else:
                                    exceptions[part[0]].append([part[1],part[2]])
            except FileNotFoundError:
                print('Error opening file:', self.cfg.vars['exceptions_file'])
        return exceptions

    def read_phonemes(self):
        """
        Load Phoneme Inventory
        """
        phoneme_maps = {}
        graphemes = []
        if self.cfg.vars['phoneme_inventory'] is not None:
            try:
                with open(os.path.join(os.getcwd(), self.cfg.vars['phoneme_inventory']), 'r', encoding='utf8') as invfile:
                    for line in invfile:
                        part = line.strip().split('\t')
                        phoneme_maps[part[0]] = (part[1], part[2])
                        graphemes.append(part[0])
            except FileNotFoundError:
                print('Error opening file:', self.cfg.vars['phoneme_inventory'])
            vowels = [mapps[0] for mapps in phoneme_maps.values() if mapps[1] == 'V']

        if self.cfg.vars['wclass_delimiters'] is not None:
            for wdlm in self.cfg.vars['wclass_delimiters']:
                graphemes.extend([wdlm])
                phoneme_maps[wdlm] = (wdlm, 'S')

        if len(self.cfg.vars['subword_delimiter'])==1:
            sdlm = self.cfg.vars['subword_delimiter']
            graphemes.extend(sdlm)
            phoneme_maps[sdlm] = (sdlm, 'S')
        return graphemes, phoneme_maps, vowels

    def read_vocabulary(self):
        """
        Create user defined vocabulary of allowed words.

            TODO: Refactor the name.
        """

        user_vocab=[]
        if self.cfg.vars['user_vocab']  is not None:
            user_vocab = load_data(self.cfg.vars['user_vocab'])

        return user_vocab

    def read_lexicon(self):
        """
        Load the lexicon:
        - Load each lexicon file one after another
        - Replace lexicon entries if there are duplicats
        return: Dict of words with list of list of phonems

        """

        flex_map = {}

        if self.cfg.vars.get('hcraft_lex_map') is not None:

            flex_map = self.cfg.vars['hcraft_lex_map']
            fminv = {p[1] for p in flex_map.items()}

            pinv = {p[1][0] for p in self.phonemes.items()}

            if not fminv.issubset(pinv):
                raise SystemError('Handcrafted lexicon phoneme mappings not matching phoneme inventory.')

        def extlexmap(prons):
            for flm in flex_map:
                prons=prons.replace(flm,flex_map[flm])
            return prons

        lex={}
        #ulex={}
        flex = self.cfg.vars['hcraft_lex']


        if flex is None:
            return lex

        diphns={'_'.join([*x]):x for x, _ in dict.values(self.phonemes) if len(x)==2}

        for fnamel in flex:
            with open(fnamel,'r',encoding='utf8') as fnl:
                lext = os.path.splitext(fnamel)[-1]
                if lext =='.grm':
                    print('UASR Lexicon Format')
                    for line in fnl.readlines():
                        if line=='\n' or line.strip()[0]=='#': continue
                        w, phnseqs = line.replace('LEX:','').replace('(.|#|)','').strip().split('\t')
                        if w is None and phnseqs is None:
                            continue
                        upron='_'.join([*phnseqs])
                        for dgr in diphns:
                            upron=upron.replace(dgr, diphns[dgr])

                        upron = extlexmap(upron).strip().split('_')

                        if upron not in lex.get(w, []):
                            lex.setdefault(w, []).append(upron)
                        #if lex.get(w) is None:
                        #    lex[w]=[]
                            #ulex[w]=[]
                        #lex[w]+=[upron]
                        #ulex[w]+=[upron]
                else:
                    for w, phnseqs in map(lambda l:l.strip().split('\t'),fnl.readlines()):
                        phnseqs = extlexmap(phnseqs)
                        if phnseqs not in lex.get(w, []):
                                lex.setdefault(w, []).append(phnseqs.split(' '))
                        #if lex.get(w) is None:
                        #    lex[w]=[]
                        #lex[w]+=map(lambda p:tuple(p.split(' ')),phnseqs)
                        #ulex[w]+=map(lambda p:tuple(p.split(' ')),phnseqs)

        return lex#,ulex

    def normalize_text(self):
        """
        Normalize text, remove sentences containing
        non-inventory characters or shorter than
        the minimal phoneme count
        """
        crpus = self.text
        inventory=self.graphemes

        if len(self.user_vocab)==0:
            uvoc = None
        else:
            uvoc = self.user_vocab
        case = self.cfg.vars['case']
        digraphs = self.cfg.vars['digraphs']
        min_phm_len = self.cfg.vars['min_duration'] * 10

        txt = []
        rmv = []
        inv = set(inventory)
        if uvoc is not None:
            if case == 'uc':
                uvoc = list(map(lambda x: x.upper(), uvoc))
            if case == 'lc':
                uvoc = list(map(lambda x: x.lower(), uvoc))
            # Converting it into list
            uvoc = set(list(uvoc))

        clen = len(crpus)
        cnt=0
        print_progress_bar(0, clen, prefix='Normalize Corpus:', suffix='Complete', length=50)

        for line in crpus:
            tline = re.sub(r'[^\w\s\d{}\#]', '', line)
            if len(tline)==0:
                continue
            if set(tline)==set(['#']):
                print(line)
                continue
            tlist=[]
            for token in tline.split():
                if self.cfg.vars['wclass_delimiters'][0] in token and self.cfg.vars['wclass_delimiters'][1] in token:
                    continue
                else:
                    if case == "uc":
                        #re.sub(r"\b(?<!{)(\w+)(?!})\b", lambda match: match.group(1).upper(), tline)
                        token = token.upper()
                    elif case == "lc":
                        #re.sub(r"\b(?<!{)(\w+)(?!})\b", lambda match: match.group(1).lower(), tline)
                        token = token.lower()

                tlist.append(token)

            tline = ' '.join(tlist).strip()

            if uvoc is not None:
                lwrds = set(tline.split())
                if not lwrds.issubset(uvoc):
                    cnt+=1
                    print_progress_bar(cnt+1, clen, prefix='Normalize Corpus:', suffix='Complete', length=50)
                    continue

            grphs = '_'.join(tline.upper())
            for dgr in digraphs:
                grphs = grphs.replace(dgr, digraphs[dgr])

            grphs = grphs.strip().split('_')

            if inventory:
                linv = set(grphs)
                linv.discard(' ')
                linv.discard('')
                if linv.issubset(inv) and len(linv) > min_phm_len:
                    txt.append(tline)
                else:
                    rmv.append((linv.difference(inv), tline))
            else:
                txt.append(tline)
            cnt+=1
            print_progress_bar(cnt+1, clen, prefix='Normalize Corpus:', suffix='Complete', length=50)
        print('\nCorpus normalization completed.')

        self.norm_text = list(dict.fromkeys(txt))
        self.removed = rmv

    def get_vocabulary(self):
        """
        Extract vocabulary from the normalized corpus
        """
        text = ' '.join(self.norm_text)
        self.vocabulary = sorted(list(set(text.split())))

    def get_stats(self, punts: Dict = None, show_bar = False) -> Dict:
        """
        get_stats _summary_

        Args:
            punts (Dict, optional): _description_. Defaults to None.
            show_bar (bool, optional): _description_. Defaults to False.

        Returns:
            Dict: _description_
        """
        stats = {}
        phones = {}
        diphones = {}
        triphones = {}

        counter = 0
        plen = len(punts)
        # Initial call to print 0% progress
        if show_bar:
            print_progress_bar(0, plen, prefix='Get  Statistics:', suffix='Complete', length=50)

        for phonelist in punts:
            #phonelist = ln
            for phon in phonelist:
                if phones.get(phon) is not None:
                    phones[phon] += 1
                else:
                    phones[phon] = 1

                # extract diphones from phones
            for i in range(len(phonelist) - 1):
                dip = f'{phonelist[i]}_{phonelist[i + 1]}'
                if diphones.get(dip) is not None:
                    diphones[dip] += 1
                else:
                    diphones[dip] = 1

            for i in range(len(phonelist) - 2):
                tri = f'{phonelist[i]}^{phonelist[i + 1]}+{phonelist[i + 2]}'
                if triphones.get(dip) is not None:
                    triphones[tri] += 1
                else:
                    triphones[tri] = 1

            if show_bar:
                counter += 1
                print_progress_bar(counter + 1, plen, prefix='Get  Statistics:', suffix='Complete', length=50)

        stats['phones'] = phones
        stats['diphones'] = diphones
        stats['triphones'] = triphones

        return stats

    def create_lexicon(self):
        """
        Make lexicon from vocabulary
        """
        def _addq(lex):
            """
            Add the phnoeme 'Q' to all words in the lexicon starting with a vowel
            lex: Lexicon with uasr phonems
            return: Modified lexicon
            """
            entry={}
            for word, prons in lex.items():
                if len(prons[0])!=0:
                    entry[word]=prons+[['Q']+p for p in prons if p[0] in self.vowels and word[0] not in self.cfg.vars['subword_delimiter'] ]
            return entry

        def _check_exceptions(rules):
            """
            Check if there are exceptions for a given phoneme context
            """

            excps = []
            excpr = []
            for excp in self.exceptions:
                for rule in rules:
                    if excp in rule:
                        excps.extend([self.exceptions[excp]])
                        excpr.extend([excp])
                        return excps, excpr
            #return list(dict.fromkeys(excps)), list(dict.fromkeys(excpr))
            return excps, excpr

        def _phonemize(word, phmap):
            """
            G2P for a given word and phoneme map
            """

            canonical = []
            alternatives= []
            pattern = []

            if self.cfg.vars['wclass_delimiters'][0] in word and self.cfg.vars['wclass_delimiters'][1] in word:
                return [word,word], ''

            if phmap is not None:
                excpc = 0
                graphs = '_'.join(list('$' + word.strip() + '$'))
                for dgr in self.cfg.vars['digraphs']:
                    graphs = graphs.replace(dgr, self.cfg.vars['digraphs'][dgr])
                graphs = graphs.split('_')

                graphs = [g for g in graphs if g != '']

                for grp in range(len(graphs) - 2):
                    left = graphs[grp]
                    grapheme = graphs[grp + 1]
                    if grapheme in self.cfg.vars['subword_delimiter'] or grapheme in self.cfg.vars['wclass_delimiters']:
                        continue
                    right = graphs[grp + 2]
                    rule1 = left + '_' + grapheme + '_' + right
                    rule2 = ('#' + phmap[left][1] if left != '$' else '$') + '_' + grapheme + '_' + right
                    rule3 = left + '_' + grapheme + '_' + ('#' + phmap[right][1] if right != '$' else '$')
                    rule4 = ('#' + phmap[left][1] if left != '$' else '$') + '_' + \
                            grapheme + '_' + ('#' + phmap[right][1] if right != '$' else '$')
                    lrules = list(set([rule1, rule2, rule3, rule4]))
                    excp, excpr = _check_exceptions(lrules)
                    excpc = excpc + len(excp)


                    # in case of multiple exception rules, takse always the first (mandatory) in the order of apearance
                    if len(excp) > 1:
                        print(word, grapheme, excp)
                        excp = [excp[0]]

                    phn = []

                    #canonical.extend(phmap[grapheme][0].split(' '))
                    if len(excp) > 0:
                        #if excp[0][0] != '*':
                        phn = excp[0][0][0].split(' ')
                        rtype = excp[0][0][1][0]
                        rule = ''.join(excpr)
                        if rtype == 'M':
                            canonical.extend(phn)
                            #alternatives.extend(phmap[grapheme][0].split(' '))
                            alternatives.extend(phn)
                            pattern.extend(['M[ ' + rule + ' ]'])
                        elif rtype == 'A':
                            canonical.extend(phmap[grapheme][0].split(' '))
                            alternatives.extend(phn)
                            pattern.extend(['A[ ' + rule + ' ]'])
                        else:
                            canonical.extend(phmap[grapheme][0].split(' '))
                            alternatives.extend(phmap[grapheme][0].split(' '))
                            pattern.extend(['?[ ' + rule + ' ]'])
                        if phmap[grapheme][1] == 'V' and '*' not in phn:
                            self.vowels.extend(phn)
                    else:
                        canonical.extend(phmap[grapheme][0].split(' '))
                        alternatives.extend(phmap[grapheme][0].split(' '))
                        pattern.extend(['','C'])

                can = canonical
                if sorted(canonical)!=sorted(alternatives):
                    alt = alternatives
                    return [can, alt], pattern
                return [can,], pattern
            else:
                return word.strip(), ''

        def remove_successive_duplicates(lst):
            result = []
            for v in lst:
                newv = []
                for i, value in enumerate(v):
                    if i == 0 or value != v[i - 1]:
                        newv.extend([value])
                result.append(newv)
            return result

        vocab=self.vocabulary
        phoneme_maps=self.phonemes

        lex = {}
        expl= {}
        #ulex = self.uasr_lexicon
        lvoc = len(vocab)+len(self.lexicon)
        cnt=len(self.lexicon)
        print_progress_bar(cnt+1, lvoc, prefix='Create Lexicon:', suffix='Complete', length=50)

        for vcb in vocab:
            if self.lexicon.get(vcb) is None:
                pron, patt = _phonemize(vcb, phoneme_maps)
                if pron!='':
                    lex[vcb] = remove_successive_duplicates(pron)
                    expl[vcb] = patt
            cnt+=1
            print_progress_bar(cnt+1, lvoc, prefix='Create Lexicon:', suffix='Complete', length=50)

        self.vowels = list(set(self.vowels))

        lex = _addq(lex)

        print('Lexicon completed.')
        self.lexicon = {**self.lexicon, **lex}
        self.explog = expl

    def create_prompts(self):
        """
        Generate phoneme sequences from sentences
        """

        if self.norm_text is None or self.lexicon is None:
            raise SystemError('Missing normalized text and the lexicon')

        sent=self.norm_text
        lex=self.lexicon

        pronunciation = []
        sents = []
        lexset = set(lex.keys())
        sdel=self.cfg.vars['subword_delimiter']

        for snt in sent:
            prn = []
            words = snt.strip().split(' ')
            words = list(filter(None, words))
            if not set(words).issubset(lexset) and bool(lex):
                continue
            prn.extend('.')

            for wrd in words:
                if not lex.get(wrd):
                    raise SystemError('Word not in lexicon')
                phn = lex[wrd][0]

                prn.extend(phn)
                if wrd[-1]!=sdel:
                    prn.extend('.')

            pronunciation.append(prn)
            sents.append(snt.replace(sdel+' '+sdel,''))
        self.phonemized=pronunciation
        self.prompts=sents

    def sentence_select(self):
        """
        Make lists for different scoring methods
        """

        def scorelists(stat, name):
            """
            Create scoring lists.
            """
            tokens = list(stat[name].keys())
            # Score 1: each type should be present at least once
            score1 = np.full(np.array(list(stat[name].values())).shape[0], 1)

            # Score 2: each base type according the negative probability logs
            score2 = np.array(list(stat[name].values()))
            score2 = -np.log(score2 / np.sum(score2))

            return tokens, list(score1), list(score2), list(score2)

        def score_sentence(sentence, scorestats):
            """
            Score sentence according to the statistics.
            """

            scoring_type=self.cfg.vars['scoring_type']

            if scoring_type in (1,2): #== 1 or scoring_type == 2:
                score = np.dot(sentence, scorestats)
            elif scoring_type == 3:
                # According to Berry & Fadiga "Data-driven Design of a Sentence List for an Articulatory Speech Corpus"
                tkns = np.sum(sentence)  # number of tokens (phonemes, di-tri phones)
                if tkns != 0:
                    unqt = np.count_nonzero(np.array(sentence))  # unique tokens
                    binsent = sentence
                    binsent[np.nonzero(sentence)] = 1
                    score = 1 / tkns * np.dot(binsent, scorestats) * (unqt / tkns)
                else:
                    score = 0
            else:
                raise SystemExit('Wrong scoring type.')

            return score

        def token_counts(corp, token_type, token_ids, score):
            """
            Count the used tokens by type
            """

            scr = []
            i = 0
            lcrp = len(corp)
            # Initial call to print 0% progress
            print_progress_bar(0, lcrp, prefix='Score Sentences:', suffix='Complete', length=50)

            for phonlist in corp:
                if token_type == "phones":
                    tokens = phonlist
                elif token_type == "diphones":
                    tokens = [f'{phonlist[i]}_{phonlist[i + 1]}' for i in range(len(phonlist) - 1)]
                elif token_type == "triphones":
                    tokens = [f'{phonlist[i]}^{phonlist[i + 1]}+{phonlist[i + 2]}' for i in
                            range(len(phonlist) - 2)]
                else:
                    raise SystemExit('Token type not defined')

                dataset = np.zeros(len(token_ids))
                for token in tokens:
                    idx = np.where(np.array(token_ids) == np.array(token))
                    try:
                        dataset[idx] += 1
                    except Exception as exc:
                        dataset[idx] = 1
                        raise UserWarning('') from exc
                scr.append(score_sentence(dataset, score))
                i += 1
                print_progress_bar(i + 1, lcrp, prefix='Score Sentences:', suffix='Complete', length=50)

            return scr

        def sent_selection(stats, score_type=1):
            """
            Sentence selection according the scoring methodology
            """
            if 1 > score_type > 3:
                raise SystemExit("Wrong scoring type")

            scores = scorelists(stats, self.cfg.vars['basic_type'])
            dataset = token_counts(self.phonemized, self.cfg.vars['basic_type'], scores[0], scores[score_type])

            print('Scoring Done')

            return np.argsort(dataset)[-self.cfg.vars['num_sentences']:]

        if self.phonemized is None:
            raise SystemError('Phonemized text is missing.')

        self.ideal_stats = self.get_stats(self.phonemized,True)

        """ Sentence selection  """
        self.selected_sentence_ids = sent_selection(self.ideal_stats, self.cfg.vars['scoring_type'])

""" Main loop """
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} config')
        raise SystemExit()

    """
        *   config       - YAML config file;
    """

    corpus = CorpusDataset(sys.argv[1])
    corpus.normalize_text()
    corpus.get_vocabulary()
    corpus.create_lexicon()
    corpus.write_corpus()
    corpus.write_uasr()

    if corpus.cfg.vars['basic_type'] is not None:
        corpus.create_prompts()
        corpus.sentence_select()
        corpus.write_bas()

    sys.exit(0)
