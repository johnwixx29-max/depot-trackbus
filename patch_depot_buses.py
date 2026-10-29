#!/usr/bin/env python3
"""Run in ~/Desktop/depot-trackbus:  python3 patch_depot_buses.py
Replaces the small Add/Edit Bus box with a full bus form (identity, crew,
emergency numbers, route stops with times, documents, service) and shows more
detail in the Fleet and Drivers tables. Backup: index.html.bak2
Run sql/06_bus_details.sql in Supabase FIRST."""
import re, shutil, sys
p = 'index.html'
s = open(p, encoding='utf-8').read()
if 'id="bf-bus_no"' in s:
    sys.exit('Already applied.')
shutil.copy(p, p + '.bak2')

def need(cond, what):
    if not cond:
        sys.exit('Could not find: ' + what + '  (send me a screenshot of this message)')

# ---------------- form description ----------------
SERVICE = ['Ordinary (Karnataka Sarige)', 'Express', 'Rajahamsa', 'Non-stop', 'AC', 'Sleeper', 'Electric', 'Mini bus', 'Other']
FUEL = ['Diesel', 'CNG', 'Electric', 'Other']

def inp(k, label, typ='text', ph='', full=False, **extra):
    cls = ' class="full"' if full else ''
    step = ' step="any"' if typ == 'number' else ''
    return f'<div{cls}><label for="bf-{k}">{label}</label><input type="{typ}" id="bf-{k}" placeholder="{ph}"{step} /></div>'
def sel(k, label, opts):
    o = '<option value="">Select</option>' + ''.join(f'<option>{x}</option>' for x in opts)
    return f'<div><label for="bf-{k}">{label}</label><select id="bf-{k}">{o}</select></div>'
def chk(k, label):
    return f'<div class="chk"><label><input type="checkbox" id="bf-{k}" /> {label}</label></div>'

