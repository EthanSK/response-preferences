import {build} from 'esbuild';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const result=await build({entryPoints:[path.join(root,'src/editor.js')],bundle:true,minify:true,write:false,format:'iife',target:'es2022',legalComments:'inline'});
const script=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const style=fs.readFileSync(path.join(root,'src/viewer.css'),'utf8');
// A replacement function keeps library strings such as $& and $` literal.
const template=fs.readFileSync(path.join(root,'src/viewer.html'),'utf8').replace('__STYLE__',()=>style).replace('__SCRIPT__',()=>script);
fs.mkdirSync(path.join(root,'assets'),{recursive:true});
fs.writeFileSync(path.join(root,'assets/viewer.html'),template);
console.log(`Built standalone viewer template (${Buffer.byteLength(template)} bytes)`);
