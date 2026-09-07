/* A personal desktop around the guide. Links never launch or control local apps. */
(()=>{
'use strict';
const d=document, apps=window.DESKTOP_APPS||[], app=d.querySelector('.app');
if(!app||!apps.length)return;
const byId=new Map(apps.map(a=>[a.id,a]));
const el=(tag,cls,text)=>{const n=d.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
const svg=(body)=>'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+body+'</svg>';
const symbols={apple:'<path fill="currentColor" stroke="none" d="M16.9 12.7c0-2 1.6-3 1.7-3.1-1-1.5-2.5-1.7-3.1-1.7-1.3-.1-2.4.8-3.1.8-.6 0-1.6-.8-2.7-.8-1.4 0-2.6.8-3.3 2-1.4 2.4-.4 6.1.9 8 .6.9 1.3 1.9 2.3 1.8.9 0 1.3-.6 2.5-.6s1.6.6 2.6.6c1.1 0 1.7-.9 2.3-1.8.7-1 1-2 1-2.1-.1 0-3.1-1.2-3.1-3.1zM15 6.7c.5-.7.9-1.5.8-2.4-.8 0-1.8.6-2.4 1.3-.5.6-1 1.5-.9 2.3.9.1 1.8-.4 2.5-1.2z"/>',
search:'<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>',wifi:'<path d="M3 8a15 15 0 0 1 18 0M6 12a10 10 0 0 1 12 0M9 16a5 5 0 0 1 6 0"/><circle cx="12" cy="20" r="1" fill="currentColor"/>',battery:'<rect x="2" y="6" width="18" height="12" rx="3"/><path d="M23 10v4"/><path d="m12 4-5 9h5l-1 7 6-10h-5z" fill="currentColor" stroke="none"/>',sound:'<path d="m3 9 4 0 5-4v14l-5-4H3zM16 8a7 7 0 0 1 0 8m3-11a11 11 0 0 1 0 14"/>',display:'<rect x="2" y="3" width="14" height="11" rx="2"/><rect x="8" y="10" width="14" height="11" rx="2"/>',control:'<rect x="3" y="4" width="18" height="6" rx="3"/><rect x="3" y="14" width="18" height="6" rx="3"/><circle cx="7" cy="7" r="1"/><circle cx="17" cy="17" r="1"/>',clock:'<path d="M3 10a9 9 0 1 1 1 8M3 5v5h5M12 7v6l4 2"/>',more:'<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',folder:'<path fill="#68bdf4" stroke="#b9e3fc" d="M2 6h8l2 2h10v12H2z"/><path fill="#8ed2ff" stroke="none" d="M2 4h7l3 3H2z"/>'};
const tip=el('div','desktop-tooltip');tip.id='desktop-tooltip';tip.role='tooltip';tip.hidden=true;d.body.append(tip);
let tipOwner=null;
function hideTip(){tip.hidden=true;tipOwner?.removeAttribute('aria-describedby');tipOwner=null;}
function bindTip(n,title,detail){
 const show=()=>{tip.replaceChildren(el('strong','',title),el('span','',detail));tip.hidden=false;tipOwner=n;n.setAttribute('aria-describedby',tip.id);const r=n.getBoundingClientRect(),b=tip.getBoundingClientRect();tip.style.left=Math.max(8,Math.min(innerWidth-b.width-8,r.left+r.width/2-b.width/2))+'px';tip.style.top=(n.closest('.mac-dock')?r.top-b.height-16:r.bottom+10)+'px';};
 n.addEventListener('pointerenter',show);n.addEventListener('pointerleave',hideTip);n.addEventListener('focus',show);n.addEventListener('blur',hideTip);n.addEventListener('click',hideTip);
}
function appLink(a,cls){
 const n=el(a.url?'a':'button',cls);if(a.url){n.href=a.url;n.target='_blank';n.rel='noopener noreferrer';}else{n.type='button';n.addEventListener('click',()=>openDirectory(n,a.name));}
 n.dataset.appId=a.id;n.setAttribute('aria-label',a.name+(a.url?' — open website in new tab':' — view local helper details'));
 const image=el('img');image.src=a.icon;image.alt='';image.width=64;image.height=64;n.append(image);
 bindTip(n,a.name,a.url?'Open website in new tab':'Local helper · view details');return n;
}
const bar=el('header','mac-menu-bar');bar.setAttribute('aria-label','Example macOS menu bar');
const menus=el('nav','mac-app-menus');menus.setAttribute('aria-label','Desktop menu');
const apple=el('a','mac-apple');apple.href='https://www.apple.com/macos/';apple.target='_blank';apple.rel='noopener noreferrer';apple.innerHTML=svg(symbols.apple);apple.setAttribute('aria-label','macOS — open Apple website');bindTip(apple,'macOS Tahoe','Open Apple website');menus.append(apple);
const brand=el('button','mac-current-app','Codex');brand.type='button';brand.addEventListener('click',()=>openDirectory(brand,'Codex'));menus.append(brand);
for(const [name,target] of [['File','#files'],['Edit','#setup'],['View','#format'],['Window','#welcome'],['Help','#setup']]){const link=el('a','mac-text-menu',name);link.href=target;menus.append(link);}
const status=el('nav','mac-status');status.setAttribute('aria-label','Ethan’s menu bar apps');
const share=el('a','mac-screen-sharing');share.href='https://support.apple.com/guide/mac-help/share-the-screen-of-another-mac-mh14066/mac';share.target='_blank';share.rel='noopener noreferrer';share.innerHTML=svg(symbols.display);share.setAttribute('aria-label','Screen sharing — Apple guide');bindTip(share,'Screen sharing','Open Apple guide');status.append(share);
const menuApps=el('div','mac-menu-apps');
for(const id of window.DESKTOP_MENU_ORDER||[]){const a=byId.get(id);if(a)menuApps.append(appLink(a,'mac-menu-app'));}status.append(menuApps);
const more=el('button','mac-more-apps');more.type='button';more.innerHTML=svg(symbols.more);more.setAttribute('aria-label','More apps');more.addEventListener('click',()=>openDirectory(more));bindTip(more,'Apps in this setup','See the full Dock and menu bar');status.append(more);
const system=el('div','mac-system-items');
const systemItems=[
 ['Spotlight','search','https://support.apple.com/guide/mac-help/search-with-spotlight-mchlp1008/mac'],['Time Machine','clock','https://support.apple.com/guide/mac-help/back-up-files-mh35860/mac'],['Screen Mirroring','display','https://support.apple.com/guide/mac-help/stream-content-to-apple-tv-mh40768/mac'],['Battery','battery','https://support.apple.com/guide/mac-help/check-the-condition-of-your-mac-laptops-battery-mh20865/mac'],['Sound','sound','https://support.apple.com/guide/mac-help/change-the-sound-output-settings-mchlp2256/mac'],['Wi-Fi','wifi','https://support.apple.com/guide/mac-help/connect-your-mac-to-the-internet-using-wi-fi-mchlp1180/mac'],['Control Centre','control','https://support.apple.com/guide/mac-help/use-control-center-mchl50f94f8f/mac']];
for(const [name,symbol,url] of systemItems){
 const n=el('a','mac-system-link');n.href=url;n.target='_blank';n.rel='noopener noreferrer';n.innerHTML=svg(symbols[symbol]);n.setAttribute('aria-label',name+' — open Apple guide');bindTip(n,name,'Open Apple guide');system.append(n);
}status.append(system);
const clock=el('time','mac-clock');clock.setAttribute('aria-label','Date and time');status.append(clock);
function updateClock(){const now=new Date();clock.dateTime=now.toISOString();clock.textContent=new Intl.DateTimeFormat('en-GB',{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(now).replace(',','');}updateClock();setInterval(updateClock,60000);
bar.append(menus,status);d.body.prepend(bar);
const dock=el('nav','mac-dock');dock.setAttribute('aria-label','Ethan’s Dock — app websites');
const dockItems=el('div','mac-dock-items');
for(const a of apps.filter(a=>a.dock&&a.id!=='trash')){const n=appLink(a,'mac-dock-app');if(a.id==='textedit')n.classList.add('dock-divider');dockItems.append(n);}
for(const name of ['MusicOutput','Screenshots','Downloads','YOMG2Assets']){const n=el('a','mac-dock-app dock-folder');n.href=byId.get('finder').url;n.target='_blank';n.rel='noopener noreferrer';n.innerHTML=svg(symbols.folder);n.setAttribute('aria-label',name+' folder — open Finder guide');bindTip(n,name,'Local folder · open Finder guide');dockItems.append(n);}
const trash=byId.get('trash');if(trash)dockItems.append(appLink(trash,'mac-dock-app'));
dock.append(dockItems);d.body.append(dock);
const wallpaper=el('button','desktop-wallpaper-link','Ethan’s setup ↗');wallpaper.type='button';wallpaper.addEventListener('click',()=>openDirectory(wallpaper));bindTip(wallpaper,'Recreate this setup','Explore the apps and wallpaper');d.body.append(wallpaper);
const dialog=el('dialog','desktop-directory');dialog.setAttribute('aria-labelledby','desktop-directory-title');
const head=el('div','desktop-directory-head');const h=el('h2','','Apps in this setup');h.id='desktop-directory-title';const close=el('button','desktop-directory-close','×');close.type='button';close.setAttribute('aria-label','Close app list');head.append(h,close);
const intro=el('p','desktop-directory-intro','Ethan’s Dock and menu bar. Choose an app to open its website in a new tab.');
const search=el('input','desktop-app-search');search.type='search';search.placeholder='Search apps';search.setAttribute('aria-label','Search apps');
const list=el('div','desktop-app-list');const empty=el('p','desktop-no-apps','No apps found.');empty.hidden=true;
for(const a of apps){const item=el('div','desktop-app-card');item.dataset.search=(a.name+' '+a.note).toLowerCase();const link=appLink(a,'desktop-app-icon');if(!a.url){link.disabled=true;link.setAttribute('aria-label',a.name);}
 const info=el('div','desktop-app-info');if(a.url){const title=el('a','',a.name+' ↗');title.href=a.url;title.target='_blank';title.rel='noopener noreferrer';info.append(title);}else info.append(el('strong','',a.name));
 info.append(el('small','',a.note||(a.dock?'In Ethan’s Dock':'In Ethan’s menu bar')));item.append(link,info);list.append(item);}
const resources=el('div','desktop-resources');const wallpaperLink=el('a','','Get this wallpaper ↗');wallpaperLink.href='./desktop/tahoe.jpg';wallpaperLink.target='_blank';wallpaperLink.rel='noopener noreferrer';const macLink=el('a','','macOS Tahoe ↗');macLink.href='https://www.apple.com/macos/';macLink.target='_blank';macLink.rel='noopener noreferrer';resources.append(wallpaperLink,macLink);
const note=el('p','desktop-source-note','Dock order saved 7 September 2026. Extra menu bar apps come from the 25 August 2026 ultrawide screenshot and saved app settings. This desktop is a demonstration, not real macOS.');
const guides=el('details','desktop-system-guides');guides.append(el('summary','','macOS controls'));for(const [name,,url] of systemItems){const a=el('a','',name+' ↗');a.href=url;a.target='_blank';a.rel='noopener noreferrer';guides.append(a);}
dialog.append(head,intro,search,list,empty,resources,guides,note);d.body.append(dialog);
let directoryOpener=null;
function filterApps(){const q=search.value.toLowerCase().trim();let count=0;for(const n of list.children){n.hidden=!n.dataset.search.includes(q);if(!n.hidden)count++;}empty.hidden=count!==0;}
function openDirectory(opener,query=''){hideTip();directoryOpener=opener;search.value=query;filterApps();if(!dialog.open)dialog.showModal();search.focus();}
function closeDirectory(){dialog.close();hideTip();if(directoryOpener?.isConnected){directoryOpener.focus();hideTip();}}
close.addEventListener('click',closeDirectory);dialog.addEventListener('cancel',e=>{e.preventDefault();closeDirectory();});dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDirectory();}});search.addEventListener('input',filterApps);
dialog.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();closeDirectory();}});
d.addEventListener('keydown',e=>{if(e.key==='Escape')hideTip();});
function fitDesktop(){hideTip();const available=status.getBoundingClientRect().width-share.getBoundingClientRect().width-more.getBoundingClientRect().width-system.getBoundingClientRect().width-clock.getBoundingClientRect().width-9;const count=Math.max(0,Math.floor(available/26));[...menuApps.children].forEach((n,i)=>n.hidden=i>=count);const total=dockItems.children.length;const size=Math.max(23,Math.min(45,(innerWidth-72)/total-3));dock.style.setProperty('--dock-icon',size+'px');}
addEventListener('resize',fitDesktop);fitDesktop();
})();
