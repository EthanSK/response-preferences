import {basicSetup} from 'codemirror';
import {EditorState, StateField, StateEffect, Compartment, RangeSet} from '@codemirror/state';
import {EditorView, Decoration, GutterMarker, gutterLineClass, keymap, scrollPastEnd} from '@codemirror/view';
import {indentWithTab} from '@codemirror/commands';
import {openSearchPanel} from '@codemirror/search';
import {HighlightStyle, syntaxHighlighting, StreamLanguage} from '@codemirror/language';
import {tags} from '@lezer/highlight';
import {markdown} from '@codemirror/lang-markdown';
import {javascript} from '@codemirror/lang-javascript';
import {python} from '@codemirror/lang-python';
import {json} from '@codemirror/lang-json';
import {html} from '@codemirror/lang-html';
import {css} from '@codemirror/lang-css';
import {sql} from '@codemirror/lang-sql';
import {yaml} from '@codemirror/legacy-modes/mode/yaml';
import {shell} from '@codemirror/legacy-modes/mode/shell';
import {rust} from '@codemirror/legacy-modes/mode/rust';
import {go} from '@codemirror/legacy-modes/mode/go';
import {renderMarkdown, selectPassage} from './markdown.js';
import {decodeText, writeIfUnchanged} from './files.js';
import {resizeTables} from './table-resize.js';
import {installAppearance} from './theme.js';

