#!/usr/bin/env python3
"""Run in ~/Desktop/depot-trackbus. Changes the word 'riders' to 'passengers' in the depot dashboard."""
p = 'depot/index.html'
s = open(p, encoding='utf-8').read()
n = s.count('riders')
s = s.replace('shown to riders', 'shown to passengers').replace('hide it from riders', 'hide it from passengers')
open(p, 'w', encoding='utf-8').write(s)
print('Done. Remaining "riders":', s.count('riders'), '(was', n, ')')
