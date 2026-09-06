import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js/lib/common';

export function renderMarkdown(source, {images = {}, links = {}} = {}) {
  const md = new MarkdownIt({html: false, linkify: false, typographer: false, highlight(code, language) {
    return language && hljs.getLanguage(language) ? hljs.highlight(code, {language}).value : '';
  }});
  md.block.ruler.before('hr','front_matter',(state,start,end,silent)=>{
    if(start!==0 || state.src.slice(state.bMarks[0],state.eMarks[0]).trim()!=='---')return false;
    let stop=1;while(stop<end && state.src.slice(state.bMarks[stop],state.eMarks[stop]).trim()!=='---')stop++;
    if(stop===end)return false;
    if(silent)return true;
    const token=state.push('front_matter','',0);token.map=[0,stop+1];token.content=state.getLines(1,stop,0,false);state.line=stop+1;return true;
  });
  md.renderer.rules.front_matter=(tokens,index)=>`<details class="passage" data-start="1" data-end="${tokens[index].map[1]}"><summary>Skill metadata</summary><pre><code>${hljs.highlight(tokens[index].content,{language:'yaml'}).value}</code></pre></details>`;
  // Source maps come from the parser, including repeated and nested list items.
  md.core.ruler.push('source_lines', state => {
    const names = new Map();
    for (let i = 0; i < state.tokens.length; i++) {
      const token = state.tokens[i];
      if (token.map && (token.nesting === 1 || ['fence', 'code_block', 'hr'].includes(token.type))) {
        token.attrSet('data-start', String(token.map[0] + 1));
        token.attrSet('data-end', String(token.map[1]));
        token.attrJoin('class', 'passage');
      }
      if (token.type === 'heading_open') {
        const text = state.tokens[i + 1]?.content || '';
        const base = text.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, '').trim().replace(/\s+/g, '-');
        const count = names.get(base) || 0; names.set(base, count + 1);
        token.attrSet('id', base + (count ? '-' + count : ''));
      }
    }
  });
  md.renderer.rules.image = (tokens, index) => {
    const token = tokens[index], href = token.attrGet('src');
    const alt = md.utils.escapeHtml(token.content);
    // Only generator-embedded raster images. No remote tracking or arbitrary data URLs.
    const embedded = Object.hasOwn(images, href) && images[href];
    if (!embedded || !/^data:image\/(png|jpeg|gif|webp);base64,[A-Za-z0-9+/]*={0,2}$/.test(embedded)) return `<span class="image-note">${alt || 'Image'} (not included)</span>`;
    return `<img src="${embedded}" alt="${alt}" loading="lazy">`;
  };
  const fence = md.renderer.rules.fence;
  md.renderer.rules.fence = (tokens, index, options, env, self) => {
    const t = tokens[index];
    return `<div class="passage code-block" data-start="${t.map[0]+1}" data-end="${t.map[1]}">${fence(tokens,index,options,env,self)}</div>`;
  };
  const open = md.renderer.rules.link_open || ((tokens,index,options,env,self) => self.renderToken(tokens,index,options));
  md.renderer.rules.link_open = (tokens,index,options,env,self) => {
    const t = tokens[index], href = t.attrGet('href');
    const resolved = Object.hasOwn(links, href) ? links[href] : href;
    if (/^(https?:|mailto:|#)/i.test(resolved || '')) t.attrSet('href', resolved);
    else if (/^file:/i.test(resolved || '') && Object.hasOwn(links, href)) t.attrSet('href', resolved);
    else {t.attrSet('href', '#');t.attrSet('data-unavailable', 'true');}
    t.attrSet('rel', 'noopener noreferrer');
    return open(tokens,index,options,env,self);
  };
  return md.render(source);
}

export function selectPassage(root, line) {
  const candidates = [...root.querySelectorAll('[data-start]')];
  return candidates.filter(el => +el.dataset.start <= line && +el.dataset.end >= line)
    .sort((a,b) => (+a.dataset.end - +a.dataset.start) - (+b.dataset.end - +b.dataset.start) || (a.contains(b) ? 1 : -1))[0]
    || candidates.find(el => +el.dataset.start >= line) || candidates.at(-1);
}
