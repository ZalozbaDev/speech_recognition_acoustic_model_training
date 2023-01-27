#!/usr/bin/python3

import re

# ctxs: 0:<empty>, 1:<eps>, 2..6:-43..-47, 7..77664:tri  #2+5+77658=77665
# C-IS: 1..77664 #77664
#
# AM-Phones: 1..2, 3..42  # 2+40=42
# AM-PdfCls: 3*p=126
# AM-Triples: 3543 [1..42 #42 ; 0..2 #3 ; 0..3391 #3392]
# AM-Triples: 3543 (phone,state/pdfclass,pdf)
# AM-Logprobs: #7087(-1) = Triples*2 (loop,nonloop,...)
# AM-Pdfs:  3392
#
# Tree: [0..42 , 0..42, 0..42, 0..2] => [0..3391]
# Tree: (phone-l,phone-m,phone-r,state/pdfclass) => pdf
#
# H-IS: 2..7086/2, 7087..7092 #3543+6=3549 => triples=(phone,state,pdf)
# H-OS: 1..77664  #77664 => ilabels=(phone-l,phone-m,phone-r)

def loadphones(fn):
    with open(fn,'r') as f: dat=f.readlines()
    phones=filter( lambda l:re.match('^#[0-9]+$',l[0]) is None , map(lambda s:s.strip().split(' '),dat) )
    phones,ids=zip(*phones)
    if list(map(int,ids))!=list(range(len(ids))): raise ValueError(f'Symbol ids not sequential in {fn}')
    if phones[0]!='<eps>': raise ValueError(f'First phoneme is no <eps>')
    return phones

class Tree:
    def __init__(self,fn=None,dat=None):
        if not fn is None:
            with open(fn,'r') as fd: dat=fd.read()

        if (m:=re.match('ContextDependency ([0-9]+) ([0-9]+) ToPdf ((.|\n)*)EndContextDependency',dat)) is None: raise ValueError('Parse tree failed')
        self.N,self.P=map(int,m.groups()[:2])
        dat=[m[3]+' <END>']
        self.ev=Tree.getevent(dat)
        if dat[0]!='<END>': raise ValueError('parse')

    def get(self,*x): return self.ev.get(*x)

    def spl(dat,num):
        x=re.split('\\s+',dat[0].strip(),num)
        if len(x)!=num+1: raise ValueError('parse')
        dat[0]=x[-1]
        return x[:-1]

    def getevent(dat):
        t=Tree.spl(dat,1)[0]
        if not t in ('CE','SE','TE','NULL'): raise ValueError(f'unknown typ: {t}')
        return eval(f'Tree.{t}')(dat)

    class CE:
        def __init__(self,dat):
            self.val=int(Tree.spl(dat,1)[0])
        def get(self,*x): return self.val

    class SE:
        def __init__(self,dat):
            x=Tree.spl(dat,2)
            if x[-1]!='[': raise ValueError('parse')
            self.key=int(x[0])

            if (e:=dat[0].find(']'))<0: raise ValueError('parse')
            self.yes=set(map(int,re.split('\\s+',dat[0][:e].strip())))
            dat[0]=dat[0][e+1:]

            if Tree.spl(dat,1)[0]!='{': raise ValueError('parse')
            self.evy=Tree.getevent(dat)
            self.evn=Tree.getevent(dat)
            if Tree.spl(dat,1)[0]!='}': raise ValueError('parse')
        def get(self,*x): return (self.evy if x[self.key] in self.yes else self.evn).get(*x)

    class TE:
        def __init__(self,dat):
            x=Tree.spl(dat,3)
            if x[-1]!='(': raise ValueError('parse')
            self.key,num=map(int,x[:2])
            self.evs={i:Tree.getevent(dat) for i in range(num)}
            if Tree.spl(dat,1)[0]!=')': raise ValueError('parse')
        def get(self,*x): return self.evs[x[self.key]].get(*x)

    class NULL:
        def __init__(self,dat): pass
        def get(self,*x): return None

    def __repr__(self):
        return f'Tree-Model context-width={self.N} context-position={self.P}'
    __str__=__repr__

    def bldctxs(self,phones,disambig):
        if self.N==1 and self.P==0:
            return [(-pi,) if pi in disambig else (pi,) for pi,p in enumerate(phones) if p!='<eps>']
        elif self.N==3 and self.P==1:
            ctxs=[(0,)]
            ps=sorted(set(range(len(phones))).difference(disambig))
            psreal=[p for p in ps if phones[p]!='<eps>']
            ctxs+=[(v1,v2,v3) for v1 in ps for v2 in psreal for v3 in psreal+[phones.index('<eps>')]]
            ctxs+=[(-v,) for v in sorted(disambig)]
            return ctxs
        else:
            raise ValueError(f'unsupported N={self.N}, P={self.P}')

    def fstcontext(self,phones,disambig,nxtsym,ctxs):
        try: import uasrpy,iasr
        except: import iasrrdc as iasr
        f=iasr.Fst(i=ctxsym(phones,ctxs),o=phones[1:])
        u=f.addu('ctx')
        if self.N==1 and self.P==0:
            s0=u.adds(True)
            for i,ctx in enumerate(ctxs): u.addt(s0,s0,i,abs(ctx[0])-1)
        elif self.N==3 and self.P==1:
            ctxref={l:i for i,l in enumerate(ctxs)}
            realphn=[pi for pi,p in enumerate(phones) if p!='<eps>' and not pi in disambig]
            s0=u.adds()
            se=u.adds(True)
            sp1={p:u.adds() for i,p in enumerate(realphn)}
            sp2={p:u.adds() for i,p in enumerate((p1,p2) for p1 in realphn for p2 in realphn)}
            for p1 in realphn:
                u.addt(s0,sp1[p1],ctxref[(0,)],p1-1)
                u.addt(sp1[p1],se,ctxref[(0,p1,0)],nxtsym-1)
                for p2 in realphn:
                    u.addt(sp1[p1],sp2[(p1,p2)],ctxref[(0,p1,p2)],p2-1)
                    u.addt(sp2[(p1,p2)],se,ctxref[(p1,p2,0)],nxtsym-1)
                    for p3 in realphn:
                        u.addt(sp2[(p1,p2)],sp2[(p2,p3)],ctxref[(p1,p2,p3)],p3-1)
            for s in (0,*sp1.values(),*sp2.values()):
                for d in disambig: u.addt(s,s,ctxref[(-d,)],d-1)
            u.addt(s0,se,ctxref[(0,)],nxtsym-1)
        else:
            raise ValueError(f'unsupported N={self.N}, P={self.P}')

        return f

