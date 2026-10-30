// Tutorial assistant: a chat panel that talks to the backend's /chat endpoint (Claude).
// The API key lives on the backend; this file only sends the conversation and what is on screen.
(() => {
  const configEl = document.getElementById('ita-chat-config');
  const root = document.querySelector('[data-chat]');
  if (!configEl || !root) return;

  const config = JSON.parse(configEl.textContent);
  const apiUrls = (config.apiUrls || []).map((url) => String(url).replace(/\/$/, '')).filter(Boolean);
  const panel = root.querySelector('[data-chat-panel]');
  const openButton = root.querySelector('[data-chat-open]');
  const closeButton = root.querySelector('[data-chat-close]');
  const clearButton = root.querySelector('[data-chat-clear]');
  const log = root.querySelector('[data-chat-log]');
  const form = root.querySelector('[data-chat-form]');
  const input = root.querySelector('[data-chat-input]');
  const sendButton = root.querySelector('[data-chat-send]');
  const contextEl = root.querySelector('[data-chat-context]');
  const contextToggle = root.querySelector('[data-chat-context-toggle]');
  const statusEl = root.querySelector('[data-chat-status]');

  const storageKey = 'ita:chat:history';
  let history = [];
  try { history = JSON.parse(sessionStorage.getItem(storageKey) || '[]'); } catch (_) { history = []; }
  const save = () => { try { sessionStorage.setItem(storageKey, JSON.stringify(history.slice(-30))); } catch (_) { /* storage blocked */ } };

  let tabId = '';
  try { tabId = sessionStorage.getItem('browser-notebook:tab-session-id') || ''; } catch (_) { /* storage blocked */ }
  if (!tabId) tabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

  // ---- markdown (small, escape-first) ------------------------------------------------------

  const escapeHtml = (text) => text.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const inline = (text) => escapeHtml(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>')
    .replace(/(^|\W)_([^_\s][^_]*)_(?=\W|$)/g, '$1<em>$2</em>');
  const renderMarkdown = (source) => {
    const html = [];
    const blocks = source.split(/```/);
    blocks.forEach((block, index) => {
      if (index % 2 === 1) {
        html.push(`<pre><code>${escapeHtml(block.replace(/^[\w-]*\n/, '').replace(/\n$/, ''))}</code></pre>`);
        return;
      }
      block.split(/\n{2,}/).forEach((chunk) => {
        const lines = chunk.split('\n').filter((line) => line.trim());
        if (!lines.length) return;
        if (lines.every((line) => /^\s*([-*]|\d+[.)])\s+/.test(line))) {
          const ordered = /^\s*\d/.test(lines[0]);
          const items = lines.map((line) => `<li>${inline(line.replace(/^\s*([-*]|\d+[.)])\s+/, ''))}</li>`).join('');
          html.push(ordered ? `<ol>${items}</ol>` : `<ul>${items}</ul>`);
        } else if (/^#{1,4}\s/.test(lines[0]) && lines.length === 1) {
          html.push(`<p><strong>${inline(lines[0].replace(/^#+\s*/, ''))}</strong></p>`);
        } else {
          html.push(`<p>${lines.map(inline).join('<br>')}</p>`);
        }
      });
    });
    return html.join('');
  };

  // ---- page context ---------------------------------------------------------------------

  const focusedTask = () => {
    const tasks = Array.from(document.querySelectorAll('[data-task]'));
    if (!tasks.length) return null;
    const middle = innerHeight / 2;
    let best = null;
    let bestDistance = Infinity;
    tasks.forEach((task) => {
      const rect = task.getBoundingClientRect();
      const distance = rect.top > middle ? rect.top - middle : rect.bottom < middle ? middle - rect.bottom : 0;
      if (distance < bestDistance) { best = task; bestDistance = distance; }
    });
    return bestDistance < innerHeight ? best : null;
  };

  const pageContext = () => {
    const title = document.querySelector('.ita-title, .ita-hero__title')?.textContent.trim() || document.title;
    const context = { page: `${title} (${location.pathname})`, page_path: location.pathname };
    const task = focusedTask();
    if (task) {
      const number = task.querySelector('.ita-task__num')?.textContent.trim();
      context.task = `${number} · ${task.querySelector('.ita-task__title')?.textContent.trim()}`;
      context.question = task.querySelector('[data-question]')?.textContent.trim() || '';
      const editor = task.querySelector('.CodeMirror')?.CodeMirror;
      context.code = editor ? editor.getValue() : task.querySelector('[data-editor] textarea')?.value || '';
      const output = task.querySelector('[data-output]');
      if (output && !output.hidden) {
        const text = Array.from(output.querySelectorAll('pre, .ita-output__html')).map((el) => el.innerText.trim()).join('\n').slice(0, 2500);
        const figures = output.querySelectorAll('img').length;
        context.output = text + (figures ? `\n[${figures} gráfico(s) na saída]` : '');
      }
      context.analysis = task.querySelector('[data-response]')?.value.trim() || '';
    }
    return context;
  };

  let includeContext = true;
  const describeContext = () => {
    const task = focusedTask();
    const label = task
      ? `${task.querySelector('.ita-task__num')?.textContent.trim()} · ${task.querySelector('.ita-task__title')?.textContent.trim()}`
      : (document.querySelector('.ita-title, .ita-hero__title')?.textContent.trim() || 'esta página');
    contextEl.textContent = includeContext ? `Contexto: ${label}` : 'Sem contexto da página';
    contextToggle.textContent = includeContext ? 'Remover' : 'Incluir';
  };
  contextToggle.addEventListener('click', () => { includeContext = !includeContext; describeContext(); });

  // ---- rendering ------------------------------------------------------------------------

  const addBubble = (role, text) => {
    const bubble = document.createElement('div');
    bubble.className = `ita-chat__msg ita-chat__msg--${role}`;
    if (role === 'assistant') bubble.innerHTML = renderMarkdown(text); else bubble.textContent = text;
    log.append(bubble);
    log.scrollTop = log.scrollHeight;
    return bubble;
  };
  const renderHistory = () => {
    log.querySelectorAll('.ita-chat__msg').forEach((el) => el.remove());
    history.forEach((message) => addBubble(message.role, message.content));
  };

  // ---- backend --------------------------------------------------------------------------

  let available = null;
  const checkAvailable = async () => {
    if (available !== null) return available;
    for (const base of apiUrls) {
      try {
        const response = await fetch(`${base}/health`);
        const health = await response.json();
        if (health.chat_enabled) { available = base; return available; }
      } catch (_) { /* try the next one */ }
    }
    available = false;
    return available;
  };

  const setStatus = (text) => { statusEl.textContent = text; statusEl.hidden = !text; };

  let busy = false;
  const send = async (text) => {
    if (busy || !text.trim()) return;
    const base = await checkAvailable();
    if (!base) {
      setStatus('O assistente ainda não está disponível. Avise o instrutor.');
      input.value = text;
      return;
    }
    busy = true;
    sendButton.disabled = true;
    setStatus('');
    history.push({ role: 'user', content: text.trim() });
    const userBubble = addBubble('user', text.trim());
    save();
    const bubble = addBubble('assistant', '');
    bubble.classList.add('is-pending');
    let answer = '';
    try {
      const response = await fetch(`${base}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: tabId, messages: history, context: includeContext ? pageContext() : null }),
      });
      if (!response.ok || !response.body) {
        let message = `Erro ${response.status}`;
        try { message = (await response.json()).error || message; } catch (_) { /* not JSON */ }
        throw new Error(message);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let failed = '';
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop();
        for (const raw of events) {
          if (!raw.startsWith('data: ')) continue;
          const event = JSON.parse(raw.slice(6));
          if (event.type === 'text') {
            answer += event.text;
            bubble.classList.remove('is-pending');
            bubble.innerHTML = renderMarkdown(answer);
            log.scrollTop = log.scrollHeight;
          } else if (event.type === 'error') {
            failed = event.error;
          }
        }
      }
      if (failed && !answer) throw new Error(failed);
      if (failed) setStatus(failed);
      history.push({ role: 'assistant', content: answer });
      save();
    } catch (error) {
      bubble.remove();
      history.pop();  // drop the unanswered question so the conversation stays valid
      save();
      userBubble.remove();
      input.value = text;
      setStatus(error.message || String(error));
    } finally {
      busy = false;
      sendButton.disabled = false;
    }
  };

  // ---- panel ----------------------------------------------------------------------------

  const open = () => {
    root.classList.add('is-open');
    panel.hidden = false;
    openButton.setAttribute('aria-expanded', 'true');
    describeContext();
    checkAvailable().then((base) => { if (!base) setStatus('O assistente ainda não está disponível. Avise o instrutor.'); });
    setTimeout(() => input.focus(), 50);
  };
  const close = () => {
    root.classList.remove('is-open');
    panel.hidden = true;
    openButton.setAttribute('aria-expanded', 'false');
    openButton.focus();
  };
  openButton.addEventListener('click', () => (panel.hidden ? open() : close()));
  closeButton.addEventListener('click', close);
  clearButton.addEventListener('click', () => { history = []; save(); renderHistory(); setStatus(''); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !panel.hidden) close(); });
  addEventListener('scroll', () => { if (!panel.hidden) describeContext(); }, { passive: true });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = input.value;
    input.value = '';
    send(text);
  });
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
  });
  root.querySelectorAll('[data-chat-suggestion]').forEach((button) => {
    button.addEventListener('click', () => send(button.textContent.trim()));
  });

  renderHistory();
})();
