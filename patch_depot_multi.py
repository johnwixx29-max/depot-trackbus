#!/usr/bin/env python3
"""Run in ~/Desktop/depot-trackbus:  python3 patch_depot_multi.py
Makes the dashboard multi-depot: each staff member sees only their depot,
state admins see all depots and get a "Depots and Staff" page (add depots,
add or remove staff, read website requests), new staff can create their
own account on the sign-in screen. Backup: index.html.bak3
Run 08_multi_depot.sql in Supabase FIRST. Needs patch_depot_buses.py applied before."""
import re, shutil, sys
p = 'index.html'
s = open(p, encoding='utf-8').read()
if 'id="page-admin"' in s:
    sys.exit('Already applied.')
if 'id="bf-bus_no"' not in s:
    sys.exit('Run patch_depot_buses.py first (the full bus form), then run this again.')
shutil.copy(p, p + '.bak3')
done, skipped = [], []

def need_replace(name, old, new, count=1):
    global s
    if old not in s:
        skipped.append(name); return
    s = s.replace(old, new, count); done.append(name)

def regex_replace(name, pat, rep, flags=0):
    global s
    s2, n = re.subn(pat, rep, s, count=1, flags=flags)
    if n: s = s2; done.append(name)
    else: skipped.append(name)

# ---------- CSS ----------
css = '''
  /* ---------- MULTI-DEPOT ---------- */
  #depot-badge { padding: 0 20px 14px; font-size: 13px; }
  #depot-badge b { display: block; color: var(--text-primary); font-size: 14px; }
  #depot-badge span { color: var(--text-dim); font-size: 12px; }
  #depot-badge select { margin-top: 8px; width: 100%; background: var(--bg-deep); color: var(--text-primary);
    border: 1px solid var(--line); border-radius: 6px; padding: 7px 8px; font-size: 13px; }
  .adm-form { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 28px; align-items: center; }
  .adm-form input, .adm-form select { background: var(--bg-deep); border: 1px solid var(--line); border-radius: 6px;
    padding: 9px 10px; color: var(--text-primary); font-size: 13px; min-width: 150px; }
  .adm-note { font-size: 12px; color: var(--text-dim); margin: -16px 0 28px; max-width: 60em; }
'''
need_replace('css', '</style>', css + '</style>')

# ---------- nav: depot badge + admin item ----------
need_replace('nav badge', '<div class="mark">TRACKBUS</div>',
             '<div class="mark">TRACKBUS</div>\n    <div id="depot-badge"></div>')
need_replace('nav admin item', '    <div id="nav-footer">',
             '    <div class="nav-item" data-page="admin" id="nav-admin" style="display:none"><span class="dot"></span>Depots and Staff</div>\n    <div id="nav-footer">')

# ---------- admin page ----------
page = '''    <!-- DEPOTS AND STAFF (state admin) -->
    <div class="page" id="page-admin">
      <div class="page-header">
        <h1>Depots and Staff</h1>
        <span class="sub">Visible to state admins only</span>
      </div>

      <div class="section-title">Depots</div>
      <table class="data-table">
        <thead><tr><th>Name</th><th>Code</th><th>District</th><th>Helpline</th></tr></thead>
        <tbody id="adm-depots"></tbody>
      </table>
      <div class="adm-form">
        <input id="ad-name" placeholder="Depot name" maxlength="80">
        <input id="ad-code" placeholder="Code (BGM)" maxlength="10" style="min-width:90px">
        <input id="ad-district" placeholder="District" maxlength="60">
        <input id="ad-helpline" placeholder="Helpline" maxlength="20">
        <button class="btn primary" id="ad-add">Add depot</button>
      </div>

      <div class="section-title">Staff who can sign in</div>
      <table class="data-table">
        <thead><tr><th>Email</th><th>Name</th><th>Depot</th><th>Role</th><th></th></tr></thead>
        <tbody id="adm-staff"></tbody>
      </table>
      <div class="adm-form">
        <input id="as-email" type="email" placeholder="Staff email" maxlength="120">
        <input id="as-name" placeholder="Full name" maxlength="80">
        <select id="as-depot"></select>
        <select id="as-role"><option value="depot_admin">Depot admin</option><option value="state_admin">State admin (all depots)</option></select>
        <button class="btn primary" id="as-add">Add staff</button>
      </div>
      <div class="adm-note">After you add an email, that person opens the depot page, chooses Create account, and sets a password. On first sign-in they set up an authenticator app.</div>

      <div class="section-title">Requests from the website</div>
      <table class="data-table">
        <thead><tr><th>Received</th><th>Name</th><th>Depot or organisation</th><th>Contact</th><th>Message</th><th>Status</th></tr></thead>
        <tbody id="adm-requests"></tbody>
      </table>
    </div>

'''
regex_replace('admin page', r'(    <!-- STUDENT PASSES -->\s*)?(<div class="page" id="page-students">)', lambda m: (m.group(1) or '') + page + m.group(2))

