import json,hashlib,re,os,sys,base64,subprocess,urllib.request,time,threading
from concurrent.futures import ThreadPoolExecutor
K=open('/home/claude/tts/.key').read().strip()
texts=json.load(open('/home/claude/tts/texts2.json'))
os.makedirs('/home/claude/kids-app/audio',exist_ok=True)
emo=re.compile('[\U0001F000-\U0001FAFF☀-➿️‍⬀-⯿←-⇿]')
SYL=set(['בָּא','אָה','לָה','חָה','הָא','נָה','קָה','שָׁה','רָה','מָה','תָּא','יָה','כָּה','דָּה','גָּה','עַה','פָּא','סָה','וָה','צָה','טָה','זָא'])
def synth_text(x):
    t=x['t']
    if x['l']=='he' and t in SYL: t=t[:-1]   # pure syllable, e.g. בָּא -> בָּ
    t=emo.sub('',t).replace('❓','?').strip()
    return t
def fname(x): return hashlib.sha1((x['l']+'|'+x['t']).encode()).hexdigest()[:12]+'.mp3'
lock=threading.Lock();stats={'ok':0,'fail':0,'sec':0.0};log=open('/home/claude/tts/gen.log','a')
def one(x):
    out='/home/claude/kids-app/audio/'+fname(x)
    if os.path.exists(out) and os.path.getsize(out)>500: return
    txt=synth_text(x)
    if not txt: return
    body={"contents":[{"parts":[{"text":txt}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":"Kore"}}}}}
    for attempt in range(6):
        try:
            req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent",data=json.dumps(body).encode(),headers={"x-goog-api-key":K,"Content-Type":"application/json"})
            r=json.load(urllib.request.urlopen(req,timeout=120))
            p=r['candidates'][0]['content']['parts'][0]['inlineData'];raw=base64.b64decode(p['data'])
            tmp=out+'.raw';open(tmp,'wb').write(raw)
            fmt=[] if 'wav' in p.get('mimeType','') else ['-f','s16le','-ar','24000','-ac','1']
            subprocess.run(['ffmpeg','-y','-loglevel','error',*fmt,'-i',tmp,'-af','silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.4:stop_threshold=-45dB,apad=pad_dur=0.15','-ac','1','-ar','24000','-b:a','40k',out],check=True)
            os.remove(tmp)
            d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout or 0)
            with lock: stats['ok']+=1;stats['sec']+=d;log.write(json.dumps({'f':fname(x),'t':x['t'],'d':d},ensure_ascii=False)+'\n');log.flush()
            return
        except urllib.error.HTTPError as e:
            msg=e.read()[:300]
            if e.code in (429,500,503): time.sleep(5*(attempt+1));continue
            with lock: stats['fail']+=1;log.write(json.dumps({'f':fname(x),'t':x['t'],'err':f'{e.code} {msg}'},ensure_ascii=False)+'\n');log.flush()
            return
        except Exception as e:
            time.sleep(3*(attempt+1))
    with lock: stats['fail']+=1;log.write(json.dumps({'f':fname(x),'t':x['t'],'err':'gave up'},ensure_ascii=False)+'\n');log.flush()
with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv)>1 else 6) as ex: list(ex.map(one,texts))
print('DONE',stats)
