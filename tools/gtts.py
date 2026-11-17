import json,sys,base64,subprocess,urllib.request,time
K=open('/home/claude/tts/.key').read().strip()
def tts(text,out,model='gemini-3.8-flash-tts',voice='Kore',style=None):
    prompt=(style+': ' if style else '')+text
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"x-goog-api-key":K,"Content-Type":"application/json"})
    try: r=json.load(urllib.request.urlopen(req,timeout=90))
    except urllib.error.HTTPError as e: return 'HTTP %s %s'%(e.code,e.read()[:300])
    p=r['candidates'][0]['content']['parts'][0]['inlineData']
    pcm=base64.b64decode(p['data'])
    open(out+'.pcm','wb').write(pcm)
    fmt=[] if 'wav' in p.get('mimeType','') else ['-f','s16le','-ar','24000','-ac','1']
    subprocess.run(['ffmpeg','-y','-loglevel','error',*fmt,'-i',out+'.pcm','-b:a','48k',out],check=True)
    import os;os.remove(out+'.pcm');return 'ok '+p.get('mimeType','')
if __name__=='__main__':
    t='בָּ, מָ, לָ, תָּ, חָ. הָאוֹת לָמֶד. חַלָּה, מָרָק, שַׁבָּת, אַרְנָב, עַכְבָּר.'
    for m in ['gemini-3.8-flash-tts','gemini-3.1-flash-tts-preview']:
        print(m, tts(t,f'/home/claude/tts/g_{m}.mp3',model=m,style='קראי בעברית, לאט וברור, לילד בכיתה א׳, בדיוק לפי הניקוד'))
