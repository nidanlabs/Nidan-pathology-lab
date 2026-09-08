(() => {
  const cfg = window.NIDAN_CONFIG || {};
  const configured = cfg.supabaseUrl && cfg.supabasePublishableKey && !cfg.supabasePublishableKey.startsWith('YOUR_');
  if (!configured || !window.supabase?.createClient) return;

  const client = window.supabase.createClient(cfg.supabaseUrl, cfg.supabasePublishableKey);
  const CHECK_MS = 30000;
  let checking = false;
  let signingOut = false;

  const lockout = async (message) => {
    if (signingOut) return;
    signingOut = true;
    const loginMessage = document.getElementById('loginMessage');
    if (loginMessage) loginMessage.textContent = message;
    try { await client.auth.signOut({ scope: 'local' }); } catch (_) {}
    window.location.replace(window.location.pathname + window.location.search + window.location.hash);
  };

  const checkActiveProfile = async (user) => {
    if (checking || !user?.id || signingOut) return;
    checking = true;
    try {
      const { data, error } = await client
        .from('profiles')
        .select('active')
        .eq('user_id', user.id)
        .maybeSingle();
      if (error || !data || data.active !== true) {
        await lockout('Your laboratory access is inactive. Please contact the laboratory owner.');
      }
    } finally {
      checking = false;
    }
  };

  const init = async () => {
    const { data: { session } } = await client.auth.getSession();
    if (session?.user) await checkActiveProfile(session.user);

    client.auth.onAuthStateChange((event, nextSession) => {
      if (event === 'SIGNED_OUT') return;
      if (nextSession?.user) setTimeout(() => checkActiveProfile(nextSession.user), 0);
    });

    setInterval(async () => {
      const { data: { session } } = await client.auth.getSession();
      if (session?.user) await checkActiveProfile(session.user);
    }, CHECK_MS);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        client.auth.getSession().then(({ data: { session } }) => {
          if (session?.user) checkActiveProfile(session.user);
        });
      }
    });
  };

  init();
})();