def ctxsym(phones,ctxs):
    return ['-'.join(map(lambda p:phones[abs(p)],ctx)) for ctx in ctxs]

class Trans:
    def __init__(self,fn=None,dat=None):
        if not fn is None:
            with open(fn,'r') as fd: dat=fd.read()

        self.f={}
        for de in re.split('<TopologyEntry>',dat)[1:]:
            de=re.split('</TopologyEntry>',de)[0]
            phns=re.findall('<ForPhones>([0-9 \n]+)</ForPhones>',de)[0]
            phns=list(map(int,re.split('[ \n]+',phns.strip())))
            f=[]
            for ds in re.findall('<State> ([0-9]+) (.*)</State>',de):
                s=int(ds[0])
                pdf=re.findall('<PdfClass> ([0-9]+)',ds[1])
                pdf=int(pdf[0]) if len(pdf) else None
                ut=False
                for dt in re.findall('<Transition> ([0-9]+) (-?[0-9.]+)',ds[1]):
                    e=int(dt[0])
                    w=float(dt[1])
                    f.append([s,e,pdf,w])
                    ut=True
                if not ut: f.append([s,])
            for p in phns: self.f[p]=list(map(list,f))

        trp=re.findall('<Triples> +[0-9]+ +\n([0-9 \n]+)</Triples>',dat)[0]
        self.trp=[tuple(map(int,l.strip().split(' '))) for l in trp.strip().split('\n')]

        log=re.findall('<LogProbs>\\s*\\[([0-9\\s.-]+)\\]\\s*</LogProbs>',dat)[0]
        self.log=[float(l) for l in re.split('\\s+',log.strip())]

        st={p:set(t[2] for t in f if len(t)>2) for p,f in self.f.items()}
        for p,s,g in self.trp:
            if not p in self.f: raise ValueError(f'Import of transition model failed: phone {p} not in Topology')
            if not s in st[p]: raise ValueError(f'Import of transition model failed: state {s} of phone {p} not in Topology')
        

    def __repr__(self):
        st=[len(set(t[2] for t in f if len(t)>2)) for f in self.f.values()]
        pdfs=set(l[2] for l in self.trp)
        return f'Transition-Model\n'+ \
            f' - Phones {min(self.f)}..{max(self.f)} #{len(self.f)}\n'+ \
            f' - PdfCls #{min(st)}..#{max(st)} #{sum(st)}\n'+ \
            f' - Tids #{len(self.trp)} LogProbs #{len(self.log[1:])}\n'+ \
            f' - Pdfs {min(pdfs)}..{max(pdfs)} #{len(pdfs)}'
    __str__=__repr__

    def bldtids(self,ctxs):
        trpdis=[(f'#{ctx[0]}',) for ctx in ctxs if len(ctx)==1 and ctx[0]<=0]
        trp=self.trp+trpdis
        return trp,[trp.index(v) for v in trpdis]

    def fstphone(self,tree,phones,ctxs,tids):
        try: import uasrpy,iasr
        except: import iasrrdc as iasr
        tidsref={tid:i for i,tid in enumerate(tids)}
        Ha=iasr.Fst(o=ctxsym(phones,ctxs))
        disambig=set(phones[-ctx[0]] for ctx in ctxs if len(ctx)==1 and ctx[0]<0)
        for p in phones:
            if p!='<eps>' and not p in disambig: u=Ha.addu(p); u.adds()
        xreg={}
        for o,ctx in enumerate(ctxs):
            if len(ctx)==1 and ctx[0]<=0: continue # skip disambig
            f=self.f[ctx[tree.P]]
            u=Ha.ud[ctx[tree.P]-1]
            pdfs=sorted(set(t[2] for t in f if len(t)>1))
            ts=tuple((ctx[tree.P],d,tree.get(*ctx,d)) for d in pdfs)
            #wloop=lambda s:math.log(1-math.exp(next(iter(l[2] for l in f if len(l)>1 and l[0]==l[1]==s)))) use trans.log[i] for w
            smap=lambda s,offs:s if s==0 else offs+s
            if ts in xreg:
                for l in f:
                    if len(l)==1: continue
                    s,e,d,tw=l
                    if s!=0: continue
                    if s==e: continue
                    u.addt(0,smap(e,xreg[ts]),tidsref[ts[d]],o)
            else:
                offs=len(u.sd)-1
                xreg[ts]=offs
                xs=max(l[i] for l in f for i in range(1 if len(l)<=2 else 2))
                for i in range(xs): u.adds()
                for l in f:
                    if len(l)==1: u.sd[smap(l[0],offs)]=True
                    else:
                        s,e,d,tw=l
                        if s==e: continue
                        u.addt(smap(s,offs),smap(e,offs),tidsref[ts[d]],o if s==0 else -1)

        pdfs=[tid[-1] for tid in tids if isinstance(tid[0],int)]
        if len(pdfs)*2+1!=len(self.log): raise ValueError('number of tids missmatching number of logprobs')
        Ha.i=list(zip(pdfs,self.log[1::2],self.log[2::2]))

        return Ha