html = '''<!-- ADD/EDIT BUS MODAL -->
<div id="modal-overlay">
  <div id="modal-box">
    <h3 id="modal-title">Add Bus</h3>

    <div class="bf-h">Bus</div>
    <div class="bf-grid">
''' + '\n      '.join([
    inp('bus_no', 'Bus number (registration) *', ph='KA22F1001'),
    inp('fleet_no', 'Depot / fleet code', ph='e.g. BGM-114'),
    sel('service_type', 'Service type', SERVICE),
    sel('fuel_type', 'Fuel', FUEL),
    inp('make', 'Make', ph='Ashok Leyland, Tata, Eicher...'),
    inp('model', 'Model'),
    inp('mfg_year', 'Year of manufacture', 'number', '2022'),
    inp('seats', 'Seats', 'number', '45'),
    inp('standing_capacity', 'Standing capacity', 'number'),
    inp('ladies_seats', 'Seats reserved for women', 'number'),
    chk('is_ac', 'Air-conditioned'),
    chk('wheelchair_accessible', 'Wheelchair accessible'),
    chk('is_active', 'In service (shown to riders)'),
]) + '''
    </div>

    <div class="bf-h">Crew</div>
    <div class="bf-grid">
      ''' + '\n      '.join([
    inp('driver_name', 'Driver name'),
    inp('driver_phone', 'Driver phone', 'tel', '+91...'),
    inp('driver_licence_no', 'Driver licence number'),
    inp('driver_emp_id', 'Driver employee ID'),
    inp('conductor_name', 'Conductor name'),
    inp('conductor_phone', 'Conductor phone', 'tel', '+91...'),
    inp('conductor_emp_id', 'Conductor employee ID'),
]) + '''
    </div>

    <div class="bf-h">Emergency and control</div>
    <div class="bf-grid">
      ''' + '\n      '.join([
    inp('emergency_phone', 'Emergency number (shown to riders)', 'tel', 'Helpline / control room'),
    inp('depot_control_phone', 'Depot control room number', 'tel'),
]) + '''
    </div>

    <div class="bf-h">Route and timetable</div>
    <div class="bf-grid">
      ''' + '\n      '.join([
    inp('route', 'Route name (leave blank to use first stop to last stop)', full=True, ph='Belagavi to Chikkodi via Nipani'),
    inp('fare_full', 'Full-route fare (Rs)', 'number', '85'),
]) + '''
      <div>
        <label>Runs on</label>
        <div id="bf-days">
          <label><input type="checkbox" class="od" value="Mon" /> Mon</label>
          <label><input type="checkbox" class="od" value="Tue" /> Tue</label>
          <label><input type="checkbox" class="od" value="Wed" /> Wed</label>
          <label><input type="checkbox" class="od" value="Thu" /> Thu</label>
          <label><input type="checkbox" class="od" value="Fri" /> Fri</label>
          <label><input type="checkbox" class="od" value="Sat" /> Sat</label>
          <label><input type="checkbox" class="od" value="Sun" /> Sun</label>
        </div>
      </div>
    </div>

    <label>Stops the bus goes through, in order, with arrival time</label>
    <div id="stops-head"><span>#</span><span>Stop name</span><span>Time</span><span>Latitude</span><span>Longitude</span><span></span></div>
    <div id="stops-list"></div>
    <datalist id="known-stops"></datalist>
    <div id="stops-actions">
      <button type="button" class="btn" id="stop-add">+ Add stop</button>
      <button type="button" class="btn" id="stop-bulk-toggle">Paste a list</button>
      <span id="stops-count"></span>
    </div>
    <div id="stops-bulk" style="display:none">
      <textarea id="stops-bulk-text" rows="6" placeholder="One stop per line:&#10;Belagavi CBT, 07:00 AM&#10;Tilakwadi, 07:12 AM&#10;Nipani, 08:30 AM, 16.4, 74.38"></textarea>
      <button type="button" class="btn" id="stops-bulk-add">Add these stops</button>
      <div class="hint">Format: name, time, and optionally latitude, longitude.</div>
    </div>
    <div class="hint">Latitude and longitude are filled in automatically for stops the system already knows. For a new stop, enter them so the app can place it on the map.</div>

    <div class="bf-h">Documents and service</div>
    <div class="bf-grid">
      ''' + '\n      '.join([
    inp('permit_no', 'Route permit number'),
    inp('permit_expiry', 'Permit valid until', 'date'),
    inp('insurance_expiry', 'Insurance valid until', 'date'),
    inp('fitness_expiry', 'Fitness certificate valid until', 'date'),
    inp('puc_expiry', 'Pollution (PUC) valid until', 'date'),
    inp('last_service_date', 'Last service date', 'date'),
    inp('next_service_due', 'Next service due', 'date'),
    inp('odometer_km', 'Odometer (km)', 'number'),
]) + '''
    </div>

    <div class="bf-h">Notes</div>
    <textarea id="bf-notes" rows="3" placeholder="Anything else about this bus"></textarea>

    <div id="modal-actions">
      <button class="btn danger" id="bf-delete-btn" style="display:none">Delete bus</button>
      <span style="flex:1"></span>
      <button class="btn" id="modal-cancel-btn">Cancel</button>
      <button class="btn primary" id="modal-save-btn">Save</button>
    </div>
  </div>
</div>

'''
a = s.find('<!-- ADD/EDIT BUS MODAL -->'); b = s.find('<!-- STUDENT PASS DETAIL -->')
need(a >= 0 and b > a, 'the Add/Edit Bus modal')
s = s[:a] + html + s[b:]

