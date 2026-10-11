(() => {
  if (window.top !== window) return;
  const observe = () => __OBSERVER__;
  let active = false, session = null, sequence = 0, pending = null, armed = null;
  let scrollBefore = null, scrollTimer = null;
  const documentId = String(performance.timeOrigin) + '-' + Math.random().toString(36).slice(2);
  const snapshot = () => { try { return observe(); } catch { return null; } };
  const safe = e => e && !['password', 'file', 'hidden'].includes(e.type);
  const value = e => safe(e) ? (e.isContentEditable ? e.innerText : e.value) : null;
  const textField = e => safe(e) && (e.isContentEditable || e.tagName === 'TEXTAREA' ||
    (e.tagName === 'INPUT' && ['text', 'search', 'email', 'url', 'tel', 'number'].includes(e.type)));
  const sends = new Set();
  function send(row) {
    const data = {...row, document_id: documentId, sequence: ++sequence, session_id: session,
      timestamp: new Date().toISOString(), frame_url: location.href};
    const p = window.__saveDemoEvent(data).catch(() => {
      // A visible error prevents a silent claim that the recording is complete.
      document.title = 'RECORDING ERROR — ' + document.title;
    }).finally(() => sends.delete(p));
    sends.add(p);
  }
  function match(before, e, kind, option) {
    const node = window.__jevFast?.ids.get(e);
    return before?.actions.filter(a => a.node === node && a.kind === kind &&
      (kind !== 'select' || a.value === option)) || [];
  }
  function record(kind, before, e, extra = {}) {
    const matches = match(before, e, kind, extra.value);
    send({kind, observation: before, selected_action: matches.length === 1 ? matches[0] : null,
      mapping: matches.length === 1 ? 'matched' : 'unsupported',
      reason: matches.length === 1 ? null : 'No unique observed action matches this event.', ...extra});
  }
  function flushText() {
    if (!pending) return;
    const p = pending;
    pending = null;
    if (p.edits.length) record('fill', p.before, p.element,
      {value: p.edits.at(-1).value, input_events: p.edits});
  }
  function flushScroll() {
    clearTimeout(scrollTimer);
    if (!scrollBefore) return;
    send({kind: 'scroll', observation: scrollBefore, selected_action: null, mapping: 'unsupported',
      reason: 'Manual scroll distance does not equal a fixed executor action.', scroll_after: {x: scrollX, y: scrollY}});
    scrollBefore = null;
  }
  window.__humanRecorderSet = async state => {
    if (!state.active) { flushText(); flushScroll(); }
    active = state.active;
    session = state.session_id;
    await Promise.all([...sends]);
  };
  window.__humanRecorderFlush = async () => {
    flushText(); flushScroll(); await Promise.all([...sends]);
    return snapshot();
  };
  window.addEventListener('pointerdown', e => {
    if (!active || !e.isTrusted) return;
    flushText(); flushScroll();
    armed = {before: snapshot(), target: e.target, time: performance.now()};
  }, true);
  window.addEventListener('click', e => {
    if (!active || !e.isTrusted) return;
    flushText();
    let element = e.composedPath().find(n => window.__jevFast?.ids.has(n));
    const label = e.target.closest?.('label');
    // The browser dispatches a second click on the labelled control.
    if (label?.control && !element) return;
    if (element?.tagName === 'SELECT' || e.target.tagName === 'OPTION') return;
    const pre = armed && performance.now() - armed.time < 3000 ? armed.before : null;
    if (!pre) {
      send({kind: 'click', observation: null, selected_action: null, mapping: 'unsupported',
        reason: 'No observation exists before this click.'});
    } else record('click', pre, element || e.target);
  }, true);
  window.addEventListener('beforeinput', e => {
    if (!active || !e.isTrusted || !textField(e.target)) return;
    if (pending?.element !== e.target) {
      flushText();
      pending = {element: e.target, before: snapshot(), edits: []};
    }
  }, true);
  window.addEventListener('input', e => {
    if (!active || !e.isTrusted || !textField(e.target)) return;
    if (!pending) pending = {element: e.target, before: null, edits: []};
    pending.edits.push({input_type: e.inputType || null, value: value(e.target), time: performance.now()});
  }, true);
  window.addEventListener('change', e => {
    if (!active || !e.isTrusted) return;
    if (e.target.tagName === 'SELECT') {
      record('select', armed?.before || null, e.target, {value: value(e.target)});
    } else if (!safe(e.target)) {
      send({kind: 'restricted_input', observation: null, selected_action: null, mapping: 'unsupported',
        reason: 'The observer does not support this input type. Its value was not recorded.'});
    }
  }, true);
  window.addEventListener('keydown', e => {
    if (!active || !e.isTrusted) return;
    if (e.key === 'Tab') { flushText(); return; }
    if (['Enter', ' ', 'ArrowUp', 'ArrowDown'].includes(e.key) && !textField(e.target)) {
      armed = {before: snapshot(), target: e.target, time: performance.now()};
    }
    if (e.key === 'Enter' && textField(e.target)) {
      flushText();
      send({kind: 'keypress', key: 'Enter', observation: snapshot(), selected_action: null,
        mapping: 'unsupported', reason: 'The executor has no Enter key action.'});
    }
  }, true);
  window.addEventListener('focusout', flushText, true);
  window.addEventListener('wheel', e => {
    if (active && e.isTrusted && !scrollBefore) { flushText(); scrollBefore = snapshot(); }
  }, {capture: true, passive: true});
  window.addEventListener('scroll', () => {
    if (!active) return;
    if (!scrollBefore) scrollBefore = snapshot();
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(flushScroll, 200);
  }, true);
  window.addEventListener('pagehide', () => { if (active) { flushText(); flushScroll(); } }, true);
  window.__getDemoConfig().then(state => window.__humanRecorderSet(state));
})();
