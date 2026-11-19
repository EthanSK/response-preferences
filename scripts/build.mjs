// Bundle the shared viewer and regenerate its standalone template and public examples.
import {build} from 'esbuild';
import {viewerIcon} from '../src/viewer-icons.js';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
await build({entryPoints:[path.join(root,'src/render-math.js')],bundle:true,minify:true,platform:'node',format:'cjs',target:'node18',outfile:path.join(root,'scripts/render-math.cjs'),legalComments:'inline'});
fs.copyFileSync(path.join(root,'node_modules/katex/LICENSE'), path.join(root,'assets/katex-LICENSE.txt'));
const result=await build({entryPoints:[path.join(root,'src/editor.js')],bundle:true,minify:true,write:false,format:'iife',target:'es2022',legalComments:'inline'});
const script=result.outputFiles[0].text.replace(/<\/script/gi,'<\\/script');
const font=fs.readFileSync(path.join(root,'assets/InterVariable.woff2')).toString('base64');
const fontLicense=fs.readFileSync(path.join(root,'assets/Inter-LICENSE.txt'),'utf8');
const katexDistribution = path.join(root, 'node_modules/katex/dist');
// Inline WOFF2 fonts so the live viewer and standalone export both work under the existing offline policy.
const latexStyle = fs.readFileSync(path.join(katexDistribution, 'katex.min.css'), 'utf8')
  .replace(/url\(fonts\/([^)]+\.woff2)\)[^;}]+/g, (_, name) => {
    const fontData = fs.readFileSync(path.join(katexDistribution, 'fonts', name)).toString('base64');
    return `url(data:font/woff2;base64,${fontData}) format("woff2")`;
  });
if (latexStyle.includes('url(fonts/')) throw Error('KaTeX still references external font files');
const style=`/* ${fontLicense} */\n@font-face{font-family:Inter;font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,${font}) format('woff2')}\n`+latexStyle+'\n'+fs.readFileSync(path.join(root,'src/viewer.css'),'utf8');
// A replacement function keeps library strings such as $& and $` literal.
const template=fs.readFileSync(path.join(root,'src/viewer.html'),'utf8').replace('__FAVICON__',()=>viewerIcon('document.txt')).replace('__STYLE__',()=>style).replace('__SCRIPT__',()=>script);
fs.mkdirSync(path.join(root,'assets'),{recursive:true});
fs.writeFileSync(path.join(root,'assets/viewer.html'),template);
console.log(`Built standalone viewer template (${Buffer.byteLength(template)} bytes)`);
// Public demos are explicit exports of synthetic/canonical sources. Build them
// together so publishing never depends on an agent remembering another step.
execFileSync('python3',[path.join(root,'scripts/build-demos.py')],{stdio:'inherit'});
