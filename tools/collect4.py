import asyncio, json
from playwright.async_api import async_playwright
JS=r'''()=>{
 const out=new Map();let TR=null;
 const add=(p,l)=>{if(!p)return;if(typeof p==='string')p={t:p,l:l||'he'};if(!p.t||!p.t.trim())return;const t=p.l==='en'?p.t:gx(p.t);out.set(TR+'|'+(p.l||'he')+'|'+t,{t,l:p.l||'he',track:TR});};
 const plan={yonatan:['math1','heb1','sci1'],tamar:['mult5','math5','eng5'],tohar:['gan1','gan2'],g8:['g8words','g8gram','g8read'],g2:['math2'],g3:['math3','eng3']};
 S.profiles=[];for(const tr in plan)for(const g of ['m','f'])S.profiles.push({id:tr+'_'+g,name:'x',gender:g,track:tr,char:'fox'});buildKids();
 for(const tr in plan)for(const g of ['m','f']){cur.kid=tr+'_'+g;TR=tr;const K=KIDS[cur.kid];
  for(const s of plan[tr]){SUBJECTS[s].stages.forEach((st,i)=>{
   if(st.L){const sl=typeof st.L==='function'?st.L():st.L;sl.forEach(x=>{(x.say||[x.t.replace(/<[^>]+>/g,'')]).forEach(p=>add(p));const d=document.createElement('div');d.innerHTML=x.v||'';d.querySelectorAll('[data-he]').forEach(e=>add(e.dataset.he));d.querySelectorAll('[data-en]').forEach(e=>add({t:e.dataset.en,l:'en'}));});}
   if(st.W)st.W.forEach(w=>add({t:w[0],l:'en'}));
   if(st.mem){st.mem.items().forEach(it=>add(it.say));return;}
   const dyn=['math5','mult5','math2','math3'].includes(s)||st.dyn;const ok=t=>!(dyn&&/\d/.test(typeof t==='string'?t:t.t));
   for(let k=0;k<1500;k++){const q=st.g();(q.say||[]).filter(ok).forEach(p=>add(p));(q.cue||[]).filter(ok).forEach(p=>add(p));if(tr==='g8')(q.after||[]).forEach(p=>add(p));if(q.readOpts)optTexts(q).forEach(x=>x&&add(x));const h=hintSay(q);if(h&&/[א-ת]/.test(h)&&ok(h))add(h);}
  });}
  add(K.m?'קֹדֶם צָרִיךְ לְסַיֵּם אֶת הַשָּׁלָב הַקּוֹדֵם':'קודם צריך לסיים את השלב הקודם');
  add(K.m?'כָּל הַכָּבוֹד! הַחִמּוּם שֶׁל הַיּוֹם הֻשְׁלַם':'כל הכבוד! החימום של היום הושלם');
  add(K.m?'מְצָא אֶת הַזּוּגוֹת!':'מִצְאִי אֶת הַזּוּגוֹת!');
  add(K.m?'בּוֹא נִלְמַד. הִנֵּה הַתְּשׁוּבָה הַנְּכוֹנָה.':'בואי נלמד. הנה התשובה הנכונה.');
  SHOP[tr].forEach(it=>add(K.m?`קָנִיתָ ${it.n}!`:`קָנִית ${it.n}!`));
  for(let n=0;n<=12;n++)add(NUMW[n]);
  add('שָׁלוֹם! בּוֹאוּ נְשַׂחֵק!');add('שָׁלוֹם! כָּכָה נִשְׁמָע הַקּוֹל בְּעִבְרִית. בָּ, מָ, לָ.');add({t:'And this is English. Cat, cake, tree.',l:'en'});
 }
 // weekly Torah portion / holiday quiz – its own bundle, loaded only when the quiz starts
 TR='parasha';SUBJECTS.parasha.stages.forEach(st=>{(st.L||[]).forEach(sl=>add(sl.t.replace(/<[^>]+>/g,'')));for(let k=0;k<200;k++){const q=st.g();(q.say||[]).forEach(p=>add(p));optTexts(q).forEach(x=>x&&add(x));add(q.hint);}});
 ['כָּל הַכָּבוֹד! מַגִּיעַ לְךָ מַמְתָּק. לֵךְ לְסַפֵּר לְאַבָּא אוֹ לְאִמָּא!','כל הכבוד! מגיע לך ממתק. לכי לספר לאבא או לאמא!'].forEach(x=>add(x));
 // greetings for our own kids (exact names)
 [['yonatan','m','יהונתן'],['tamar','f','תמר'],['tohar','f','טוהר']].forEach(([tr,g,n])=>{TR=tr;cur.kid=tr+'_'+g;add(g==='m'?`שָׁלוֹם ${n}! בְּמָה נְשַׂחֵק הַיּוֹם?`:`שלום ${n}! במה נתחיל היום?`);});
 return [...out.values()];}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(); await pg.goto('file:///home/claude/learning-game/index.html')
        r=await pg.evaluate(JS); json.dump(r,open('/home/claude/tts/texts4.json','w'),ensure_ascii=False)
        import collections;print(len(r),collections.Counter(x['track'] for x in r))
        await b.close()
asyncio.run(main())