# ---------------- CSS ----------------
css = '''
  /* ---------- FULL BUS FORM ---------- */
  #modal-box { width: min(880px, 94vw); max-height: 92vh; overflow-y: auto; }
  #modal-box select, #modal-box textarea {
    width: 100%; background: var(--bg-deep); border: 1px solid var(--line); border-radius: 6px;
    padding: 9px 10px; color: var(--text-primary); font-size: 13px; font-family: inherit; }
  #modal-box textarea { resize: vertical; }
  #modal-box input[type=checkbox] { width: auto; margin-right: 6px; }
  #modal-box input:focus, #modal-box select:focus, #modal-box textarea:focus { outline: 2px solid var(--amber); outline-offset: -1px; }
  .bf-h { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--amber);
    margin: 22px 0 4px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }
  .bf-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 18px; }
  .bf-grid .full { grid-column: 1 / -1; }
  .bf-grid .chk { display: flex; align-items: flex-end; padding-bottom: 8px; }
  .bf-grid .chk label { margin: 0; font-size: 13px; color: var(--text-primary); }
  #bf-days { display: flex; flex-wrap: wrap; gap: 4px 14px; padding-top: 6px; }
  #bf-days label { margin: 0; font-size: 13px; color: var(--text-primary); }
  #stops-head, .stop-row { display: grid; grid-template-columns: 28px 1.6fr 132px 96px 96px 92px; gap: 6px; align-items: center; }
  #stops-head { font-size: 11px; color: var(--text-dim); margin: 6px 0 4px; }
  .stop-row { margin-bottom: 6px; }
  .stop-row .stop-num { color: var(--text-dim); font-size: 12px; text-align: center; }
  .stop-row .stop-btns { display: flex; gap: 4px; }
  .stop-row .stop-btns button { background: none; border: 1px solid var(--line); color: var(--text-dim);
    border-radius: 5px; width: 26px; height: 30px; cursor: pointer; }
  .stop-row .stop-btns button:hover { border-color: var(--amber); color: var(--amber); }
  #stops-actions { display: flex; align-items: center; gap: 10px; margin-top: 8px; }
  #stops-count { font-size: 12px; color: var(--text-dim); }
  #stops-bulk { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
  .hint { font-size: 12px; color: var(--text-dim); margin-top: 6px; }
  .sub-line { display: block; font-size: 11px; color: var(--text-dim); margin-top: 2px; }
  @media (max-width: 700px) { .bf-grid { grid-template-columns: 1fr; } #stops-head { display: none; }
    .stop-row { grid-template-columns: 24px 1fr 1fr; } }
'''
need('</style>' in s, '</style>')
s = s.replace('</style>', css + '</style>', 1)

# ---------------- table headers ----------------
h1 = '<tr><th>Bus No</th><th>Route</th><th>Driver</th><th>Phone</th><th>Status</th><th></th></tr>'
need(h1 in s, 'the Fleet table header')
s = s.replace(h1, '<tr><th>Bus No</th><th>Route</th><th>Driver</th><th>Conductor</th><th>Seats</th><th>Documents</th><th>Status</th><th></th></tr>')
h2 = '<tr><th>Driver Name</th><th>Phone</th><th>Assigned Bus</th><th>Route</th></tr>'
need(h2 in s, 'the Drivers table header')
s = s.replace(h2, '<tr><th>Staff</th><th>Role</th><th>Phone</th><th>Licence / Emp ID</th><th>Bus</th><th>Route</th></tr>')

# ---------------- load every column ----------------
s, n = re.subn(r"select\('id, bus_no, route, driver_name, driver_phone[^']*'\)", "select('*')", s)
need(n == 1, 'the buses query in loadBusNames')

