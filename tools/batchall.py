import json,os,sys,time,base64,subprocess,urllib.request
sys.path.insert(0,'/home/claude/tts')
import importlib.util
spec=importlib.util.spec_from_file_location('g','/home/claude/tts/genall.py')
src=open('/home/claude/tts/genall.py').read().split('def one(x):')[0]  # reuse helpers only
ns={};exec(src,ns)
K=open('/home/claude/tts/.key').read().strip();H={"x-goog-api-key":K,"Content-Type":"application/json"}
texts=json.load(open(sys.argv[1] if len(sys.argv)>1 else '/home/claude/tts/texts2.json'))
AUD='/home/claude/kids-app/audio/'
import hashlib
VOICE=os.environ.get('VOICE','Kore')
def FN(x): return ns['fname'](x) if VOICE=='Kore' else hashlib.sha1((VOICE+'|'+x['l']+'|'+x['t']).encode()).hexdigest()[:12]+'.mp3'
pend=[x for x in texts if ns['synth_text'](x) and not os.path.exists(AUD+FN(x))]
print('pending',len(pend),flush=True)
def mk(t):return {"contents":[{"parts":[{"text":t}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE}}}}}
def api(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,headers=H);return json.load(urllib.request.urlopen(r,timeout=600))
names=[]
for c in range(0,len(pend),150):
    chunk=pend[c:c+150]
    reqs=[{"request":mk(ns['synth_text'](x)),"metadata":{"key":FN(x)}} for x in chunk]
    d=api("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:batchGenerateContent",{"batch":{"display_name":f"tts-{c}","input_config":{"requests":{"requests":reqs}}}})
    names.append(d['name']);print('submitted',d['name'],len(chunk),flush=True)
json.dump(names,open('/home/claude/tts/batches.json','w'))
done=set();ok=0;bad=0
def save(key,inl):
    global ok
    out=AUD+key;tmp=out+'.raw';open(tmp,'wb').write(base64.b64decode(inl['data']))
    fmt=[] if 'wav' in inl.get('mimeType','') else ['-f','s16le','-ar','24000','-ac','1']
    subprocess.run(['ffmpeg','-y','-loglevel','error',*fmt,'-i',tmp,'-af','silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.4:stop_threshold=-45dB,apad=pad_dur=0.15','-ac','1','-ar','24000','-b:a','40k',out],check=True);os.remove(tmp);ok+=1
while len(done)<len(names):
    time.sleep(45)
    for n in names:
        if n in done: continue
        try: d=api(f"https://generativelanguage.googleapis.com/v1beta/{n}")
        except Exception as e: print('poll err',e,flush=True);continue
        m=d.get('metadata',{});st=m.get('state')
        if st in ('BATCH_STATE_SUCCEEDED','BATCH_STATE_FAILED','BATCH_STATE_CANCELLED','BATCH_STATE_EXPIRED'):
            done.add(n);resp=(d.get('response') or m.get('output') or {}).get('inlinedResponses',{}).get('inlinedResponses',[])
            for it in resp:
                key=(it.get('metadata') or {}).get('key')
                try: save(key,it['response']['candidates'][0]['content']['parts'][0]['inlineData'])
                except Exception as e: bad+=1;print('bad',key,str(e)[:120],json.dumps(it)[:200],flush=True)
            print(n,st,m.get('batchStats'),'saved total',ok,flush=True)
print('ALLDONE ok',ok,'bad',bad,flush=True)
