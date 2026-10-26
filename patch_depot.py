#!/usr/bin/env python3
"""Run in the depot-trackbus folder:  python3 patch_depot.py
Replaces the plain login box in index.html with a Google-style sign-in
(welcome -> email -> password -> authenticator code), a staff check,
idle sign-out and a "request access" form. Backup: index.html.bak"""
import re, shutil, sys
p = 'index.html'
s = open(p, encoding='utf-8').read()
if 'id="gate"' in s:
    sys.exit('Already patched.')
shutil.copy(p, p + '.bak')

# ---------- 1. HTML ----------
a = s.index('<!-- LOGIN -->')
b = s.index('<!-- APP -->')
html = r'''<!-- LOGIN -->
<div id="login-screen">
  <div id="gate">
    <div class="g-brand">
      <div class="mark">TRACKBUS &middot; DEPOT</div>
    </div>

    <!-- 0 welcome -->
    <section class="g-step" data-step="welcome">
      <h1>Depot Control</h1>
      <p class="sub">Live fleet monitoring, student passes and maintenance for NWKRTC depot staff.</p>
      <button class="g-btn" data-go="email">Sign in</button>
      <button class="g-btn ghost" data-go="request">Request access</button>
      <p class="fine">Authorised depot staff only. All sign-ins are logged.</p>
    </section>

    <!-- 1 email -->
    <section class="g-step" data-step="email" hidden>
      <h1>Sign in</h1>
      <p class="sub">Use your depot email</p>
      <form id="f-email" novalidate>
        <input type="email" id="g-email" placeholder="Email" autocomplete="username" required />
        <div class="g-err" id="e-email"></div>
        <div class="g-row"><button type="button" class="g-link" data-go="welcome">Back</button>
          <button class="g-btn inline" type="submit">Next</button></div>
      </form>
    </section>

    <!-- 2 password -->
    <section class="g-step" data-step="password" hidden>
      <h1>Welcome</h1>
      <div class="chip" id="g-chip"></div>
      <form id="f-pass" novalidate>
        <div class="pw"><input type="password" id="g-pass" placeholder="Password" autocomplete="current-password" required />
          <button type="button" class="eye" id="g-eye">Show</button></div>
        <div class="g-err" id="e-pass"></div>
        <div class="g-row"><button type="button" class="g-link" id="g-forgot">Forgot password?</button>
          <button class="g-btn inline" type="submit" id="g-pass-btn">Sign in</button></div>
        <div class="g-row"><button type="button" class="g-link" data-go="email">Use another account</button></div>
      </form>
    </section>

    <!-- 3a authenticator code -->
    <section class="g-step" data-step="mfa" hidden>
      <h1>2-step verification</h1>
      <p class="sub">Open your authenticator app and enter the 6-digit code.</p>
      <form id="f-mfa" novalidate>
        <input type="text" id="g-code" inputmode="numeric" maxlength="6" placeholder="123456" autocomplete="one-time-code" />
        <div class="g-err" id="e-mfa"></div>
        <div class="g-row"><button type="button" class="g-link" data-go="logout">Cancel</button>
          <button class="g-btn inline" type="submit">Verify</button></div>
      </form>
    </section>

    <!-- 3b first-time authenticator setup -->
    <section class="g-step" data-step="enroll" hidden>
      <h1>Secure your account</h1>
      <p class="sub">Scan this with Google Authenticator, Microsoft Authenticator or Authy, then enter the code it shows.</p>
      <div id="g-qr" class="qr"></div>
      <div class="secret">Can't scan? Key: <code id="g-secret"></code></div>
      <form id="f-enroll" novalidate>
        <input type="text" id="g-ecode" inputmode="numeric" maxlength="6" placeholder="123456" autocomplete="one-time-code" />
        <div class="g-err" id="e-enroll"></div>
        <div class="g-row"><button type="button" class="g-link" data-go="logout">Cancel</button>
          <button class="g-btn inline" type="submit">Turn on</button></div>
      </form>
    </section>

    <!-- request access -->
    <section class="g-step" data-step="request" hidden>
      <h1>Request access</h1>
      <p class="sub">Tell us who you are. An admin will verify you and create your account.</p>
      <form id="f-request" novalidate>
        <input type="text" id="r-name" placeholder="Full name" maxlength="80" />
        <input type="email" id="r-email" placeholder="Work email" maxlength="120" />
        <input type="text" id="r-depot" placeholder="Depot / office" maxlength="80" />
        <input type="tel" id="r-phone" placeholder="Phone" maxlength="20" />
        <input type="text" id="r-hp" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px" />
        <div class="g-err" id="e-request"></div>
        <div class="g-row"><button type="button" class="g-link" data-go="welcome">Back</button>
          <button class="g-btn inline" type="submit">Send request</button></div>
      </form>
    </section>

    <!-- message -->
    <section class="g-step" data-step="notice" hidden>
      <h1 id="n-title"></h1>
      <p class="sub" id="n-body"></p>
      <button class="g-btn" data-go="welcome">Done</button>
    </section>
  </div>
</div>

'''
s = s[:a] + html + s[b:]

