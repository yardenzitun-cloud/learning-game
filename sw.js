const C='lg-v4';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
 const isPage=u.pathname.endsWith('/')||u.pathname.endsWith('.html');
 e.respondWith(caches.open(C).then(async c=>{const hit=await c.match(e.request);
  const net=fetch(e.request).then(r=>{if(r.ok)c.put(e.request,r.clone());return r;}).catch(()=>hit);
  return isPage?(net.then(r=>r||hit)):(hit||net);}));});
