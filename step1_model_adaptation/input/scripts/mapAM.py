#!/usr/bin/python3

import os
import sys
import numpy as np

sys.path.append(os.environ['UASR_HOME'] + '-py')
import dlabpro as dlp

## Config
# Input
fni = '3_20.hmm'


def read_classes(classfn):
    cls = list()

    try:
        with open(classfn, 'r') as classfile:
            for line in classfile:
                p = line.split('\t')[0].strip()
                if p != '':
                    if p[0:2] != '##': cls.append(p)
    except:
        raise SystemError('Error parsing class definiton file.')

    return cls


def getcidx(dat, name):
    i = dat.FindComp(name)
    if i < 0: raise ValueError(f'Component {name} not found')
    return i


def getcomp(dat, i):
    if isinstance(i, str): i = getcidx(dat, i)
    d = dlp.PData()
    d.Select(dat, i, 1)
    return d.tonumpy()


def storecomp(dat, i, arr):
    if isinstance(i, str): i = getcidx(dat, i)
    dat.Xstore(dlp.PData.newfromnumpy(arr), 0, 1, i)


def convertAM(sel, source, target, tie=False):
    # Output
    # fno = '3_20_cmb.hmm'
    fno = target
    fni = source

    ## Load HMM
    h = dlp.PHmm()
    h.Restore(fni)

    # Get old phonem table
    udo = list(map(bytes.decode, getcomp(h.ud(), '~NAM')))

    # Get new phonem table
    udn = list(sel)

    # Build new FST
    f = dlp.PFst()

    if not tie:
        # Get Gaussian parameters
        hmean = dlp.PData()
        hicov = dlp.PData()
        h.gm().Extract(hmean, hicov)
        hmean = hmean.tonumpy()
        hicov = hicov.tonumpy()
        varonly = h.gm().icov().nrec() == 0
        if varonly: hicov = 1 / hicov.sum(1, keepdims=True)
        htmx = None if h.gm().mmap() is None else h.gm().mmap().tmx().tonumpy()
        fmean = []
        ficov = []
        ftmx = np.zeros((0, 0))

    # Get unit index list
    for n, ids in sel.items():
        print(f'Merge {",".join(ids)} to {n}')
        udi = [udo.index(p) for p in ids]
        udi = dlp.PData.newfromnumpy(np.array(udi))

        # Build FST for this ids
        f1 = dlp.PFst()
        f1.CopyUi(h, udi, 0)
        f1.Union(f1)

        # Map output symbols
        tos = getcomp(f1.td(), '~TOS')
        tos[tos >= 0] = udn.index(n)
        storecomp(f1.td(), '~TOS', tos)

        if not tie:
            # Map input symbols
            tis = getcomp(f1.td(), '~TIS')
            use = sorted(set(tis[tis >= 0]))
            off = len(fmean if htmx is None else ftmx)
            mp = {k: i + off for i, k in enumerate(use)}
            mp[-1] = -1
            tis[...] = [mp[i] for i in tis]
            storecomp(f1.td(), '~TIS', tis)

            if not htmx is None:
                inf = htmx.max()
                guse = np.where((htmx[use] != inf).any(0))[0]
                gadd = htmx[use][:, guse]
                gs = gadd.shape;
                fs = ftmx.shape
                gadd = np.concatenate((np.ones((gs[0], fs[1])) * inf, gadd), axis=1)
                ftmx = np.concatenate((ftmx, np.ones((fs[0], gs[1])) * inf), axis=1)
                ftmx = np.concatenate((ftmx, gadd), axis=0)
                use = guse

            fmean += list(hmean[use])
            ficov += list(hicov[use])

        # Add FST to output FST
        f.Cat(f1)

    cunam = getcidx(h.ud(), '~NAM')
    h.CopyFst(f)
    os = dlp.PData.newfromnumpy(np.array([s.encode() for s in udn], dtype=f'|S{h.ud().GetCompType(cunam)}'))
    h.ud().Xstore(os, 0, 1, cunam)
    os = dlp.PData.newfromnumpy(np.array([s.encode() for s in udn], dtype=f'|S{h.ud().GetCompType(cunam)}'))
    h.os().Reallocate(len(udn))
    h.os().Xstore(os, 0, 1, cunam)

    if not tie:
        # Setup gmm
        if len(ftmx):
            vm = dlp.PVmap()
            vm.Setup(dlp.PData.newfromnumpy(ftmx), 'lsadd', 'add', float('inf'))
        else:
            vm = None
        if not varonly:
            h.gm().SETOPTION('/icov')
        h.gm().Setup(dlp.PData.newfromnumpy(np.array(fmean)), dlp.PData.newfromnumpy(np.array(ficov)), vm)

    # Save HMM
    h.Save(fno, zip=True)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} config')
        raise SystemExit()

    ''' 
        *   config       - YAML config file;
    '''
    import yaml

    config_file = sys.argv[1]
    project = config_file.split('.')[0]
    target = project + '.hmm'
    source = ["3_20.hmm"]
    classfile = 'classes_' + project + '.txt'
    gauss_tie = False

    try:
        with open(config_file, 'r') as stream:
            config = yaml.safe_load(stream)
        locals().update(config)
    except:
        raise Warning('No yaml config file. Using default configuration')

    classes = read_classes(config['classfile'])
    mapping = config['mapping']
    keys = list(mapping.keys())

    diff = [i for i, j in zip(classes, keys) if i != j]

    if len(diff) != 0:
        raise SystemError('Target phoneme classes definitions do not match the mappings')

    convertAM(mapping, source, target, tie=gauss_tie)

    exit(0)
