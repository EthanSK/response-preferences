import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {JSDOM} from 'jsdom';
function boot(width=1680){
 const dom=new JSDOM('<!doctype html><body><div class="app">Existing guide</div></body>',{url:'https://example.test/response-preferences/',runScripts:'outside-only'}),w=dom.window;
 Object.defineProperty(w,'innerWidth',{value:width,writable:true});
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
 for(const file of ['desktop-data.js','desktop.js'])w.eval(readFileSync('docs/'+file,'utf8'));
 return dom;
}
test('desktop keeps every real app reachable with correct public links and no local paths',()=>{
 const dom=boot(),d=dom.window.document,data=dom.window.DESKTOP_APPS;
 assert.equal(data.length,47);assert.equal(d.querySelectorAll('.desktop-app-card').length,data.length);
 assert.equal(d.querySelectorAll('.mac-dock [data-app-id]').length,38);
 assert.equal(d.querySelector('.mac-dock [data-app-id]').dataset.appId,'finder');
 assert.equal(d.querySelectorAll('.mac-menu-app').length,27);
 for(const a of d.querySelectorAll('a[target="_blank"]')){
  assert.match(a.rel,/noopener/);assert.match(a.rel,/noreferrer/);assert.match(a.href,/^https:\/\/|^https:\/\/example.test\//);
 }
 for(const a of data){assert(existsSync('docs/'+a.icon));assert(!JSON.stringify(a).includes('/Users/'));if(a.url)assert.match(a.url,/^https:\/\//);}
 const source=readFileSync('docs/desktop-data.js','utf8');assert(!/file:\/\/|\/Users\/|token=|api[_-]?key/i.test(source));
 for(const a of d.querySelectorAll('.mac-menu-app'))assert.equal(a.href,'https://www.menubardock.com/');
 assert.equal(d.querySelectorAll('.dock-folder').length,0);
 assert.equal(d.querySelector('.desktop-app-list [data-app-id="aiwallpaper"]').href,'https://www.aiwallpapergenerator.ai/');
 assert.equal(d.querySelector('[data-app-id="menu-bar-dock"]').href,'https://www.menubardock.com/');
 dom.window.close();
});
test('overflow menu searches shareable apps and restores focus',()=>{
 const dom=boot(390),w=dom.window,d=w.document;
 assert([...d.querySelectorAll('.mac-menu-app')].some(n=>n.hidden));
 const opener=d.querySelector('.mac-more-apps');opener.click();assert(d.querySelector('dialog').open);
 const input=d.querySelector('input');input.value='wallpaper';input.dispatchEvent(new w.Event('input'));
 assert.equal(d.querySelectorAll('.desktop-app-card:not([hidden])').length,1);
 input.value='no matching application';input.dispatchEvent(new w.Event('input'));assert.equal(d.querySelector('.desktop-no-apps').hidden,false);
 input.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
 assert.equal(d.querySelector('dialog').open,false);assert.equal(d.activeElement,opener);assert.equal(d.querySelector('.desktop-tooltip').hidden,true);
 dom.window.close();
});
test('tooltips follow keyboard focus and resize hides stale hover content',()=>{
 const dom=boot(),d=dom.window.document,w=dom.window;
 const link=d.querySelector('.mac-dock [data-app-id="google-chrome"]');link.focus();
 assert.equal(d.querySelector('.desktop-tooltip').hidden,false);assert.match(d.querySelector('.desktop-tooltip').textContent,/Google ChromeOpen website in new tab/);
 w.innerWidth=390;w.dispatchEvent(new w.Event('resize'));assert.equal(d.querySelector('.desktop-tooltip').hidden,true);
 assert.equal(d.querySelectorAll('.desktop-system-guides a').length,7);
 dom.window.close();
});
