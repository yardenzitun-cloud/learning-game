import json,time,base64,subprocess,urllib.request,sys
K=open('/home/claude/tts/.key').read().strip();H={"x-goog-api-key":K,"Content-Type":"application/json"}
TXT='כל הכבוד, תמר! בואי נמשיך לשלב הבא. מה המילה באנגלית? Butterfly!'
VOICES=sys.argv[1].split(',')
def api(url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body else None,headers=H);return json.load(urllib.request.urlopen(r,timeout=300))
reqs=[{"request":{"contents":[{"parts":[{"text":TXT}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":v}}}}},"metadata":{"key":v}} for v in VOICES]
d=api("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:batchGenerateContent",{"batch":{"display_name":"voices","input_config":{"requests":{"requests":reqs}}}})
n=d['name']
while True:
    time.sleep(20);d=api(f"https://generativelanguage.googleapis.com/v1beta/{n}");m=d.get('metadata',{})
    if m.get('state','').endswith(('SUCCEEDED','FAILED','CANCELLED','EXPIRED')):break
for it in (d.get('response') or m.get('output') or {}).get('inlinedResponses',{}).get('inlinedResponses',[]):
    v=it['metadata']['key'];p=it['response']['candidates'][0]['content']['parts'][0]['inlineData']
    open(f'/tmp/{v}.raw','wb').write(base64.b64decode(p['data']))
    fmt=[] if 'wav' in p.get('mimeType','') else ['-f','s16le','-ar','24000','-ac','1']
    subprocess.run(['ffmpeg','-y','-loglevel','error',*fmt,'-i',f'/tmp/{v}.raw','-b:a','64k',f'/home/claude/tts/voice_{v}.mp3'],check=True);print('ok',v)
