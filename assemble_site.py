#!/usr/bin/env python3
"""Run LAST, in ~/Desktop/depot-trackbus, after the patch scripts.
Makes ONE website:   /        the public page (landing/index.html)
                     /depot/  the depot dashboard (your current index.html)
and writes vercel.json (security headers, and depot.trackbus.co.in -> /depot/)."""
import os, shutil, sys
if not os.path.exists('index.html'):
    sys.exit('Run this inside the depot-trackbus folder (the one with index.html).')
if os.path.exists('depot/index.html'):
    sys.exit('Already assembled (depot/index.html exists).')
src = open('index.html', encoding='utf-8').read()
if 'login-screen' not in src:
    sys.exit('index.html here does not look like the depot dashboard. Stopping so nothing is overwritten.')
here = os.path.dirname(os.path.abspath(__file__))
for need in ('landing/index.html', 'vercel.json'):
    if not os.path.exists(os.path.join(here, need)):
        sys.exit('Missing ' + need + ' next to this script.')
os.makedirs('depot', exist_ok=True)
shutil.move('index.html', 'depot/index.html')
shutil.copy(os.path.join(here, 'landing/index.html'), 'index.html')
shutil.copy(os.path.join(here, 'vercel.json'), 'vercel.json')
for junk in ('_headers',):
    if os.path.exists(junk): os.remove(junk)
print('Done:  /  = public page,  /depot/ = dashboard,  vercel.json written.')