# ---------- bus form: depot choice ----------
regex_replace('bus form depot field',
    r'(<div class="bf-h">Bus</div>\s*<div class="bf-grid">)',
    r'\1\n      <div class="full"><label for="bf-depot_id">Depot</label><select id="bf-depot_id"></select></div>')
need_replace('BF depot', "bus_no: 'req',", "bus_no: 'req', depot_id: 's',")
need_replace('default depot', '    setBusForm(meta);\n',
             "    setBusForm(meta);\n    if (!meta) bf('depot_id').value = (isState() ? (depotFilter || '') : (me.depotId || ''));\n")
need_replace('require depot', '    const payload = f.payload;\n',
             "    const payload = f.payload;\n    if (!payload.depot_id) { alert('Choose the depot this bus belongs to.'); return; }\n")

# ---------- data: only this depot's buses ----------
regex_replace('scoped buses', r"await sb\.from\('buses'\)\.select\(([^)]*)\)\.limit\(\d+\)", r"await scopedBuses(\1).limit(1000)")
need_replace('locations filter', "(data || []).forEach(loc => { buses[loc.bus_id] = loc; });",
             "(data || []).forEach(loc => { if (busMeta[loc.bus_id]) buses[loc.bus_id] = loc; });")
need_replace('realtime filter', "else buses[payload.new.bus_id] = payload.new;",
             "else if (busMeta[payload.new.bus_id]) buses[payload.new.bus_id] = payload.new;")
need_replace('load profile first', "  async function loadAll() {\n    await loadBusNames();",
             "  async function loadAll() {\n    await loadProfile();\n    await loadBusNames();")
need_replace('reset redirect', "redirectTo: location.origin }", "redirectTo: location.origin + location.pathname }")