class Gmm:
    class G:
        def __init__(self,dat,dim):
            import numpy as np
            import io
            self.gconsts     =np.loadtxt(io.StringIO(re.findall('<GCONSTS>\\s*\\[([-0-9.e\\s]+)\\]',dat)[0].strip()))
            self.weights     =np.loadtxt(io.StringIO(re.findall('<WEIGHTS>\\s*\\[([-0-9.e\\s]+)\\]',dat)[0].strip()))
            self.meansinvvars=np.loadtxt(io.StringIO(re.findall('<MEANS_INVVARS>\\s*\\[([-0-9.e\\s]+)\\]',dat)[0].strip()))
            self.invvars     =np.loadtxt(io.StringIO(re.findall('<INV_VARS>\\s*\\[([-0-9.e\\s]+)\\]',dat)[0].strip()))
            ngau=self.gconsts.shape[0]
            if self.gconsts.shape     !=(ngau,): raise ValueError('Missmatch in GMM shape')
            if self.weights.shape     !=(ngau,): raise ValueError('Missmatch in GMM shape')
            if self.meansinvvars.shape!=(ngau,dim): raise ValueError('Missmatch in GMM shape')
            if self.invvars.shape     !=(ngau,dim): raise ValueError('Missmatch in GMM shape')
        def __repr__(self): return f'Mixture DIM {self.invvars.shape[1]} NGAU #{self.invvars.shape[0]}'
        __str__=__repr__

    def __init__(self,fn=None,dat=None):
        if not fn is None:
            with open(fn,'r') as fd: dat=fd.read()

        if (m:=re.search('<DIMENSION> ([0-9]+) <NUMPDFS> ([0-9]+)',dat)) is None: raise ValueError('Parse GMM failed')
        self.dim,npdfs=map(int,m.groups())

        self.gs=[]
        for de in re.split('<DiagGMM>',dat)[1:]:
            de=re.split('</DiagGMM>',de)[0]
            self.gs.append(Gmm.G(de,self.dim))
        if len(self.gs)!=npdfs: raise ValueError('Missmatch in GMM npdfs')

    def __repr__(self):
        return f'GMM-Model DIM {self.dim} NMIX #{len(self.gs)} NGAU #{sum(g.invvars.shape[0] for g in self.gs)}'
    __str__=__repr__