# ---------- 2. CSS ----------
css = r'''
  /* ---------- GOOGLE-STYLE GATE ---------- */
  #gate { width: min(420px, calc(100vw - 32px)); background: var(--bg-panel); border: 1px solid var(--line);
    border-radius: 16px; padding: 36px 36px 28px; }
  #gate .g-brand { text-align: center; margin-bottom: 18px; }
  #gate .mark { font-family: var(--font-mono); font-size: 12px; letter-spacing: .3em; color: var(--amber); }
  #gate h1 { font-size: 26px; font-weight: 500; margin: 6px 0 8px; text-align: center; }
  #gate .sub { color: var(--text-dim); text-align: center; font-size: 14px; margin: 0 0 22px; line-height: 1.5; }
  #gate .fine { color: var(--text-dim); font-size: 12px; text-align: center; margin: 18px 0 0; }
  #gate form { display: flex; flex-direction: column; gap: 14px; }
  #gate input { background: var(--bg-deep); border: 1px solid var(--line); border-radius: 8px; padding: 14px;
    color: var(--text-primary); font-size: 15px; width: 100%; font-family: var(--font-display); }
  #gate input:focus { outline: 2px solid var(--amber); outline-offset: -1px; border-color: var(--amber); }
  #gate .g-btn { background: var(--amber); color: #1a1204; border: 0; border-radius: 8px; padding: 13px;
    font-weight: 600; font-size: 14px; cursor: pointer; width: 100%; margin-bottom: 10px; }
  #gate .g-btn.ghost { background: transparent; color: var(--amber); border: 1px solid var(--line); }
  #gate .g-btn.inline { width: auto; padding: 11px 26px; margin: 0; }
  #gate .g-btn:disabled { opacity: .6; cursor: default; }
  #gate .g-row { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
  #gate .g-link { background: none; border: 0; color: var(--amber); font-size: 13px; cursor: pointer; padding: 6px 0; }
  #gate .g-err { color: var(--red); font-size: 13px; min-height: 16px; }
  #gate .chip { margin: 0 auto 18px; padding: 6px 14px; border: 1px solid var(--line); border-radius: 20px;
    font-size: 13px; width: fit-content; max-width: 100%; overflow: hidden; text-overflow: ellipsis; }
  #gate .pw { position: relative; }
  #gate .pw .eye { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none;
    border: 0; color: var(--text-dim); font-size: 12px; cursor: pointer; }
  #gate .qr { background: #fff; padding: 10px; border-radius: 10px; width: 180px; height: 180px; margin: 0 auto 10px; }
  #gate .qr img { width: 100%; height: 100%; }
  #gate .secret { text-align: center; font-size: 12px; color: var(--text-dim); margin-bottom: 14px; word-break: break-all; }
  #gate #g-code, #gate #g-ecode { text-align: center; letter-spacing: .5em; font-size: 20px; }
'''
s = s.replace('</style>', css + '</style>', 1)

# ---------- 3. pinned, integrity-checked libraries ----------
s = s.replace('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />',
  '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />')
s = s.replace('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
  '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>')
s = s.replace('@supabase/supabase-js@2"', '@supabase/supabase-js@2.45.4"')
s = s.replace('<meta name="viewport"', '<meta name="referrer" content="no-referrer" />\n<meta name="robots" content="noindex,nofollow" />\n<meta name="viewport"', 1)