# ---------------- fleet table ----------------
fleet = r'''  function docStatus(m) {
    const ds = [m.insurance_expiry, m.fitness_expiry, m.puc_expiry, m.permit_expiry].filter(Boolean);
    if (!ds.length) return { cls: 'stale', label: 'not added' };
    const days = Math.floor((Math.min(...ds.map(d => new Date(d).getTime())) - Date.now()) / 86400000);
    if (days < 0) return { cls: 'breakdown', label: 'expired' };
    if (days <= 30) return { cls: 'idle', label: 'due in ' + days + ' d' };
    return { cls: 'active', label: 'valid' };
  }

  function renderFleetTable() {
    const body = document.getElementById('fleet-table-body');
    const rows = Object.values(busMeta).map(meta => {
      const loc = buses[meta.id];
      const stale = loc ? isStale(loc.updated_at) : true;
      const status = loc ? (stale ? 'stale' : loc.status) : 'stale';
      const statusLabel = meta.is_active === false ? 'out of service' : (loc ? (stale ? 'no signal' : loc.status) : 'no data yet');
      const doc = docStatus(meta);
      const type = [meta.service_type, meta.is_ac ? 'AC' : ''].filter(Boolean).join(' · ');
      return `
        <tr>
          <td>${escHtml(meta.bus_no || '—')}${type ? `<span class="sub-line">${escHtml(type)}</span>` : ''}</td>
          <td>${escHtml(meta.route || '—')}</td>
          <td>${escHtml(meta.driver_name || '—')}${meta.driver_phone ? `<span class="sub-line">${escHtml(meta.driver_phone)}</span>` : ''}</td>
          <td>${escHtml(meta.conductor_name || '—')}${meta.conductor_phone ? `<span class="sub-line">${escHtml(meta.conductor_phone)}</span>` : ''}</td>
          <td>${meta.seats != null ? escHtml(meta.seats) : '—'}</td>
          <td><span class="badge ${doc.cls}">${doc.label}</span></td>
          <td><span class="badge ${status}">${statusLabel}</span></td>
          <td><button class="btn" data-edit="${escHtml(meta.id)}">Edit</button></td>
        </tr>`;
    }).join('');
    body.innerHTML = rows || `<tr><td colspan="8" class="empty-note">No buses added yet.</td></tr>`;

    body.querySelectorAll('button[data-edit]').forEach(btn => {
      btn.addEventListener('click', () => openBusModal(btn.dataset.edit));
    });
  }

'''
a = s.find('  function renderFleetTable() {')
tail = "openBusModal(btn.dataset.edit));\n    });\n  }\n"
b = s.find(tail, a)
need(a >= 0 and b > a, 'renderFleetTable')
s = s[:a] + fleet + s[b + len(tail):]

