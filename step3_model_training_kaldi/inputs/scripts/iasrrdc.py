import numpy as np

class SI:
    def lvst(self,trl,res):
        """
            return: (C,I,D,S)
        """
        trl=np.array(trl)
        lo=np.arange(len(trl)+1).reshape(-1,1)*[0,0,1,0,1]  # C,I,D,S,E = (I+D+S)-C/(len(trl)+1)

        for wr in res:

            ln=lo+[0,1,0,0,1]

            cor=trl==wr
            ln2=lo[:-1]+cor.reshape(-1,1)*[1,0,0,-1,-1-1/(len(trl)+1)]+[0,0,0,1,1]
            ln2=np.concatenate((ln[:1],ln2))

            sel=np.argmin((ln[:,-1],ln2[:,-1]),axis=0).reshape(-1,1)
            ln=ln*(1-sel)+ln2*sel

            lo=ln

            tlol=lo[0]
            for i,tlo in enumerate(lo[1:]):
                if tlol[-1]+1<tlo[-1]:
                    tlo[...]=tlol+[0,0,1,0,1]
                tlol=tlo

        return tuple(map(int,lo[-1,:-1]))

class Fst:
    class Unit:
        def __init__(self,name,sd=None,td=None,start=0):
            self.name=name
            self.sd=[] if sd is None else sd
            self.td=[] if td is None else td
            self.start=start
        def adds(self,final=False):
            self.sd.append(final)
            return len(self.sd)-1
        def addt(self,ini,ter,tis=-1,tos=-1,lsr=0,stk=0,**add):
            self.td.append({'ini':ini,'ter':ter,'tis':tis,'tos':tos,'lsr':lsr,'stk':stk,**add})
            return self.td[-1]
    def __init__(self,i=[],o=[],ud=None):
        self.ud=[] if ud is None else ud
        self.i=i
        self.o=o
    def addu(self,name):
        self.ud.append(self.Unit(name))
        return self.ud[-1]
    def todlp(self):
        import idlabpro as dlp
        if not dlp.found: raise ValueError('ERROR: dlabpro import failed')
        f=DFst(i=self.i,o=self.o)
        f.SETOPTION('/fst'); f.SETOPTION('/lsr'); f.Addunit('')

        ud=np.array([(len(u.sd),len(u.td)) for u in self.ud])
        ud=np.concatenate(( ud, np.cumsum(ud,0)-ud ),1)
        f.ud().Reallocate(len(ud))
        f.ud().Xstore(dlp.PData.newfromnumpy(ud),0,4,1)
        f.ud().Xstore(dlp.PData.newfromnumpy(np.array([u.name.encode() for u in self.ud],dtype=f'|S{f.ud().GetCompType(0)}')),0,1,0)

        td=np.array([(t['ter'],t['ini'],t['tis'],t['tos'],t['lsr']) for u in self.ud for t in u.td])
        f.td().Reallocate(len(td))
        f.td().Xstore(dlp.PData.newfromnumpy(td),0,5,0)

        sd=np.array([int(s) for u in self.ud for s in u.sd])
        f.sd().Reallocate(len(sd))
        f.sd().Xstore(dlp.PData.newfromnumpy(sd),0,1,0)

        encio=lambda io:[v.encode() for v in io]
        todlp=lambda io:dlp.PData.newfromnumpy(np.array(encio(io),dtype='|S255') if isinstance(io[0],str) else np.array(io,dtype=np.float64))
        if len(self.i)>0: f.is_().Copy(todlp(self.i))
        if len(self.o)>0: f.os().Copy(todlp(self.o))

        return f

class DFst:
    def __init__(self,d=None,i=None,o=None):
        import idlabpro as dlp
        if not dlp.found: raise ValueError('ERROR: dlabpro import failed')
        self.d=dlp.PFst() if d is None else d
        def getsym(da,df):
            if not da is None: return da
            if df.nrec()>0 and df.dim()==1 and df.GetCompType(0)<=255:
                return list(map(bytes.decode,df.tonumpy()))
            return []
        self.i=getsym(i,self.d.is_())
        self.o=getsym(o,self.d.os())
    def ud(self): return self.d.ud()
    def sd(self): return self.d.sd()
    def td(self): return self.d.td()
    def os(self): return self.d.os()
    def is_(self): return self.d.is_()
    def SETOPTION(self,name): self.d.SETOPTION(name)
    def Addunit(self,name): self.d.Addunit(name)