# ---------- 4. JS ----------
a = s.index("  const loginScreen = document.getElementById('login-screen');")
b = s.index("  let map, markers = {}")
c = s.index("  // ---------- AUTH ----------")
d = s.index("  // ============================================================\n  // STUDENT PASSES")
head = r'''  const loginScreen = document.getElementById('login-screen');
  const appShell = document.getElementById('app');
'''
auth = r'''  // ---------- AUTH (welcome -> email -> password -> 2-step code) ----------
  const $g = (id) => document.getElementById(id);
  const IDLE_MINUTES = 15;
  let gEmail = '', failCount = 0, lockedUntil = 0, idleTimer = null, enrolling = null;

  function gShow(step) {
    document.querySelectorAll('#gate .g-step').forEach(x => { x.hidden = x.dataset.step !== step; });
    const first = document.querySelector(`#gate [data-step="${step}"] input:not([tabindex])`);
    if (first) setTimeout(() => first.focus(), 30);
  }
  function gNotice(title, body) { $g('n-title').textContent = title; $g('n-body').textContent = body; gShow('notice'); }
  function gErr(id, msg) { $g(id).textContent = msg || ''; }

  document.querySelectorAll('#gate [data-go]').forEach(btn => btn.addEventListener('click', async () => {
    const to = btn.dataset.go;
    if (to === 'logout') { await sb.auth.signOut(); gShow('welcome'); return; }
    if (to === 'welcome') { $g('g-pass').value = ''; }
    gShow(to);
  }));
  $g('g-eye').addEventListener('click', () => {
    const i = $g('g-pass'); const show = i.type === 'password';
    i.type = show ? 'text' : 'password'; $g('g-eye').textContent = show ? 'Hide' : 'Show';
  });

  $g('f-email').addEventListener('submit', (e) => {
    e.preventDefault();
    const v = $g('g-email').value.trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) { gErr('e-email', 'Enter a valid email address'); return; }
    gErr('e-email'); gEmail = v; $g('g-chip').textContent = v; gShow('password');
  });

  $g('f-pass').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (Date.now() < lockedUntil) {
      gErr('e-pass', 'Too many attempts. Try again in ' + Math.ceil((lockedUntil - Date.now()) / 60000) + ' min.'); return;
    }
    const btn = $g('g-pass-btn'); btn.disabled = true; btn.textContent = 'Checking...';
    const { error } = await sb.auth.signInWithPassword({ email: gEmail, password: $g('g-pass').value });
    btn.disabled = false; btn.textContent = 'Sign in';
    if (error) {
      failCount++;
      if (failCount >= 5) { lockedUntil = Date.now() + 5 * 60000; failCount = 0; gErr('e-pass', 'Too many attempts. Locked for 5 minutes.'); }
      else gErr('e-pass', 'Wrong email or password');   // same message either way: do not reveal which
      return;
    }
    failCount = 0; $g('g-pass').value = ''; gErr('e-pass');
    await afterPassword();
  });

  // Is this signed-in user depot staff? (any rider can sign in to Supabase, so the dashboard must check)
  async function isStaff() {
    let r = await sb.rpc('is_depot_staff');
    if (r.error) r = await sb.rpc('is_depot_admin');
    return !r.error && r.data === true;
  }

  async function afterPassword() {
    if (!(await isStaff())) {
      await sb.auth.signOut();
      gShow('password'); gErr('e-pass', 'This account does not have depot access. Use "Request access".');
      return;
    }
    const { data: aal } = await sb.auth.mfa.getAuthenticatorAssuranceLevel();
    if (aal && aal.currentLevel === 'aal2') { enterApp(); return; }
    const { data: f } = await sb.auth.mfa.listFactors();
    const verified = (f && f.totp || []).find(x => x.status === 'verified');
    if (verified) { enrolling = { factorId: verified.id }; gShow('mfa'); return; }
    // first time: set up an authenticator app
    for (const x of (f && f.all || [])) if (x.status !== 'verified') await sb.auth.mfa.unenroll({ factorId: x.id });
    const { data, error } = await sb.auth.mfa.enroll({ factorType: 'totp', friendlyName: 'TrackBus depot' });
    if (error) { gShow('password'); gErr('e-pass', error.message); return; }
    enrolling = { factorId: data.id };
    $g('g-qr').innerHTML = '';
    const img = document.createElement('img'); img.alt = 'QR code'; img.src = data.totp.qr_code; $g('g-qr').appendChild(img);
    $g('g-secret').textContent = data.totp.secret;
    gShow('enroll');
  }

  async function verifyCode(inputId, errId) {
    const code = $g(inputId).value.replace(/\D/g, '');
    if (code.length !== 6) { gErr(errId, 'Enter the 6-digit code'); return; }
    const { data: ch, error: e1 } = await sb.auth.mfa.challenge({ factorId: enrolling.factorId });
    if (e1) { gErr(errId, e1.message); return; }
    const { error: e2 } = await sb.auth.mfa.verify({ factorId: enrolling.factorId, challengeId: ch.id, code });
    if (e2) { gErr(errId, 'That code did not work. Check the time on your phone and try again.'); return; }
    $g(inputId).value = ''; gErr(errId); enterApp();
  }
  $g('f-mfa').addEventListener('submit', (e) => { e.preventDefault(); verifyCode('g-code', 'e-mfa'); });
  $g('f-enroll').addEventListener('submit', (e) => { e.preventDefault(); verifyCode('g-ecode', 'e-enroll'); });

  $g('g-forgot').addEventListener('click', async () => {
    await sb.auth.resetPasswordForEmail(gEmail, { redirectTo: location.origin });
    gNotice('Check your email', 'If this email belongs to a depot account, a password reset link is on its way.');
  });

  $g('f-request').addEventListener('submit', async (e) => {
    e.preventDefault();
    if ($g('r-hp').value) { gNotice('Request sent', 'An admin will contact you.'); return; }   // bot trap
    const row = { full_name: $g('r-name').value.trim(), email: $g('r-email').value.trim().toLowerCase(),
                  depot: $g('r-depot').value.trim(), phone: $g('r-phone').value.trim() };
    if (!row.full_name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(row.email) || !row.depot) {
      gErr('e-request', 'Name, a valid email and depot are required'); return; }
    const { error } = await sb.from('depot_access_requests').insert(row);
    if (error) { gErr('e-request', 'Could not send. Try again later.'); return; }
    gErr('e-request'); gNotice('Request sent', 'An admin will verify you and create your account. You will be told by email.');
  });

  // sign out after IDLE_MINUTES without any activity
  function armIdle() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => { logout('You were signed out after ' + IDLE_MINUTES + ' minutes of inactivity.'); }, IDLE_MINUTES * 60000);
  }
  ['click', 'keydown', 'mousemove', 'touchstart'].forEach(ev => window.addEventListener(ev, () => { if (idleTimer) armIdle(); }, { passive: true }));

  async function logout(message) {
    clearTimeout(idleTimer); idleTimer = null;
    await sb.auth.signOut();
    appShell.classList.remove('active');
    loginScreen.style.display = 'flex';
    if (message) gNotice('Signed out', message); else gShow('welcome');
  }
  document.getElementById('logout-btn').addEventListener('click', () => logout());

  async function checkExistingSession() {
    const { data } = await sb.auth.getSession();
    gShow('welcome');
    if (data.session) {
      const { data: aal } = await sb.auth.mfa.getAuthenticatorAssuranceLevel();
      if (aal && aal.currentLevel === 'aal2' && await isStaff()) { enterApp(); return; }
      await sb.auth.signOut();   // half-finished or non-staff session: start again
    }
  }

  function enterApp() {
    loginScreen.style.display = 'none';
    appShell.classList.add('active');
    armIdle();
    initNav();
    loadAll();
  }


'''
s = s[:a] + head + s[b:c] + auth + s[d:]