# ---------- JS ----------
js = r'''  // ---------- WHO AM I: depot and role ----------
  let me = { role: 'depot_admin', depotId: null, depotName: '', name: '' };
  let depotFilter = '';
  let depotList = [];
  const isState = () => me.role === 'state_admin';

  function scopedBuses(cols) {
    let q = sb.from('buses').select(cols);
    const d = isState() ? depotFilter : me.depotId;
    if (d) q = q.eq('depot_id', d);
    return q;
  }

  async function loadProfile() {
    try {
      const { data: { session } } = await sb.auth.getSession();
      const email = ((session && session.user && session.user.email) || '').toLowerCase();
      const r = await sb.from('depot_admins').select('depot_id, role, full_name, depots(name, code)').eq('email', email).limit(1);
      if (r.error) console.warn('profile:', r.error.message);
      const row = r.data && r.data[0];
      if (row) me = { role: row.role || 'depot_admin', depotId: row.depot_id, depotName: row.depots ? row.depots.name : '', name: row.full_name || '', email };
      const d = await sb.from('depots').select('id, name, code, district, helpline').order('name');
      depotList = d.data || [];
    } catch (e) { console.warn(e); }
    renderDepotBadge();
  }

  function renderDepotBadge() {
    const badge = document.getElementById('depot-badge');
    badge.innerHTML = '';
    const b = document.createElement('b'); const sp = document.createElement('span');
    if (isState()) {
      b.textContent = 'All depots'; sp.textContent = 'State admin';
      badge.appendChild(b); badge.appendChild(sp);
      const sel = document.createElement('select'); sel.id = 'depot-filter';
      sel.innerHTML = '<option value="">Every depot</option>' + depotList.map(d => `<option value="${escHtml(d.id)}">${escHtml(d.name)}</option>`).join('');
      sel.value = depotFilter;
      sel.addEventListener('change', async () => {
        depotFilter = sel.value;
        await loadBusNames(); await loadLocations();
        renderOverview(); renderFleetTable(); renderDriversTable(); if (map) renderMapMarkers();
      });
      badge.appendChild(sel);
    } else {
      b.textContent = me.depotName || 'No depot assigned'; sp.textContent = me.name ? me.name + ', depot admin' : 'Depot admin';
      badge.appendChild(b); badge.appendChild(sp);
    }
    document.getElementById('nav-admin').style.display = isState() ? '' : 'none';
    const opts = (isState() ? depotList : depotList.filter(d => d.id === me.depotId));
    const o = opts.map(d => `<option value="${escHtml(d.id)}">${escHtml(d.name)}</option>`).join('');
    const bd = document.getElementById('bf-depot_id');
    bd.innerHTML = (isState() ? '<option value="">Choose a depot</option>' : '') + o;
    bd.disabled = !isState();
    document.getElementById('as-depot').innerHTML = depotList.map(d => `<option value="${escHtml(d.id)}">${escHtml(d.name)}</option>`).join('');
  }

  // ---------- DEPOTS AND STAFF PAGE ----------
  async function loadAdmin() {
    const [dp, st, pr, ar] = await Promise.all([
      sb.from('depots').select('*').order('name'),
      sb.from('depot_admins').select('email, full_name, role, depot_id').order('email'),
      sb.from('pilot_requests').select('*').order('created_at', { ascending: false }).limit(100),
      sb.from('depot_access_requests').select('*').order('created_at', { ascending: false }).limit(100),
    ]);
    depotList = dp.data || depotList;
    const depotName = (id) => { const d = depotList.find(x => x.id === id); return d ? d.name : '—'; };

    document.getElementById('adm-depots').innerHTML = depotList.map(d =>
      `<tr><td>${escHtml(d.name)}</td><td>${escHtml(d.code || '—')}</td><td>${escHtml(d.district || '—')}</td><td>${escHtml(d.helpline || '—')}</td></tr>`).join('')
      || '<tr><td colspan="4" class="empty-note">No depots yet.</td></tr>';

    document.getElementById('adm-staff').innerHTML = (st.data || []).map(a =>
      `<tr><td>${escHtml(a.email)}</td><td>${escHtml(a.full_name || '—')}</td><td>${escHtml(depotName(a.depot_id))}</td>
        <td>${a.role === 'state_admin' ? 'State admin' : 'Depot admin'}</td>
        <td><button class="btn danger" data-rm="${escHtml(a.email)}">Remove</button></td></tr>`).join('')
      || '<tr><td colspan="5" class="empty-note">No staff yet.</td></tr>';
    document.querySelectorAll('#adm-staff button[data-rm]').forEach(btn => btn.addEventListener('click', async () => {
      const email = btn.dataset.rm;
      if (me.email && email.toLowerCase() === me.email.toLowerCase()) { alert('You cannot remove your own access.'); return; }
      if (!confirm('Remove sign-in access for ' + email + '?')) return;
      const { error } = await sb.from('depot_admins').delete().eq('email', email);
      if (error) { alert('Could not remove: ' + error.message); return; }
      loadAdmin();
    }));

    const reqs = [];
    (pr.data || []).forEach(r => reqs.push({ t: 'pilot_requests', id: r.id, at: r.created_at, name: r.full_name, org: [r.organisation, r.district].filter(Boolean).join(', '), contact: [r.phone, r.email].filter(Boolean).join(' / '), msg: r.message || '', status: r.status }));
    (ar.data || []).forEach(r => reqs.push({ t: 'depot_access_requests', id: r.id, at: r.created_at, name: r.full_name, org: r.depot, contact: [r.phone, r.email].filter(Boolean).join(' / '), msg: 'Access request', status: r.status }));
    reqs.sort((a, b) => String(b.at).localeCompare(String(a.at)));
    document.getElementById('adm-requests').innerHTML = reqs.map(r =>
      `<tr><td>${escHtml(new Date(r.at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }))}</td><td>${escHtml(r.name)}</td><td>${escHtml(r.org)}</td>
        <td>${escHtml(r.contact || '—')}</td><td>${escHtml(r.msg)}</td>
        <td>${r.status === 'new' ? `<button class="btn" data-done="${escHtml(r.t + '|' + r.id)}">Mark contacted</button>` : escHtml(r.status)}</td></tr>`).join('')
      || '<tr><td colspan="6" class="empty-note">No requests yet.</td></tr>';
    document.querySelectorAll('#adm-requests button[data-done]').forEach(btn => btn.addEventListener('click', async () => {
      const [t, id] = btn.dataset.done.split('|');
      const { error } = await sb.from(t).update({ status: 'contacted' }).eq('id', id);
      if (error) { alert('Could not update: ' + error.message); return; }
      loadAdmin();
    }));
  }

  document.getElementById('nav-admin').addEventListener('click', loadAdmin);

  document.getElementById('ad-add').addEventListener('click', async () => {
    const v = (id) => document.getElementById(id).value.trim();
    if (!v('ad-name')) { alert('Enter the depot name.'); return; }
    const { error } = await sb.from('depots').insert({ name: v('ad-name'), code: v('ad-code') || null, district: v('ad-district') || null, helpline: v('ad-helpline') || null });
    if (error) { alert('Could not add the depot: ' + error.message); return; }
    ['ad-name', 'ad-code', 'ad-district', 'ad-helpline'].forEach(id => { document.getElementById(id).value = ''; });
    await loadAdmin(); renderDepotBadge();
  });

  document.getElementById('as-add').addEventListener('click', async () => {
    const email = document.getElementById('as-email').value.trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { alert('Enter a valid email address.'); return; }
    const depot_id = document.getElementById('as-depot').value;
    const role = document.getElementById('as-role').value;
    if (role === 'depot_admin' && !depot_id) { alert('Choose a depot.'); return; }
    const { error } = await sb.from('depot_admins').insert({ email, full_name: document.getElementById('as-name').value.trim() || null, depot_id: depot_id || null, role });
    if (error) { alert('Could not add: ' + error.message); return; }
    document.getElementById('as-email').value = ''; document.getElementById('as-name').value = '';
    loadAdmin();
  });

'''
need_replace('multi js', '  async function loadBusNames() {', js + '  async function loadBusNames() {')

