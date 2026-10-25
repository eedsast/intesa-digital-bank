# -*- coding: utf-8 -*-
"""Render the HL architecture drawio to inline SVG: same geometry, same colours."""
import re, html, sys

src = '/mnt/user-data/outputs/arch/Target Architecture - high level.drawio'
d = open(src, encoding='utf-8').read()

cells = []
for m in re.finditer(r'<mxCell\b(.*?)(?:/>|</mxCell>)', d, re.S):
    blk = m.group(0)
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    geo = re.search(r'<mxGeometry([^>]*)/?>', blk)
    if not geo or 'edge' in attrs: continue
    g = dict(re.findall(r'(\w+)="([^"]*)"', geo.group(1)))
    try:
        x, y = float(g.get('x', 0)), float(g.get('y', 0))
        w, h = float(g['width']), float(g['height'])
    except (KeyError, ValueError):
        continue
    style = attrs.get('style', '')
    raw = html.unescape(attrs.get('value', ''))
    label = re.sub(r'<br\s*/?>', '\n', raw)
    label = re.sub(r'</?div[^>]*>|</?p[^>]*>', '\n', label)
    label = html.unescape(re.sub(r'<[^>]+>', '', label)).replace('\xa0', ' ')
    label = '\n'.join(l.strip() for l in label.split('\n') if l.strip())
    def sv(k, dflt=None):
        mm = re.search(k + r'=([^;"]*)', style)
        return mm.group(1) if mm else dflt
    cells.append(dict(x=x, y=y, w=w, h=h, style=style, label=label,
                      fill=sv('fillColor'), stroke=sv('strokeColor'),
                      rounded=sv('rounded', '0') == '1',
                      sw=float(sv('strokeWidth', '1') or 1),
                      shape=sv('shape'), rot=float(sv('rotation', '0') or 0),
                      fs=float(sv('fontSize', '12') or 12),
                      bold='fontStyle=1' in style, istext=style.startswith('text;')))

# brackets are skipped when drawing, so they must not stretch the viewBox either
vis=[c for c in cells if not (c['shape'] and 'annotation_2' in c['shape'])]
xs=[c['x'] for c in vis]; ys=[c['y'] for c in vis]
xe=[c['x']+c['w'] for c in vis]; ye=[c['y']+c['h'] for c in vis]
PAD=24
minx,miny,maxx,maxy = min(xs)-PAD, min(ys)-PAD, max(xe)+PAD, max(ye)+PAD
W,H = maxx-minx, maxy-miny

def esc(t): return (t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'))
def wrap(text, width, fs):
    cw = fs*0.55
    out=[]
    for para in text.split('\n'):
        words=para.split(); line=''
        for wd in words:
            t=(line+' '+wd).strip()
            if len(t)*cw > width-12 and line:
                out.append(line); line=wd
            else: line=t
        if line: out.append(line)
    return out

parts=[]
# bands first (unrounded pale rects), then boxes, so boxes sit on top
cells.sort(key=lambda c: (0 if (c['fill']=='#fff2cc' or c['w']>400 and not c['label']) else 1, c['y']))

for c in cells:
    x,y,w,h = c['x']-minx, c['y']-miny, c['w'], c['h']
    sh, st = c['shape'], (c['stroke'] or '#36393d').lstrip('#')
    st = '#'+st.lstrip('#')
    fill = c['fill'] or 'none'
    if c['istext'] or (sh is None and fill=='none' and not c['stroke']):
        pass  # plain label, drawn below
    elif sh == 'umlActor':
        cx, cy = x+w/2, y+h/2
        parts.append(f'<g stroke="#36393d" stroke-width="1.4" fill="none">'
                     f'<circle cx="{cx:.1f}" cy="{y+8:.1f}" r="7"/>'
                     f'<path d="M{cx:.1f} {y+15:.1f}V{y+34:.1f}M{x+4:.1f} {y+22:.1f}H{x+w-4:.1f}'
                     f'M{cx:.1f} {y+34:.1f}L{x+4:.1f} {y+h:.1f}M{cx:.1f} {y+34:.1f}L{x+w-4:.1f} {y+h:.1f}"/></g>')
    elif sh and 'cylinder' in sh:
        parts.append(f'<path d="M{x} {y+9}a{w/2} 9 0 0 1 {w} 0v{h-18}a{w/2} 9 0 0 1 {-w} 0z" '
                     f'fill="{fill}" stroke="{st}"/>'
                     f'<path d="M{x} {y+9}a{w/2} 9 0 0 0 {w} 0" fill="none" stroke="{st}"/>')
    elif sh == 'rhombus' or c['style'].startswith('rhombus'):
        parts.append(f'<path d="M{x+w/2} {y}L{x+w} {y+h/2}L{x+w/2} {y+h}L{x} {y+h/2}z" '
                     f'fill="{fill}" stroke="{st}"/>')
    elif sh and 'annotation_2' in sh:
        continue
    else:
        r = 6 if c['rounded'] else 0
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
                     f'fill="{fill}" stroke="{st}" stroke-width="{c["sw"]}"/>')

    if not c['label'] or sh == 'umlActor': continue
    fs = c['fs'] if c['fs'] != 12 else (12 if not c['istext'] else 12)
    weight = '700' if c['bold'] else '500'
    if 'swimlane' in c['style'] and 'horizontal=0' in c['style']:
        cx, cy = x+w/2, y+h/2
        parts.append(f'<text transform="translate({cx:.1f},{cy:.1f}) rotate(-90)" text-anchor="middle" '
                     f'dominant-baseline="central" font-size="{fs}" font-weight="700">{esc(c["label"])}</text>')
        continue
    lines = wrap(c['label'], w, fs)
    y0 = y + h/2 - (len(lines)-1)*fs*0.62
    for i, ln in enumerate(lines):
        parts.append(f'<text x="{x+w/2:.1f}" y="{y0+i*fs*1.24:.1f}" text-anchor="middle" '
                     f'dominant-baseline="central" font-size="{fs}" font-weight="{weight}">{esc(ln)}</text>')

svg = (f'<svg class="arch-svg" viewBox="0 0 {W:.0f} {H:.0f}" xmlns="http://www.w3.org/2000/svg" '
       f'role="img" aria-label="Target architecture — high level">\n'
       f'<title>Target architecture — high level</title>\n'
       f'<g font-family="Instrument Sans, Helvetica, Arial, sans-serif" fill="#1A1A1A">\n'
       + '\n'.join(parts) + '\n</g>\n</svg>')
open('/tmp/claude-0/-home-claude/1edb3c17-826c-51cf-96fe-4703a9d26580/scratchpad/arch.svg','w',encoding='utf-8').write(svg)
print('svg written:', len(svg), 'chars, viewBox', f'{W:.0f}x{H:.0f}', '-', len(parts), 'elements')