# ---------- 5. escape text that comes from the database (stops script injection) ----------
n0 = 0
def sub(pat, rep):
    global s, n0
    s, k = re.subn(pat, rep, s); n0 += k
sub(r"\$\{((?:n\.)?meta\.(?:bus_no|route|driver_name|driver_phone)[^}]*)\}", r"${escHtml(\1)}")
sub(r"\$\{(m\.notes \|\| m\.issue_description \|\| '—')\}", r"${escHtml(\1)}")
sub(r"\$\{(maintenance && maintenance\.notes \? maintenance\.notes : '')\}", r"${escHtml(\1)}")
for old in ("const name = meta.bus_no || loc.bus_id.slice(0, 8);",):
    s = s.replace(old, "const name = escHtml(meta.bus_no || loc.bus_id.slice(0, 8));")
s = s.replace("const route = meta.route || 'Unknown route';", "const route = escHtml(meta.route || 'Unknown route');")
s = s.replace("const route = meta.route || '—';", "const route = escHtml(meta.route || '—');")
s = s.replace("`<br/>Driver: ${meta.driver_name}`", "`<br/>Driver: ${escHtml(meta.driver_name)}`")
print('escaped', n0, 'expressions')
open(p, 'w', encoding='utf-8').write(s)
print('Done. Backup saved as index.html.bak')