# ---------- sign-in: create staff account ----------
if 'id="gate"' in s:
    need_replace('welcome link', '<button class="g-btn ghost" data-go="request">Request access</button>',
        '<button class="g-btn ghost" data-go="request">Request access</button>\n      <button class="g-link" data-go="signup" style="display:block;margin:0 auto">Create account (staff added by an admin)</button>')
    signup_html = '''    <!-- create staff account -->
    <section class="g-step" data-step="signup" hidden>
      <h1>Create account</h1>
      <p class="sub">Use the email your admin added. You will not get access until they have.</p>
      <form id="f-signup" novalidate>
        <input type="email" id="su-email" placeholder="Email" autocomplete="username" />
        <input type="password" id="su-pass" placeholder="Password, at least 12 characters" autocomplete="new-password" />
        <input type="password" id="su-pass2" placeholder="Repeat password" autocomplete="new-password" />
        <div class="g-err" id="e-signup"></div>
        <div class="g-row"><button type="button" class="g-link" data-go="welcome">Back</button>
          <button class="g-btn inline" type="submit">Create account</button></div>
      </form>
    </section>

'''
    need_replace('signup html', '    <!-- message -->', signup_html + '    <!-- message -->')
    signup_js = r'''  $g('f-signup').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = $g('su-email').value.trim().toLowerCase(), pw = $g('su-pass').value;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { gErr('e-signup', 'Enter a valid email address'); return; }
    if (pw.length < 12 || !/[A-Za-z]/.test(pw) || !/\d/.test(pw)) { gErr('e-signup', 'Use at least 12 characters, with letters and numbers'); return; }
    if (pw !== $g('su-pass2').value) { gErr('e-signup', 'The two passwords do not match'); return; }
    const { data, error } = await sb.auth.signUp({ email, password: pw, options: { emailRedirectTo: location.origin + location.pathname } });
    if (error) { gErr('e-signup', error.message); return; }
    gErr('e-signup'); $g('su-pass').value = ''; $g('su-pass2').value = '';
    if (data && data.session) { gEmail = email; await afterPassword(); }
    else gNotice('Check your email', 'We sent a link to ' + email + '. Open it, then sign in here.');
  });

'''
    need_replace('signup js', "  $g('f-request').addEventListener('submit'", signup_js + "  $g('f-request').addEventListener('submit'")
else:
    skipped.append('sign-up screen (security patch not applied)')

open(p, 'w', encoding='utf-8').write(s)
print('Applied:', ', '.join(done))
if skipped: print('SKIPPED:', ', '.join(skipped))
print('Backup saved as index.html.bak3')
