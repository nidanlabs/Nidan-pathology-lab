(() => {
  const wait = 900;
  const original = () => window.NIDAN_PRINT?.report;
  let last = null;
  let lastAt = 0;

  const wrap = () => {
    const fn = original();
    if (!fn || fn.__nidanGuarded) return;
    const guarded = async id => {
      const now = Date.now();
      if (last === id && now - lastAt < wait) return;
      last = id; lastAt = now;
      return fn(id);
    };
    guarded.__nidanGuarded = true;
    window.NIDAN_PRINT.report = guarded;
  };

  // Reports has two legacy navigation handlers (app.js + workflow.js).
  // Capture the click first so the async legacy Reports loader cannot replace
  // the workflow DOM and later write into a detached/missing #reportPanel.
  document.addEventListener('click', event => {
    const target = event.target.closest('[data-section="reports"]');
    if (!target) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const open = window.NIDAN_WORKFLOW?.verificationHome;
    if (typeof open === 'function') {
      Promise.resolve(open()).catch(error => {
        const page = document.getElementById('page');
        if (page) page.innerHTML = `<div class="error-card"><h2>Unable to open reports</h2><p>${String(error?.message || error)}</p></div>`;
      });
    }
  }, true);

  setTimeout(wrap, 0);
})();