def saveclasses(fn,ctxs,phones):
    i2p=dict(enumerate(phones))
    with open(fn,'w') as f:
        f.write('## UASR class definition file\n')
        f.write('\n')
        for ctx in ctxs:
            if len(ctx)==0 or ctx[0]<=0: continue
            n='-'.join(i2p[i] for i in ctx)
            f.write(f' {n:3s} 3  1.0  [spe]\n')
        f.write('\n')
        f.write('## EOF\n')


if __name__=='__main__': 

    import os,sys
    import numpy as np
    try: import uasrpy
    except: pass
    import idlabpro as dlp

    def blduasrgm(gmm,am):
        g=  np.concatenate([g.gconsts      for g in gmm.gs])
        miv=np.concatenate([g.meansinvvars for g in gmm.gs])
        iv= np.concatenate([g.invvars      for g in gmm.gs])

        m=miv/iv
        v=1/iv.reshape(-1,1,iv.shape[-1])

        tmxw=np.concatenate([g.weights for g in gmm.gs])
        tmxo=[gi for gi,g in enumerate(gmm.gs) for i in range(len(g.weights))]
        tmxi=list(range(len(tmxw)))
        tmx=dlp.PData.newfromnumpy(np.array([tmxi,tmxo]).T)
        tmx.AddComp("W",3008)
        tmx.Xstore(dlp.PData.newfromnumpy(tmxw),0,1,2)
        
        mmap=dlp.PVmap()
        mmap.Setup(tmx,'lsadd','add',float('inf'))

        am.addgm()
        am.gm().Setup(dlp.PData.newfromnumpy(m),dlp.PData.newfromnumpy(v),mmap)

        return am

    if len(sys.argv) not in (2,3):
        print(f'Usage: {sys.argv[0]} KALDI-GMM.txt {{OUT-UASR.hmm}}')
        print(f'  - Parallel to "KALDI-GMM.txt" there need to be "phones.txt" and "tree.txt"')
        print(f'    ("KALDI-GMM.txt" can be created with "gmm-copy --binary=false")')
        print(f'    ("tree.txt" can be created with "copy-tree --binary=false")')
        print(f'  - Without "OUT-UASR.hmm" "KALDI-GMM.hmm" is created')
        print(f'  - Parallel to "OUT-UASR.hmm" "OUT-UASR_classes.txt" is created')
        raise SystemExit()

    kfn=sys.argv[1]
    ufn=sys.argv[2] if len(sys.argv)>2 else kfn.replace('.txt','')+'.hmm'
    kpfn=os.path.join(os.path.dirname(kfn),'phones.txt')
    ktfn=os.path.join(os.path.dirname(kfn),'tree.txt')
    ucfn=ufn.replace('.hmm','')+'_classes.txt'
    
    print(f'Load {kfn}')
    with open(kfn,'r') as f:
        dat=f.read()
        trans=Trans(dat=dat)
        gmm=Gmm(dat=dat)
    print(f'Load {ktfn}')
    tree=Tree(ktfn)
    print(f'Load {kpfn}')
    phones=loadphones(kpfn)
    if len(gmm.gs)!=len(set(l[2] for l in trans.trp)): raise ValueError('Missmatch in num of pdfs')
    if set(trans.f)!=set(i for i,p in enumerate(phones) if p!='<eps>'): raise ValueError('Missmatch in phones.txt')

    print(f'Convert')
    am=dlp.PHmm()
    blduasrgm(gmm,am)
    ctxs=tree.bldctxs(phones,[])
    tids,disambigtid=trans.bldtids(ctxs)
    Ha=trans.fstphone(tree,phones,ctxs,tids)
    am.CopyFst(Ha.todlp().d)

    am.ud().AddComp('~XL',2002)
    xs=dlp.PData()
    xs.Select(am.ud(),1,1)
    xl=np.clip(xs.tonumpy()-1,0,None)
    am.ud().Xstore(dlp.PData.newfromnumpy(xl),0,1,5)
    
    nxtsym=32767
    ctx=tree.fstcontext(phones,[],nxtsym,ctxs)
    dctx=ctx.todlp().d
    def addval(dat,name,val): dat.AddComp(name,2008); dat.Dstore(val,0,dat.FindComp(name))
    addval(dctx.ud(),'~N',tree.N)
    addval(dctx.ud(),'~P',tree.P)
    addval(dctx.ud(),'~NXT',nxtsym)
    am.AddFstWord('ctx',dctx)

    print(f'Save {ufn}')
    am.Save(ufn,zip=True)
    #print(f'Save {ucfn}')
    #saveclasses(ucfn,ctxs,phones)

