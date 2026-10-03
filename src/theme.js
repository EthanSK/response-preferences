// Generated documents carry only whitelisted appearance values, never the config itself.
const hex = /^#[0-9a-f]{6}$/i;
const fonts = /^[\w ,"'.-]{1,200}$/u;
function mix(a, b, amount) {
  const rgb = value => [1,3,5].map(i => parseInt(value.slice(i,i+2),16));
  return '#' + rgb(a).map((v,i) => Math.round(v+(rgb(b)[i]-v)*amount).toString(16).padStart(2,'0')).join('');
}
function alpha(color, opacity) {
  return `rgba(${[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)).join(',')},${opacity})`;
}
export function installAppearance(root, toggle, appearance = {}) {
  const media = typeof matchMedia === 'function' ? matchMedia('(prefers-color-scheme: light)') : null;
  let followSystem = !['light','dark'].includes(appearance.mode);
  function apply(mode) {
    root.dataset.theme = mode;
    // Clear the previous palette so the light/dark defaults can take over.
    for (const name of ['bg','chrome','panel','panel-strong','line','line-strong','text','muted','accent','link','accent-soft','accent-strong','selection','ui','mono','code','code-text']) root.style.removeProperty('--'+name);
    const theme = appearance[mode];
    if (theme && ['surface','ink','accent'].every(k=>hex.test(theme[k]))) {
      const {surface,ink,accent} = theme;
      const strength = typeof theme.contrast==='number' ? Math.min(100,Math.max(0,theme.contrast))/50 : 1;
      const values = {
        bg:surface,text:ink,accent,link:mode==='dark'?mix(accent,ink,.4):accent,
        chrome:mix(surface,ink,.06*strength),panel:mix(surface,ink,.12*strength),
        'panel-strong':mix(surface,ink,.19*strength),line:mix(surface,ink,.13*strength),
        'line-strong':mix(surface,ink,.25*strength),muted:mix(surface,ink,.6),
        'accent-soft':alpha(accent,.18),'accent-strong':alpha(accent,.4),selection:alpha(accent,.28)
      };
      if (fonts.test(theme.ui || '')) values.ui=theme.ui+',Inter,-apple-system,BlinkMacSystemFont,sans-serif';
      if (fonts.test(theme.code || '')) values.mono=theme.code+',ui-monospace,Menlo,monospace';
      for (const [key,value] of Object.entries(values)) root.style.setProperty('--'+key,value);
      // Retain Linear's distinct code surface; other chrome seeds use a quiet inset.
      if (theme.codeThemeId !== 'linear') {
        root.style.setProperty('--code',mix(surface,ink,.035));
        root.style.setProperty('--code-text',ink);
      }
    }
  }
  const systemMode=()=>media?.matches?'light':'dark';
  apply(followSystem?systemMode():appearance.mode);
  media?.addEventListener?.('change',()=>{if(followSystem)apply(systemMode());});
  toggle.onclick=()=>{followSystem=false;apply(root.dataset.theme==='light'?'dark':'light');};
}
