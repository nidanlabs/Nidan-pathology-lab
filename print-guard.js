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
  setTimeout(wrap, 0);
})();