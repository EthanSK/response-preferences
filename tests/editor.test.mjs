import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {JSDOM,VirtualConsole} from 'jsdom';

test('bundled editor boots, changes views, jumps to line and opens search without a browser',async()=>{
  const template=fs.readFileSync(new URL('../assets/viewer.html',import.meta.url),'utf8');
  const page=template.replace('__DOCUMENT__',JSON.stringify({name:'example.md',source:'# Heading\n\n- first\n- second\n',line:4,images:{},links:{}}));
  const errors=[];const virtualConsole=new VirtualConsole();virtualConsole.on('jsdomError',error=>errors.push(error.message));
  const dom=new JSDOM(page,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://example.invalid/viewer.html',virtualConsole,beforeParse(window){
    window.TextDecoder=TextDecoder;window.TextEncoder=TextEncoder;
    window.Range.prototype.getClientRects=()=>[];
    window.Range.prototype.getBoundingClientRect=()=>({top:0,left:0,right:0,bottom:0,width:0,height:0});
    window.HTMLElement.prototype.scrollIntoView=()=>{};
    window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
  }});
  try {
    await new Promise(resolve=>setTimeout(resolve,100));
    const d=dom.window.document;
    assert.deepEqual(errors,[]);
    assert.equal(d.querySelector('#filename').textContent,'example.md');
    assert.equal(d.querySelector('.selected').textContent.trim(),'second');
    assert.equal(d.querySelector('#save').disabled,true);
    d.querySelector('button[data-mode="edit"]').click();
    await new Promise(resolve=>setTimeout(resolve,30));
    assert.equal(d.querySelector('#workspace').dataset.mode,'edit');
    assert.ok(d.querySelector('.cm-editor .cm-content'));
    d.querySelector('#line').value='1';d.querySelector('#jump-form').dispatchEvent(new dom.window.Event('submit',{cancelable:true}));
    assert.equal(dom.window.location.hash,'#L1');
    d.querySelector('#search').click();assert.ok(d.querySelector('.cm-search'));
    assert.deepEqual(errors,[]);
  } finally {dom.window.close();}
});
