import os
import sys

def dlabpro_path():
    def pyfind(dn):
        base=os.path.join(dn,'build','python')
        ret=[]
        for f in os.listdir(base):
            fn=os.path.join(base,f)
            if f[:4]=='lib.' and os.path.isdir(fn): ret.append(fn)
        return list(reversed(sorted(ret)))
    if 'DLABPRO_HOME' in os.environ:
        dn=os.environ['DLABPRO_HOME']
        if os.path.isdir(dn): return pyfind(dn)
    if 'UASR_HOME' in os.environ:
        un=os.path.split(os.environ['UASR_HOME'])[0]
        for d in ['dlabpro','dLabPro']:
            dn=os.path.join(un,d)
            if os.path.isdir(dn): return pyfind(dn)
    raise ImportError("Dlabpro library path not found")


try:
    sys.path=dlabpro_path()+sys.path
    from dlabpro import *
    found=True
except ImportError:
    found=False

