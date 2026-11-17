# Recreate the raw mp3 folder from the voice_*.js bundles in the repo.
# Run this FIRST in a new session, before build6.py, otherwise rebuilt bundles would be empty.
import json,glob,os,base64,sys
repo=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out=sys.argv[1] if len(sys.argv)>1 else '/home/claude/kids-app/audio/';os.makedirs(out,exist_ok=True);n=0
for f in sorted(glob.glob(os.path.join(repo,'voice_*.js'))):
    t=open(f).read();d=json.loads(t[t.index('||{},')+5:t.rindex(');')])
    for h,b in d.items():
        p=out+h+'.mp3'
        if not os.path.exists(p):open(p,'wb').write(base64.b64decode(b));n+=1
print('extracted',n,'clips to',out)