# ---------------- editor JS (modal open / stops / save / delete) ----------------
editor = r'''  // ---------- BUS EDITOR ----------
  const BF = {
    bus_no: 'req', fleet_no: 't', service_type: 's', fuel_type: 's', make: 't', model: 't', mfg_year: 'n',
    seats: 'n', standing_capacity: 'n', ladies_seats: 'n', is_ac: 'b', wheelchair_accessible: 'b', is_active: 'b',
    driver_name: 't', driver_phone: 't', driver_licence_no: 't', driver_emp_id: 't',
    conductor_name: 't', conductor_phone: 't', conductor_emp_id: 't',
    emergency_phone: 't', depot_control_phone: 't', route: 't', fare_full: 'n',
    permit_no: 't', permit_expiry: 'd', insurance_expiry: 'd', fitness_expiry: 'd', puc_expiry: 'd',
    last_service_date: 'd', next_service_due: 'd', odometer_km: 'n', notes: 't'
  };
  const bf = (k) => document.getElementById('bf-' + k);
  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  let stopRows = [];
  let knownStops = null;

  function setBusForm(meta) {
    Object.keys(BF).forEach(k => {
      const el = bf(k);
      if (BF[k] === 'b') el.checked = meta ? (k === 'is_active' ? meta[k] !== false : !!meta[k]) : (k === 'is_active');
      else el.value = meta && meta[k] != null ? meta[k] : '';
    });
    const od = meta && meta.operating_days ? String(meta.operating_days) : 'Daily';
    document.querySelectorAll('#bf-days .od').forEach(c => { c.checked = od === 'Daily' || od.split(',').includes(c.value); });
  }

  function readBusForm() {
    const out = {};
    for (const k of Object.keys(BF)) {
      const el = bf(k), kind = BF[k];
      if (kind === 'b') out[k] = el.checked;
      else if (kind === 'n') {
        if (el.value === '') out[k] = null;
        else { const v = Number(el.value); if (!isFinite(v) || v < 0) return { error: 'Enter a valid number for "' + k.replace(/_/g, ' ') + '".' }; out[k] = v; }
      }
      else if (kind === 'd') out[k] = el.value || null;
      else out[k] = el.value.trim() || null;
    }
    if (!out.bus_no) return { error: 'Bus number is required.' };
    const days = [...document.querySelectorAll('#bf-days .od')].filter(c => c.checked).map(c => c.value);
    out.operating_days = days.length === 7 ? 'Daily' : (days.length ? days.join(',') : null);
    return { payload: out };
  }

  function to24(t) {
    if (!t) return '';
    const m = String(t).trim().match(/^(\d{1,2})[:.](\d{2})\s*([AaPp][Mm])?$/);
    if (!m) return '';
    let h = parseInt(m[1], 10);
    if (m[3]) { h = h % 12; if (/p/i.test(m[3])) h += 12; }
    return h > 23 ? '' : String(h).padStart(2, '0') + ':' + m[2];
  }
  function to12(t24) {
    if (!t24) return null;
    const parts = t24.split(':'); let h = parseInt(parts[0], 10);
    const ap = h >= 12 ? 'PM' : 'AM'; h = h % 12 || 12;
    return String(h).padStart(2, '0') + ':' + parts[1] + ' ' + ap;
  }

  async function loadKnownStops() {
    if (knownStops) return;
    knownStops = {};
    const { data } = await sb.from('bus_stops').select('name, latitude, longitude').limit(5000);
    const dl = document.getElementById('known-stops'); dl.innerHTML = '';
    (data || []).forEach(st => {
      knownStops[String(st.name).toLowerCase()] = st;
      const o = document.createElement('option'); o.value = st.name; dl.appendChild(o);
    });
  }

  function mkInput(type, value, ph) {
    const e = document.createElement('input');
    e.type = type; e.value = value == null ? '' : value; if (ph) e.placeholder = ph;
    if (type === 'number') e.step = 'any';
    return e;
  }

  function renderStops() {
    const host = document.getElementById('stops-list'); host.innerHTML = '';
    stopRows.forEach((r, i) => {
      const row = document.createElement('div'); row.className = 'stop-row';
      const num = document.createElement('span'); num.className = 'stop-num'; num.textContent = i + 1;
      const name = mkInput('text', r.name, 'Stop name'); name.setAttribute('list', 'known-stops');
      const time = mkInput('time', r.time);
      const lat = mkInput('number', r.lat, 'auto');
      const lng = mkInput('number', r.lng, 'auto');
      name.addEventListener('input', () => { r.name = name.value; updateStopsCount(); });
      name.addEventListener('change', () => {
        const k = knownStops && knownStops[name.value.trim().toLowerCase()];
        if (k && (lat.value === '' && lng.value === '')) { r.lat = k.latitude; r.lng = k.longitude; lat.value = r.lat; lng.value = r.lng; }
      });
      time.addEventListener('input', () => { r.time = time.value; });
      lat.addEventListener('input', () => { r.lat = lat.value; });
      lng.addEventListener('input', () => { r.lng = lng.value; });
      const btns = document.createElement('div'); btns.className = 'stop-btns';
      const mk = (txt, title, fn) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = txt; b.title = title; b.addEventListener('click', fn); return b; };
      btns.appendChild(mk('↑', 'Move up', () => { if (i > 0) { [stopRows[i - 1], stopRows[i]] = [stopRows[i], stopRows[i - 1]]; renderStops(); } }));
      btns.appendChild(mk('↓', 'Move down', () => { if (i < stopRows.length - 1) { [stopRows[i + 1], stopRows[i]] = [stopRows[i], stopRows[i + 1]]; renderStops(); } }));
      btns.appendChild(mk('✕', 'Remove', () => { stopRows.splice(i, 1); renderStops(); }));
      [num, name, time, lat, lng, btns].forEach(x => row.appendChild(x));
      host.appendChild(row);
    });
    updateStopsCount();
  }

  function updateStopsCount() {
    const named = stopRows.filter(r => r.name.trim());
    document.getElementById('stops-count').textContent = named.length
      ? named.length + ' stops · ' + named[0].name.trim() + ' to ' + named[named.length - 1].name.trim() : 'No stops yet';
  }

  document.getElementById('stop-add').addEventListener('click', () => {
    stopRows.push({ name: '', time: '', lat: '', lng: '' }); renderStops();
    const rows = document.querySelectorAll('#stops-list .stop-row'); const last = rows[rows.length - 1];
    if (last) last.querySelector('input').focus();
  });
  document.getElementById('stop-bulk-toggle').addEventListener('click', () => {
    const box = document.getElementById('stops-bulk'); box.style.display = box.style.display === 'none' ? 'flex' : 'none';
  });
  document.getElementById('stops-bulk-add').addEventListener('click', () => {
    const lines = document.getElementById('stops-bulk-text').value.split('\n').map(l => l.trim()).filter(Boolean);
    if (stopRows.length && stopRows.every(r => !r.name.trim() && !r.time)) stopRows = [];
    lines.forEach(line => {
      const p = line.split(',').map(x => x.trim());
      const k = knownStops && knownStops[p[0].toLowerCase()];
      stopRows.push({ name: p[0], time: to24(p[1]), lat: p[2] || (k ? k.latitude : ''), lng: p[3] || (k ? k.longitude : '') });
    });
    document.getElementById('stops-bulk-text').value = ''; document.getElementById('stops-bulk').style.display = 'none';
    renderStops();
  });

  document.getElementById('add-bus-btn').addEventListener('click', () => openBusModal(null));

  async function openBusModal(busId) {
    editingBusId = busId;
    const meta = busId ? busMeta[busId] : null;
    document.getElementById('modal-title').textContent = busId ? 'Edit Bus' : 'Add Bus';
    document.getElementById('bf-delete-btn').style.display = busId ? '' : 'none';
    setBusForm(meta);
    stopRows = busId ? [] : [{ name: '', time: '', lat: '', lng: '' }, { name: '', time: '', lat: '', lng: '' }];
    renderStops();
    document.getElementById('modal-box').scrollTop = 0;
    document.getElementById('modal-overlay').classList.add('active');
    await loadKnownStops();
    if (busId) {
      const { data, error } = await sb.from('bus_route_stops').select('stop_name, arrival_time, seq').eq('bus_id', busId).order('seq');
      if (error) { alert('Could not load the stops: ' + error.message); }
      stopRows = (data || []).map(r => {
        const k = knownStops[String(r.stop_name).toLowerCase()];
        return { name: r.stop_name, time: to24(r.arrival_time), lat: k ? k.latitude : '', lng: k ? k.longitude : '' };
      });
      renderStops();
    }
  }

  document.getElementById('modal-cancel-btn').addEventListener('click', () => {
    document.getElementById('modal-overlay').classList.remove('active');
  });

  async function saveNewStopCoords(stops) {
    try {
      const wanted = stops.filter(r => r.lat !== '' && r.lat != null && r.lng !== '' && r.lng != null
        && isFinite(Number(r.lat)) && isFinite(Number(r.lng)) && !(knownStops && knownStops[r.name.trim().toLowerCase()]));
      if (!wanted.length) return;
      const seen = {};
      const rows = wanted.filter(r => { const k = r.name.trim().toLowerCase(); if (seen[k]) return false; seen[k] = 1; return true; })
        .map(r => ({ name: r.name.trim(), latitude: Number(r.lat), longitude: Number(r.lng) }));
      const { error } = await sb.from('bus_stops').insert(rows);
      if (error) { console.warn('new stops not saved:', error.message); alert('The bus was saved, but the new stop locations were not: ' + error.message); return; }
      rows.forEach(r => { knownStops[r.name.toLowerCase()] = { name: r.name, latitude: r.latitude, longitude: r.longitude }; });
    } catch (e) { console.warn(e); }
  }

  document.getElementById('modal-save-btn').addEventListener('click', async () => {
    const f = readBusForm();
    if (f.error) { alert(f.error); return; }
    const payload = f.payload;
    const stops = stopRows.map(r => ({ name: r.name.trim(), time: r.time, lat: r.lat, lng: r.lng })).filter(r => r.name || r.time);
    if (stops.some(r => !r.name)) { alert('Every stop needs a name. Remove the empty rows.'); return; }
    if (stops.length === 1) { alert('A route needs at least 2 stops (or leave them all empty).'); return; }
    const dup = Object.values(busMeta).find(m => m.id !== editingBusId &&
      String(m.bus_no || '').replace(/\s+/g, '').toUpperCase() === payload.bus_no.replace(/\s+/g, '').toUpperCase());
    if (dup) { alert('A bus with this number already exists.'); return; }
    if (!payload.route && stops.length >= 2) payload.route = stops[0].name + ' to ' + stops[stops.length - 1].name;

    const saveBtn = document.getElementById('modal-save-btn');
    saveBtn.disabled = true; saveBtn.textContent = 'Saving...';
    let busId = editingBusId, error;
    if (busId) ({ error } = await sb.from('buses').update(payload).eq('id', busId));
    else {
      const r = await sb.from('buses').insert(payload).select('id').single();
      error = r.error; busId = r.data && r.data.id;
    }
    if (error) { saveBtn.disabled = false; saveBtn.textContent = 'Save'; alert('Save failed: ' + error.message); return; }

    if (busId && stops.length) {
      const del = await sb.from('bus_route_stops').delete().eq('bus_id', busId);
      if (del.error) alert('The bus was saved, but its stops were not: ' + del.error.message);
      else {
        const ins = await sb.from('bus_route_stops').insert(stops.map((r, i) => ({
          bus_id: busId, seq: i + 1, stop_name: r.name, arrival_time: to12(r.time) })));
        if (ins.error) alert('The bus was saved, but its stops were not: ' + ins.error.message);
      }
      await saveNewStopCoords(stops);
    }
    saveBtn.disabled = false; saveBtn.textContent = 'Save';
    document.getElementById('modal-overlay').classList.remove('active');
    await loadBusNames();
    renderFleetTable();
    renderDriversTable();
    if (map) renderMapMarkers();
  });

  document.getElementById('bf-delete-btn').addEventListener('click', async () => {
    if (!editingBusId) return;
    const m = busMeta[editingBusId] || {};
    if (!confirm('Delete bus ' + (m.bus_no || '') + ' and its stops? This cannot be undone.\n\nTo just hide it from riders, untick "In service" instead.')) return;
    const { error } = await sb.from('buses').delete().eq('id', editingBusId);
    if (error) { alert('Could not delete: ' + error.message + '\n\nUntick "In service" to hide it instead.'); return; }
    document.getElementById('modal-overlay').classList.remove('active');
    await loadBusNames(); await loadLocations();
    renderFleetTable(); renderDriversTable();
    if (map) renderMapMarkers();
  });

'''
a = s.find('  document.getElementById(\'add-bus-btn\').addEventListener')
b = s.find('  // ---------- DRIVERS PAGE ----------')
need(a >= 0 and b > a, 'the old Add/Edit Bus code')
s = s[:a] + editor + s[b:]

