document.documentElement.classList.add('js');
const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}},{threshold:.08});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
document.querySelectorAll('[data-focus]').forEach(button=>button.addEventListener('click',()=>{
  const focus=button.dataset.focus;
  document.querySelectorAll('[data-focus]').forEach(el=>el.setAttribute('aria-pressed',String(el===button)));
  document.querySelectorAll('.response-block').forEach(el=>el.classList.toggle('deemphasized',focus!=='all' && el.dataset.kind!==focus));
  document.getElementById('focus-note').textContent=focus==='all'?'Showing the whole sample reply.':`Emphasising: ${button.textContent.replace(/^\S+\s/,'')}.`;
}));
document.getElementById('copy-install').onclick=async()=>{
  const status=document.getElementById('copy-status');
  try{await navigator.clipboard.writeText('git clone https://github.com/EthanSK/response-preferences.git ~/.codex/skills/response-preferences');status.textContent='Command copied';}
  catch{status.textContent='Could not copy. Select the command above to copy it.';}
};