const $ = id => document.getElementById(id);
const data = JSON.parse($('document-data').textContent);
const language = new Compartment();
const targetEffect = StateEffect.define();
const targetGutter = new class extends GutterMarker {elementClass = 'cm-target-gutter';}();
const selectedLine = StateField.define({
  create: () => Decoration.none,
  update(value, transaction) {
    value = value.map(transaction.changes);
    for (const effect of transaction.effects) if (effect.is(targetEffect)) value = Decoration.set([Decoration.line({class: 'cm-target-line'}).range(effect.value)]);
    return value;
  },
  provide: field => [EditorView.decorations.from(field), gutterLineClass.compute([field], state => {
    const target = state.field(field).iter();
    return target.value ? RangeSet.of([targetGutter.range(target.from)]) : RangeSet.empty;
  })]
});
// Class-based so viewer.css can theme tokens per light/dark palette alongside highlight.js fences.
const colours = HighlightStyle.define([
  {tag: [tags.keyword, tags.tagName, tags.modifier, tags.operatorKeyword], class: 'tok-keyword'},
  {tag: [tags.string, tags.special(tags.string), tags.attributeValue, tags.regexp], class: 'tok-string'},
  {tag: [tags.number, tags.bool, tags.null, tags.atom], class: 'tok-number'},
  {tag: tags.comment, class: 'tok-comment'},
  {tag: [tags.function(tags.variableName), tags.function(tags.propertyName), tags.definition(tags.variableName), tags.propertyName, tags.attributeName], class: 'tok-function'},
  {tag: [tags.typeName, tags.className], class: 'tok-type'},
  {tag: tags.heading, class: 'tok-heading'}, {tag: [tags.link, tags.url], class: 'tok-link'},
  {tag: tags.strong, class: 'tok-strong'}, {tag: tags.emphasis, class: 'tok-emphasis'},
  {tag: [tags.meta, tags.processingInstruction, tags.list, tags.contentSeparator], class: 'tok-meta'},
  {tag: tags.quote, class: 'tok-quote'}, {tag: tags.monospace, class: 'tok-code'}, {tag: tags.invalid, class: 'tok-invalid'}
]);
function modeFor(name) {
  const ext = name.split('.').pop().toLowerCase();
  const md = () => markdown({codeLanguages(info) {
    const label=info.trim().split(/\s+/)[0].toLowerCase();
    const aliases={javascript:'js',typescript:'ts',python:'py',shell:'sh',rust:'rs'};
    const suffix=aliases[label] || label;
    if(['md','markdown'].includes(suffix))return null;
    const support=modeFor('code.'+suffix);
    return Array.isArray(support)?null:support.language || support;
  }});
  const modes = {md, markdown:md, js: () => javascript(), mjs: () => javascript(), cjs: () => javascript(), jsx: () => javascript({jsx:true}), ts: () => javascript({typescript:true}), tsx: () => javascript({typescript:true,jsx:true}), py: python, json, html, htm:html, css, sql, yaml: () => StreamLanguage.define(yaml), yml: () => StreamLanguage.define(yaml), sh: () => StreamLanguage.define(shell), zsh: () => StreamLanguage.define(shell), bash: () => StreamLanguage.define(shell), rs: () => StreamLanguage.define(rust), go: () => StreamLanguage.define(go)};
  return modes[ext]?.() || [];
}
let name = data.name || 'document.md', baseline = data.source, rawBaseline = data.source, fileHandle = null, busy = false;
let live = data.live ? new URLSearchParams(location.search).get('doc') : null;
let liveRevision = null, externalChange = false, polling = false;
let images = data.images || {}, links = data.links || {}, currentMode = /\.(md|markdown)$/i.test(name) ? 'preview' : 'edit';
let targetLine = Number(data.line) || 1, renderTimer, sourceEol = data.source.includes('\r\n') ? '\r\n' : '\n', sourceBom = data.source.startsWith('\ufeff');
// Whole-file links have no selected passage. Only an explicit line/hash or Go
// action owns the yellow highlight; metadata is not a warning or special route.
let hasTarget = Number(data.line) > 0 || /^#L\d+$/.test(location.hash);
const normalise = text => text.replace(/^\ufeff/, '').replace(/\r\n?/g, '\n');
baseline = normalise(baseline);
function say(message) {$('status').textContent = message;}
function isDirty() {return editor.state.doc.toString() !== baseline;}
function updateDirty() {
  const writable = fileHandle || (live && liveRevision);
  const dirty = isDirty(); $('dirty').textContent = dirty ? 'Unsaved changes' : live ? 'Live file' : fileHandle ? 'File opened' : 'Snapshot';
  $('dirty').classList.toggle('unsaved', dirty); $('save').disabled = !writable || busy || !dirty;
  $('save').title = !writable ? 'Open a file with browser saving support first' : busy ? 'Saving…' : dirty ? 'Save changes to the opened file' : 'No unsaved changes';
}
const extensions = () => [
  basicSetup, keymap.of([indentWithTab, {key:'Mod-s', run:() => {(fileHandle || live) ? saveFile() : downloadFile(); return true;}}]),
  language.of(modeFor(name)), syntaxHighlighting(colours), selectedLine, scrollPastEnd(),
  EditorView.contentAttributes.of({'aria-label':'Document source'}),
  EditorView.updateListener.of(update => {if (update.docChanged) {updateDirty();clearTimeout(renderTimer);renderTimer=setTimeout(render,180);}})
];
const editor = new EditorView({parent:$('editor'), state:EditorState.create({doc:baseline, extensions:extensions()})});
const tableWidths = new Map();
let cleanupTableResize = () => {};
const passageObserver = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(positionPassageRail);
function positionPassageRail() {
  const preview = $('preview'), passage = preview.querySelector('.selected');
  let rail = preview.querySelector('#passage-rail');
  if (!passage) {rail?.remove();return;}
  // The rail stays outside content and overflow wrappers without changing layout.
  const target = passage.closest('.table-scroll') || passage;
  const box = target.getBoundingClientRect(), pane = preview.getBoundingClientRect();
  if (!rail) {rail=document.createElement('div');rail.id='passage-rail';rail.setAttribute('aria-hidden','true');preview.append(rail);}
  rail.style.left=`${parseFloat(getComputedStyle(preview).paddingLeft)-10}px`;
  rail.style.top=`${box.top-pane.top+preview.scrollTop}px`;
  rail.style.height=`${Math.max(2,box.height)}px`;
}
function render() {
  passageObserver?.disconnect();
  cleanupTableResize();
  if (/\.(md|markdown)$/i.test(name)) $('preview').innerHTML = renderMarkdown(editor.state.doc.toString(), {images,links,live:!!live});
  else {const pre=document.createElement('pre');pre.textContent=editor.state.doc.toString();$('preview').replaceChildren(pre);}
  cleanupTableResize = resizeTables($('preview'), tableWidths);
  $('line').max=editor.state.doc.lines;
}
function jump(value, fromHash = false) {
  const line=Number(value), total=editor.state.doc.lines;
  if (!Number.isInteger(line) || line<1 || line>total) {say(`Enter a line from 1 to ${total}.`);return;}
  hasTarget=true;targetLine=line;$('line').value=line;
  if(!fromHash) {try {history.replaceState(null,'','#L'+line);} catch { /* file viewers can disable history */ }}
  const pos=editor.state.doc.line(line).from;
  editor.dispatch({effects:[targetEffect.of(pos),EditorView.scrollIntoView(pos,{y:'center'})],selection:{anchor:pos}});
  $('preview').querySelectorAll('.selected').forEach(el=>el.classList.remove('selected'));
  const passage=selectPassage($('preview'),line);
  if(passage) {
    passage.classList.add('selected');positionPassageRail();
    passageObserver?.disconnect();passageObserver?.observe($('preview'));passageObserver?.observe(passage);
    if(currentMode!=='edit') requestAnimationFrame(()=>{passage.scrollIntoView({block:'center',behavior:'instant'});positionPassageRail();});
  }
  say(`Line ${line}${passage && currentMode!=='edit' ? ` · passage spans lines ${passage.dataset.start}–${passage.dataset.end}` : ''}`);
}
function setMode(mode) {
  currentMode=mode;$('workspace').dataset.mode=mode;
  document.querySelectorAll('[data-mode]').forEach(el=>{if(el.tagName==='BUTTON')el.setAttribute('aria-pressed',String(el.dataset.mode===mode));});
  render();requestAnimationFrame(()=>{editor.requestMeasure();if(hasTarget)jump(Math.min(targetLine,editor.state.doc.lines),true);});
}
function confirmDiscard() {return !isDirty() || confirm('You have unsaved changes that opening another file will discard.');}
async function loadFile(file, handle=null) {
  if(file.size>5*1024*1024) throw Error('This file is larger than 5 MB. Open a smaller text file.');
  const text=decodeText(await file.arrayBuffer());
  name=file.name;rawBaseline=text;baseline=normalise(text);sourceEol=text.includes('\r\n')?'\r\n':'\n';sourceBom=text.startsWith('\ufeff');
  live=null;hasTarget=false;fileHandle=handle;images={};links={};tableWidths.clear();$('reload').hidden=true;
  editor.setState(EditorState.create({doc:baseline,extensions:extensions()}));
  $('filename').textContent=name;$('filename').title=name;$('file-note').textContent='Opened from disk · does not update automatically';
  $('snapshot-note').textContent=handle?'Save writes to the file you picked. Download copy creates a separate file.':'Download copy to keep your edits. The file you opened is unchanged.';
  targetLine=1;setMode(/\.(md|markdown)$/i.test(name)?'preview':'edit');updateDirty();
}
async function openFile() {
  if(busy || !confirmDiscard()) return;
  if(!window.showOpenFilePicker) {$('file-input').click();return;}
  try {const [handle]=await window.showOpenFilePicker({multiple:false});await loadFile(await handle.getFile(),handle);}
  catch(error) {if(error.name!=='AbortError') say('Could not open this file. '+error.message);}
}
function outputText() {return (sourceBom?'\ufeff':'') + editor.state.doc.toString().replace(/\n/g,sourceEol);}
async function saveFile() {
  if((!fileHandle && !live) || busy || !isDirty()) return;
  busy=true;updateDirty();say('Saving...');
  try {
    // Capture the revision being saved: edits made during the write stay marked unsaved.
    const savedRevision=editor.state.doc.toString(), savedText=outputText();
    if(live) {
      const response=await fetch('/api/document?doc='+encodeURIComponent(live),{method:'POST',headers:{'Content-Type':'application/json','X-Viewer-Document':live},body:JSON.stringify({source:savedText,revision:liveRevision})});
      const result=await response.json();if(!response.ok)throw Error(result.error || 'Could not save this file.');
      liveRevision=result.revision;externalChange=false;
    } else await writeIfUnchanged(fileHandle,rawBaseline,savedText);
    rawBaseline=savedText;baseline=savedRevision;say('Saved');
  } catch(error) {say('Failed to save. '+error.message);}
  finally {busy=false;updateDirty();}
}
async function refreshLive(force=false) {
  if(!live || polling || busy)return;
  polling=true;
  try {
    const response=await fetch('/api/document?doc='+encodeURIComponent(live),{headers:!force && liveRevision?{'If-None-Match':'"'+liveRevision+'"'}:{},cache:'no-store'});
    if(response.status===304)return;
    const next=await response.json();if(!response.ok)throw Error(next.error || 'Could not open this file.');
    if(busy)return;
    if(isDirty() && !force) {
      externalChange=true;say('This file changed somewhere else. Download your edits, then reload the file.');return;
    }
    const first=liveRevision===null;
    if(first)targetLine=Number(location.hash.match(/^#L(\d+)$/)?.[1] || data.line) || 1;
    name=next.name;rawBaseline=next.source;baseline=normalise(next.source);liveRevision=next.revision;externalChange=false;
    sourceEol=next.source.includes('\r\n')?'\r\n':'\n';sourceBom=next.source.startsWith('\ufeff');images=next.images;links=next.links;
    editor.setState(EditorState.create({doc:baseline,extensions:extensions()}));
    $('filename').textContent=name;$('filename').title=next.path;$('file-note').textContent=next.path;
    $('snapshot-note').textContent='Live file · Save writes to the original file.';
    document.title=name+' · Live file viewer';
    if(first && next.appearance)installAppearance(document.documentElement,$('theme'),next.appearance);
    if(first)currentMode=/\.(md|markdown)$/i.test(name)?'preview':'edit';
    setMode(currentMode);updateDirty();if(!hasTarget)say('File opened');
  } catch(error) {say('Could not read the original file. '+error.message);}
  finally {polling=false;}
}
function downloadFile() {
  const url=URL.createObjectURL(new Blob([outputText()],{type:'text/plain;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  say('Download started. The file you opened is unchanged.');
}
$('filename').textContent=name;$('filename').title=name;$('file-note').textContent=data.generated?`Snapshot · ${data.generated}`:'Local document';
document.querySelectorAll('button[data-mode]').forEach(button=>button.onclick=()=>setMode(button.dataset.mode));
$('jump-form').onsubmit=event=>{event.preventDefault();jump($('line').value);};
$('search').onclick=()=>{if(currentMode==='preview')setMode('edit');openSearchPanel(editor);editor.focus();};
$('open').onclick=openFile;$('save').onclick=saveFile;$('download').onclick=downloadFile;
$('reload').hidden=!live;
$('reload').onclick=()=>{if(!isDirty() || confirm('Reload file and discard your unsaved changes?'))refreshLive(true);};
$('file-input').onchange=async()=>{const file=$('file-input').files[0];if(file)try{await loadFile(file);}catch(error){say('Could not open this file. '+error.message);}finally{$('file-input').value='';}};
installAppearance(document.documentElement, $('theme'), data.appearance);
$('preview').onclick=event=>{const unavailable=event.target.closest('[data-unavailable]');if(unavailable){event.preventDefault();say('Open the linked file from disk. It is not included in this viewer.');}};
$('preview').addEventListener('load',positionPassageRail,true);
$('preview').addEventListener('toggle',positionPassageRail,true);
addEventListener('resize',positionPassageRail);
document.fonts?.ready.then(positionPassageRail);
addEventListener('beforeunload',event=>{if(isDirty()){event.preventDefault();event.returnValue='';}});
addEventListener('hashchange',()=>{const match=location.hash.match(/^#L(\d+)$/);if(match)jump(+match[1],true);});
const hash=location.hash.match(/^#L(\d+)$/);if(hash)targetLine=+hash[1];
targetLine=Math.min(Math.max(targetLine,1),editor.state.doc.lines);render();setMode(currentMode);updateDirty();
if(data.live) {
  if(!live)say('No file selected. Open a live file link.');
  else {refreshLive();setInterval(()=>{if(!document.hidden)refreshLive();},1500);addEventListener('focus',()=>refreshLive());}
}
