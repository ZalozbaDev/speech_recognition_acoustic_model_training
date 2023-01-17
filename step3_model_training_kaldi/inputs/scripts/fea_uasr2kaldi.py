#!/usr/bin/python3

import sys,os,re
import kaldiio
import idlabpro as dlp
import numpy as np

if len(sys.argv)<2:
    raise SystemExit(f'Usage: {sys.argv[0]} UASR-CONFIG.cfg [-Puasrkey=value]')

# The dLabPro binary if it is in PATH, or the full path to the binary
dlabpro = 'dlabpro'

import asyncio
async def rundlp():
    prc=await asyncio.create_subprocess_exec(
        dlabpro,os.path.splitext(sys.argv[0])[0]+'.xtp',*sys.argv[1:],'-v2',
        stdout=asyncio.subprocess.PIPE,
    )
    out=[]
    while True:
        try: l=await asyncio.wait_for(prc.stdout.readline(),1)
        except asyncio.TimeoutError: pass
        else:
            if not l: break
            l=l.decode('utf-8')
            out.append(l)
            sys.stdout.write(l)
            continue
        prc.kill()
        break
    await prc.wait()
    return out

dlpout=asyncio.get_event_loop().run_until_complete(rundlp())

flsts=[(i,re.sub('^.*Output directory:\s+(.*)\s+\.\.\..*$','\\1',l.strip())) for i,l in enumerate(dlpout) if 'Output directory:' in l]
flsts={
    dn:re.findall('[0-9]+/[0-9]+\s+-\s+(.*):',''.join(dlpout[i0:i1]))
    for (i0,dn),(i1,x) in zip(flsts,flsts[1:]+[(len(dlpout),'')])
}

dsig=re.sub('^.*- Signal dir\s+:\s+(.*)\s+\\(.*$','\\1',next(iter(l for l in dlpout if 'Signal dir' in l))).strip()

def fn2user(fn): 
    
    """
    File name from User ID and the unique file identifier (full path) 
    
        fid -> usr-full_path  
    
    Examples of custom name convention:

       * CV/CV00017/common_voice_hsb_20359475.wav
       * HSB-2/RECS/0001/0001HSB_2_162_2.wav
       * SCF_MW_A/AABT/0003/AABT_139.wav
    """

    subfs=os.path.dirname(fn).split('/')
    
    if "HSB-" in fn:
        root=subfs[0].replace('-','_')
        usr=root.replace('_A','') + '_' + subfs[2]
    else:
        usr=subfs[1]
    fid=usr + '_'.join(subfs)+'_'+os.path.basename(fn)
    return usr,fid


def joinfn(*fn): return os.path.join(*fn[:-1])+'.'+fn[-1]

def trlget(*fn):
    with open(joinfn(*fn,'txt'),'r') as f:
        return re.sub('\s+',' ',f.read().strip())

def feaget(*fn):
    fea=dlp.PData()
    fea.Restore(joinfn(*fn,'dn3'))
    return fea.tonumpy().astype(np.float32)

print('')

for dn,flst in flsts.items():
    print(f'fea_uasr2kaldi {os.path.basename(dn)} #{len(flst)}')

    odn=dn.replace('/uasrfea/','/kaldifea/')
    if not os.path.exists(odn): os.makedirs(odn)

    with open(f'{odn}/text',   'w',encoding='utf-8') as ft, \
         open(f'{odn}/corp',   'w',encoding='utf-8') as fc, \
         open(f'{odn}/utt2spk','w',encoding='utf-8') as fu, \
         open(f'{odn}/wav.scp','w',encoding='utf-8') as fw, \
         kaldiio.WriteHelper(f'ark,scp:{odn}/features_sfa.ark,{odn}/features_sfa.scp') as ff:
        for fn in flst:
            usr,fid=fn2user(fn)
            trl=trlget(dn,fn)
            fsig=joinfn(dsig,fn,'wav')
            fea=feaget(dn,fn)

            ft.write(f'{fid} {trl}\n')
            fc.write(f'{trl}\n')
            fu.write(f'{fid} {usr}\n')
            fw.write(f'{fid} {fsig}\n')
            ff(fid,fea)
    print(f' => {odn}')

