import json,os,base64,hashlib,re
G='/home/claude/learning-game/';AUD='/home/claude/kids-app/audio/'
H=lambda x:hashlib.sha1(('Leda|'+x['l']+'|'+x['t']).encode()).hexdigest()[:12]
O=json.load(open('/home/claude/tts/rec_leda_all.json'));T=json.load(open('/home/claude/tts/texts4.json'))
C={};miss=[]
for x in O:
  if os.path.exists(AUD+H(x)+'.mp3'):C[x['t']]=H(x)
  else:miss.append(x['t'])
B={'yonatan':set(),'tohar':set(),'tamar':set(),'g8':set(),'g2':set(),'g3':set(),'parasha':set(),'extra':set()}
for x in T:
  if x['t'] in C:B[x['track']].add(C[x['t']])
for x in O:
  if x['track']=='extra' and x['t'] in C:B['extra'].add(C[x['t']])
def write(name,d):open(G+name,'w').write('window.AUDIO_DATA=Object.assign(window.AUDIO_DATA||{},'+json.dumps(d,separators=(',',':'))+');')
parts={}
for tr in ['yonatan','tohar','tamar','g8','g2','g3','parasha']:
  i=1
  while os.path.exists(G+f'voice_{tr}_{i}.js'):os.remove(G+f'voice_{tr}_{i}.js');i+=1
  cur={};size=0;n=0
  for h in sorted(B[tr]):
    b=base64.b64encode(open(AUD+h+'.mp3','rb').read()).decode()
    if size+len(b)>7_800_000 and cur:n+=1;write(f'voice_{tr}_{n}.js',cur);cur={};size=0
    cur[h]=b;size+=len(b)+20
  if cur:n+=1;write(f'voice_{tr}_{n}.js',cur)
  parts[tr]=n
write('voice_extra.js',{h:base64.b64encode(open(AUD+h+'.mp3','rb').read()).decode() for h in B['extra']})
s=open(G+'index.html',encoding='utf-8').read()
a=s.index('const CLIPS=')+12;e=s.index('};',a)+1
s=s[:a]+json.dumps(C,ensure_ascii=False,separators=(',',':'))+s[e:]
i=s.index('const CLIPS_T=');j=s.index('};',i)+2 if s[i+14:i+16]!='{}' else i+17
s=s[:i]+'const CLIPS_T={};'+s[j:]
s=s.replace("function clipOf(t){return curType()==='tamar'?CLIPS_T[t]:CLIPS[t];}","function clipOf(t){return CLIPS[t];}")
s=re.sub(r'const VOICE_PARTS=\{[^}]*\};','const VOICE_PARTS='+json.dumps(parts)+';',s)
s=re.sub(r"\.js\?v=(\d+)'",lambda m:".js?v=%d'"%(int(m.group(1))+1),s)
open(G+'index.html','w',encoding='utf-8').write(s)
w=re.sub(r"lg-v(\d+)",lambda m:'lg-v%d'%(int(m.group(1))+1),open(G+'sw.js').read());open(G+'sw.js','w').write(w)
print(parts,len(C),'extra',len(B['extra']),'miss',len(miss),miss[:5])
