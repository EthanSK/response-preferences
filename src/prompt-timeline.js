// Render an Agent Flow archive's ordered captures inside the shared file viewer.
const eventLabels = {
  speech: 'Speech', speech_segment: 'Speech', typed_text: 'Typed text',
  potential_tts: 'Possible playback', codex_selection: 'Selection', app_selection: 'Selection',
  local_screenshot: 'Screenshot', app_selection_image: 'Selection image',
};
const authored = new Set(['speech', 'speech_segment', 'typed_text', 'potential_tts']);
const imageKinds = new Set(['local_screenshot', 'app_selection_image']);

export function renderPromptTimeline({events, rainbow, guidance = []}, query) {
  const timeline = document.createElement('div');
  timeline.className = 'prompt-timeline';
  let word = rainbow;
  for (const [index, event] of events.entries()) {
    const card = document.createElement('section');
    card.className = 'prompt-event';
    card.dataset.kind = event.kind;
    const label = eventLabels[event.kind];
    if (label) {
      const heading = document.createElement('h2');
      heading.textContent = [label, event.attributes.source].filter(Boolean).join(' · ');
      card.append(heading);
    }
    const body = document.createElement('div');
    body.className = 'prompt-payload';
    if (imageKinds.has(event.kind)) {
      const preview = document.createElement('img');
      preview.alt = label;
      preview.loading = 'lazy';
      preview.addEventListener('error', () => {
        preview.replaceWith(document.createTextNode(event.attributes.path || 'Image unavailable.'));
      }, {once: true});
      preview.src = '/api/prompt-image?' + query + '&event=' + index;
      body.append(preview);
    } else if (authored.has(event.kind)) {
      for (const part of event.text.trim().split(/(\s+)/u)) {
        if (!part || /^\s+$/u.test(part)) {
          body.append(part);
          continue;
        }
        const span = document.createElement('span');
        span.style.setProperty('--word-hue', String((word++ % 24) * 15));
        span.textContent = part;
        body.append(span);
      }
    } else {
      body.textContent = event.text;
    }
    card.append(body);
    if (Object.keys(event.attributes).length) {
      const details = document.createElement('details');
      details.className = 'prompt-metadata';
      const summary = document.createElement('summary');
      summary.textContent = 'Details';
      const list = document.createElement('dl');
      for (const [key, value] of Object.entries(event.attributes)) {
        const term = document.createElement('dt');
        const description = document.createElement('dd');
        term.textContent = key;
        description.textContent = value;
        list.append(term, description);
      }
      details.append(summary, list);
      card.append(details);
    }
    timeline.append(card);
  }
  if (guidance.length) {
    const sections = document.createElement('section');
    sections.className = 'prompt-guidance';
    sections.setAttribute('aria-label', 'Prompt guidance');
    for (const {label, text} of guidance) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = label;
      const body = document.createElement('pre');
      body.textContent = text;
      details.append(summary, body);
      sections.append(details);
    }
    timeline.append(sections);
  }
  return timeline;
}
