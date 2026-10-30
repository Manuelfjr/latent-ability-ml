// Hands-on runtime for the ITA tutorial pages.
// Runs task cells on the Python backend when it is reachable, otherwise in the browser (Pyodide).
(() => {
  const configEl = document.getElementById('ita-lab-config');
  const lab = document.querySelector('.ita-lab');
  if (!configEl || !lab) return;

  const config = JSON.parse(configEl.textContent);
  const statusEl = document.querySelector('[data-runtime-status]');
  const storageKey = (suffix) => `ita:${config.pageId}:${suffix}`;
  const store = {
    get(key) { try { return sessionStorage.getItem(storageKey(key)); } catch (_) { return null; } },
    set(key, value) { try { sessionStorage.setItem(storageKey(key), value); } catch (_) { /* storage blocked */ } },
    remove(key) { try { sessionStorage.removeItem(storageKey(key)); } catch (_) { /* storage blocked */ } },
  };

  let tabId = '';
  try {
    tabId = sessionStorage.getItem('browser-notebook:tab-session-id') || '';
    if (!tabId) {
      tabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
      sessionStorage.setItem('browser-notebook:tab-session-id', tabId);
    }
  } catch (_) {
    tabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  }
  const sessionId = `${tabId}:ita-${config.pageId}`;
  const apiUrls = (config.apiUrls || []).map((url) => String(url).replace(/\/$/, '')).filter(Boolean);

  // ---- status ---------------------------------------------------------------------------

  const setStatus = (text, state) => {
    if (!statusEl) return;
    statusEl.hidden = false;
    statusEl.textContent = text;
    statusEl.dataset.state = state;
  };

  // ---- analytics (same endpoint as the rest of the site) --------------------------------

  const track = (eventType, payload = {}) => {
    if (!config.analytics || !apiUrls.length) return;
    fetch(`${apiUrls[0]}/analytics/event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
      body: JSON.stringify({
        event_type: eventType,
        page: location.pathname,
        title: document.title,
        session_id: tabId,
        notebook_id: `ita-${config.pageId}`,
        language: navigator.language || '',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
        platform: navigator.userAgentData?.platform || navigator.platform || '',
        viewport_width: innerWidth,
        viewport_height: innerHeight,
        screen_width: screen.width,
        screen_height: screen.height,
        ...payload,
      }),
    }).catch(() => {});
  };

  // ---- runtimes -------------------------------------------------------------------------

  const fetchJson = async (url, options = {}, timeoutMs = 30000) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      });
      const text = await response.text();
      let payload = {};
      try { payload = text ? JSON.parse(text) : {}; } catch (_) { payload = { error: text }; }
      if (!response.ok) throw new Error(payload.error || `${response.status} ${response.statusText}`);
      return payload;
    } finally {
      clearTimeout(timer);
    }
  };

  const initBackend = async (baseUrl) => {
    await fetchJson(`${baseUrl}/health`, {}, 6000);
    const payload = await fetchJson(`${baseUrl}/session/init`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, initial_code: config.themeCode || '' }),
    }, 120000);
    if (payload.init && payload.init.success === false) {
      console.warn('Theme code failed on the backend', payload.init.stderr);
    }
    return {
      kind: 'backend',
      execute: (code) => fetchJson(`${baseUrl}/execute`, {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, code }),
      }, 240000),
    };
  };

  const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.27.5/full/';
  const PY_RUNNER = `
import ast, base64, io, sys, traceback, warnings
from contextlib import redirect_stdout, redirect_stderr
warnings.filterwarnings("ignore", message=".*non-interactive.*")
_CTX = {"__builtins__": __builtins__, "__name__": "__main__"}
_HTML = []
_FIGS = []

def _html_repr(value):
    if value is None or isinstance(value, type):
        return None
    repr_html = getattr(value, "_repr_html_", None)
    if callable(repr_html):
        try:
            html = repr_html()
            return html if isinstance(html, str) and html else None
        except Exception:
            return None
    return None

def _flush():
    plt = sys.modules.get("matplotlib.pyplot")
    if plt is None:
        return
    for number in plt.get_fignums():
        buffer = io.BytesIO()
        plt.figure(number).savefig(buffer, format="png", bbox_inches="tight", dpi=150)
        _FIGS.append(base64.b64encode(buffer.getvalue()).decode("ascii"))
    plt.close("all")

def display(*values):
    for value in values:
        if value is None:
            continue
        html = _html_repr(value)
        if html:
            _HTML.append(html)
        else:
            print(repr(value))

_CTX["display"] = display

def run_cell(code):
    _HTML.clear(); _FIGS.clear()
    out, err = io.StringIO(), io.StringIO()
    ok = True
    try:
        import matplotlib.pyplot as _plt
        _plt.show = lambda *a, **k: _flush()
    except Exception:
        pass
    try:
        tree = ast.parse(code, "<célula>", "exec")
        last = tree.body[-1] if tree.body and isinstance(tree.body[-1], ast.Expr) else None
        body = ast.Module(body=tree.body[:-1] if last else tree.body, type_ignores=[])
        with redirect_stdout(out), redirect_stderr(err):
            exec(compile(body, "<célula>", "exec"), _CTX, _CTX)
            if last is not None:
                display(eval(compile(ast.Expression(last.value), "<célula>", "eval"), _CTX, _CTX))
    except BaseException:
        ok = False
        err.write(traceback.format_exc())
    _flush()
    return {"success": ok, "stdout": out.getvalue(), "stderr": err.getvalue(), "figures": list(_FIGS), "html": list(_HTML)}
`;

  const loadScript = (src) => new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Não foi possível carregar ${src}`));
    document.head.append(script);
  });

  const initBrowser = async () => {
    setStatus('Carregando Python no navegador…', 'loading');
    await loadScript(`${PYODIDE_URL}pyodide.js`);
    const pyodide = await window.loadPyodide({ indexURL: PYODIDE_URL });
    await pyodide.loadPackage(['numpy', 'pandas', 'matplotlib', 'scipy', 'scikit-learn']);
    pyodide.FS.mkdirTree('/home/pyodide/utils');
    for (const file of config.pythonFiles || []) {
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Falha ao baixar ${file.path}`);
      pyodide.FS.writeFile(`/home/pyodide/${file.path}`, await response.text());
    }
    await pyodide.runPythonAsync(`import sys\nsys.path.insert(0, "/home/pyodide")\n${PY_RUNNER}`);
    const runCell = pyodide.globals.get('run_cell');
    const execute = async (code) => {
      const proxy = runCell(code);
      const result = proxy.toJs({ dict_converter: Object.fromEntries });
      proxy.destroy();
      return result;
    };
    if (config.themeCode) await execute(config.themeCode);
    return { kind: 'browser', execute };
  };

  let runtimePromise = null;
  const getRuntime = () => {
    if (runtimePromise) return runtimePromise;
    runtimePromise = (async () => {
      setStatus('Conectando ao Python…', 'loading');
      for (const baseUrl of apiUrls) {
        try {
          const runtime = await initBackend(baseUrl);
          setStatus('Python pronto · servidor', 'ready');
          return runtime;
        } catch (error) {
          console.warn(`Backend indisponível em ${baseUrl}`, error);
        }
      }
      try {
        const runtime = await initBrowser();
        setStatus('Python pronto · no navegador', 'ready');
        return runtime;
      } catch (error) {
        setStatus('Python indisponível — use o Colab', 'error');
        runtimePromise = null;
        throw error;
      }
    })();
    return runtimePromise;
  };

  // Cells run one at a time so a participant clicking quickly never races the session.
  let queue = Promise.resolve();
  const enqueue = (job) => {
    const next = queue.then(job, job);
    queue = next.catch(() => {});
    return next;
  };

  // ---- output ---------------------------------------------------------------------------

  const renderOutput = (outputEl, result) => {
    outputEl.replaceChildren();
    const stdout = (result.stdout || '').replace(/\s+$/, '');
    const stderr = (result.stderr || '').replace(/\s+$/, '');
    const figures = Array.isArray(result.figures) ? result.figures : [];
    const htmlBlocks = Array.isArray(result.html) ? result.html : [];

    if (stdout) {
      const pre = document.createElement('pre');
      pre.className = 'ita-output__text';
      pre.textContent = stdout;
      outputEl.append(pre);
    }
    htmlBlocks.forEach((html) => {
      const block = document.createElement('div');
      block.className = 'ita-output__html';
      block.innerHTML = html;
      outputEl.append(block);
    });
    figures.forEach((encoded) => {
      const img = document.createElement('img');
      img.className = 'ita-output__figure';
      img.alt = 'Gráfico gerado pela célula';
      img.src = `data:image/png;base64,${encoded}`;
      outputEl.append(img);
    });
    if (stderr) {
      const pre = document.createElement('pre');
      pre.className = result.success === false ? 'ita-output__error' : 'ita-output__warning';
      pre.textContent = stderr;
      outputEl.append(pre);
    }
    if (!outputEl.children.length) {
      const empty = document.createElement('p');
      empty.className = 'ita-output__empty';
      empty.textContent = 'Executada, sem saída.';
      outputEl.append(empty);
    }
    outputEl.hidden = false;
  };

  // ---- tasks ----------------------------------------------------------------------------

  const tasks = Array.from(lab.querySelectorAll('[data-task]')).map((article) => {
    const id = article.dataset.task;
    const seed = article.querySelector('[data-seed]').textContent;
    const solution = article.querySelector('[data-solution]')?.textContent || '';
    const textarea = article.querySelector('textarea');
    const saved = store.get(`code:${id}`);
    if (saved !== null) textarea.value = saved;

    let editor = null;
    if (window.CodeMirror) {
      editor = window.CodeMirror.fromTextArea(textarea, {
        mode: 'python',
        lineNumbers: true,
        indentUnit: 4,
        viewportMargin: Infinity,
        extraKeys: {
          'Shift-Enter': () => run(),
          Tab: (cm) => cm.replaceSelection('    '),
        },
      });
      editor.on('change', () => store.set(`code:${id}`, editor.getValue()));
    } else {
      textarea.addEventListener('input', () => store.set(`code:${id}`, textarea.value));
      textarea.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && event.shiftKey) { event.preventDefault(); run(); }
      });
    }

    const getCode = () => (editor ? editor.getValue() : textarea.value);
    const setCode = (value) => {
      if (editor) editor.setValue(value); else textarea.value = value;
      store.set(`code:${id}`, value);
    };

    const outputEl = article.querySelector('[data-output]');
    const stateEl = article.querySelector('[data-task-state]');
    const runButton = article.querySelector('[data-action="run"]');
    const task = { id, article, optional: article.classList.contains('ita-task--optional'), done: store.get(`done:${id}`) === '1' };

    const setDone = (done) => {
      task.done = done;
      article.classList.toggle('is-done', done);
      stateEl.textContent = done ? 'Feita' : '';
      if (done) store.set(`done:${id}`, '1'); else store.remove(`done:${id}`);
      updateProgress();
    };

    async function run() {
      runButton.disabled = true;
      runButton.textContent = 'Executando…';
      article.classList.add('is-running');
      try {
        const runtime = await getRuntime();
        const result = await enqueue(() => runtime.execute(getCode()));
        renderOutput(outputEl, result);
        if (result.success !== false) setDone(true);
        track('run_cell', { cell_label: id, runtime_mode: runtime.kind === 'backend' ? 'cloud' : 'browser' });
      } catch (error) {
        renderOutput(outputEl, { success: false, stderr: `Não foi possível executar: ${error.message || error}` });
      } finally {
        runButton.disabled = false;
        runButton.textContent = 'Executar';
        article.classList.remove('is-running');
      }
    }

    article.querySelector('[data-action="run"]').addEventListener('click', run);
    article.querySelector('[data-action="reset"]').addEventListener('click', () => setCode(seed));

    const hintButton = article.querySelector('[data-action="hint"]');
    if (hintButton) {
      const hints = Array.from(article.querySelectorAll('[data-hint]'));
      let shown = 0;
      hintButton.addEventListener('click', () => {
        article.querySelector('[data-hints]').hidden = false;
        if (shown < hints.length) hints[shown].hidden = false;
        shown += 1;
        if (shown >= hints.length) {
          hintButton.disabled = true;
          hintButton.textContent = 'Sem mais dicas';
        } else {
          hintButton.textContent = `Dica ${shown + 1}`;
        }
      });
    }

    const answerEl = article.querySelector('[data-answer]');
    const answerButton = article.querySelector('[data-action="answer"]');
    answerButton.addEventListener('click', () => {
      answerEl.hidden = !answerEl.hidden;
      answerButton.textContent = answerEl.hidden ? 'Resposta' : 'Esconder resposta';
      if (!answerEl.hidden) track('show_answer', { cell_label: id });
    });
    article.querySelector('[data-action="solution"]')?.addEventListener('click', () => setCode(solution));

    if (task.done) {
      article.classList.add('is-done');
      stateEl.textContent = 'Feita';
    }
    return task;
  });

  // ---- progress -------------------------------------------------------------------------

  const progressLabel = lab.querySelector('[data-progress-label]');
  const progressFill = lab.querySelector('[data-progress-fill]');
  const steps = new Map(Array.from(lab.querySelectorAll('[data-step]')).map((link) => [link.dataset.step, link]));

  function updateProgress() {
    const required = tasks.filter((task) => !task.optional);
    const done = required.filter((task) => task.done).length;
    progressLabel.textContent = `${done} de ${required.length} tarefas`;
    progressFill.style.width = `${required.length ? (100 * done) / required.length : 0}%`;
    tasks.forEach((task) => steps.get(task.id)?.classList.toggle('is-done', task.done));
  }

  // Highlight the task currently in view in the step bar.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          steps.forEach((link) => link.classList.remove('is-current'));
          steps.get(entry.target.dataset.task)?.classList.add('is-current');
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    tasks.forEach((task) => observer.observe(task.article));
  }

  updateProgress();
  track('page_view');
  // Warm the runtime up while the participant reads the first task.
  getRuntime().catch(() => {});
})();