# ---------------- drivers + conductors page ----------------
drivers = r'''  function renderDriversTable() {
    const body = document.getElementById('drivers-table-body');
    const rows = [];
    Object.values(busMeta).forEach(m => {
      const add = (name, role, phone, id) => rows.push(`
        <tr>
          <td>${escHtml(name)}</td>
          <td>${role}</td>
          <td>${escHtml(phone || '—')}</td>
          <td>${escHtml(id || '—')}</td>
          <td>${escHtml(m.bus_no || '—')}</td>
          <td>${escHtml(m.route || '—')}</td>
        </tr>`);
      if (m.driver_name) add(m.driver_name, 'Driver', m.driver_phone, [m.driver_licence_no, m.driver_emp_id].filter(Boolean).join(' / '));
      if (m.conductor_name) add(m.conductor_name, 'Conductor', m.conductor_phone, m.conductor_emp_id);
    });
    body.innerHTML = rows.join('') || `<tr><td colspan="6" class="empty-note">No crew added yet. Add drivers and conductors from the Fleet page.</td></tr>`;
  }

'''
a = s.find('  function renderDriversTable() {'); b = s.find('  // ---------- MAINTENANCE PAGE ----------')
need(a >= 0 and b > a, 'renderDriversTable')
s = s[:a] + drivers + s[b:]

open(p, 'w', encoding='utf-8').write(s)
print('Done. Backup saved as index.html.bak2')
