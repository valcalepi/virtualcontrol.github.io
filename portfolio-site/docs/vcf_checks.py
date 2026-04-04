#!/usr/bin/env python3
"""VCF Health Check — Extracted Python modules.
Called by vcf-health-check.sh for complex data processing.
Each subcommand reads from stdin and/or environment variables.
"""
import sys


def html_report():
    """Generate HTML health check report.
    Env: HTML_DATA_FILE, HTML_REPORT_FILE, CUSTOMER_NAME, CUSTOMER_LOGO, CUSTOMER_ENV_LABEL"""
    import sys, re, html as html_mod, os, json, math, glob as glob_mod, base64, mimetypes

    data_file = os.environ.get('HTML_DATA_FILE', '')
    output_file = os.environ.get('HTML_REPORT_FILE', '')
    script_dir = os.path.dirname(output_file) if output_file else ''
    if not data_file or not output_file: sys.exit(1)

    with open(data_file, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    results, failures, warnings, remediations = [], [], [], []
    components, meta, history, trends = [], {}, {}, []
    fix_actions, latency_data, sla_data = [], [], []

    for line in lines:
        line = line.rstrip('\n')
        if line.startswith('R:'): results.append(line[2:])
        elif line.startswith('F:'): failures.append(line[2:])
        elif line.startswith('W:'): warnings.append(line[2:])
        elif line.startswith('REM:'): remediations.append(line[4:])
        elif line.startswith('C:'):
            parts = line[2:].split('|')
            if len(parts)==5: components.append({'name':parts[0],'pass':int(parts[1]),'warn':int(parts[2]),'fail':int(parts[3]),'status':parts[4]})
        elif line.startswith('META:'): k,v=line[5:].split('=',1); meta[k]=v
        elif line.startswith('HIST:'): k,v=line[5:].split('=',1); history[k]=v
        elif line.startswith('TREND:'):
            parts=line[6:].split('|')
            if len(parts)==6: trends.append(parts)
        elif line.startswith('FIX:'): fix_actions.append(line[4:])
        elif line.startswith('LATENCY:'): latency_data.append(line[8:].split('|'))
        elif line.startswith('SLA:'): sla_data.append(line[4:].split('|'))

    # Feature 9: Build list of available historical reports for diff view
    # Feature 14: SLA uptime tracking from historical data
    hist_reports = []
    all_hist_scores = []  # For full history chart
    sla_counts = {}  # component -> {up: N, total: N}
    if script_dir:
        for jf in sorted(glob_mod.glob(os.path.join(script_dir, 'VCF-Health-Report_*.json')), reverse=True):
            try:
                with open(jf, 'r') as fj:
                    jd = json.load(fj)
                    entry = {'file': os.path.basename(jf), 'date': jd.get('date','?'), 'grade': jd.get('grade','?'), 'score': jd.get('score',0)}
                    hist_reports.append(entry)
                    all_hist_scores.append(entry)
                    # Compute SLA from component data
                    for c in jd.get('components', []):
                        cn = c.get('name','?')
                        if cn not in sla_counts: sla_counts[cn] = {'up': 0, 'total': 0}
                        sla_counts[cn]['total'] += 1
                        if c.get('fail', 0) == 0: sla_counts[cn]['up'] += 1
            except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
    # Add current run to history, SLA, and diff view
    current_entry = {'file': os.path.basename(output_file).replace('.html','.json'), 'date': meta.get('date','?'), 'grade': meta.get('grade','?'), 'score': int(meta.get('score',0))}
    hist_reports.insert(0, current_entry)
    all_hist_scores.append(current_entry)
    for c in components:
        cn = c['name']
        if cn not in sla_counts: sla_counts[cn] = {'up': 0, 'total': 0}
        sla_counts[cn]['total'] += 1
        if c['fail'] == 0: sla_counts[cn]['up'] += 1

    def esc(s): return html_mod.escape(str(s))
    def gc(g):
        if g in ('A','B+'): return '#27ae60'
        if g=='B': return '#f39c12'
        if g=='C': return '#e67e22'
        return '#e74c3c'
    def badge(s):
        c={'PASS':'#27ae60','WARN':'#f39c12','FAIL':'#e74c3c','N/A':'#95a5a6'}.get(s,'#95a5a6')
        return f'<span class="badge" style="background:{c};">{esc(s)}</span>'

    grade = meta.get('grade','?')
    color = gc(grade)
    score = int(meta.get('score','0'))
    p_count = int(meta.get('passed','0'))
    w_count = int(meta.get('warnings','0'))
    f_count = int(meta.get('failed','0'))
    total = int(meta.get('total','1'))

    # Group results by section
    sections = {}
    sec_order = []
    for r in results:
        m = re.match(r'\[(PASS|FAIL|WARN)\]\s*\[([^\]]+)\]\s*(.*)', r)
        if m:
            st, sec, msg = m.group(1), m.group(2), m.group(3)
            if sec not in sections: sections[sec] = []; sec_order.append(sec)
            sections[sec].append((st, msg))

    # SVG donut chart
    def donut_svg(p, w, f, size=140):
        t = p + w + f
        if t == 0: return ''
        r = size/2 - 10
        cx = cy = size/2
        c = 2 * math.pi * r
        segs = [('#27ae60', p), ('#f39c12', w), ('#e74c3c', f)]
        svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        offset = -c/4  # start at top
        for col, val in segs:
            if val == 0: continue
            dash = (val/t) * c
            svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="18" stroke-dasharray="{dash:.1f} {c-dash:.1f}" stroke-dashoffset="{-offset:.1f}" stroke-linecap="round"/>'
            offset += dash
        svg += f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="22" font-weight="800" fill="var(--text)">{score}%</text>'
        svg += '</svg>'
        return svg

    # SVG sparkline for trend
    def sparkline_svg(trend_data, width=200, height=40):
        scores = []
        try: scores.append(score)
        except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
        for t in trend_data:
            try: scores.append(int(t[5].replace('%','')))
            except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
        scores.reverse()
        if len(scores) < 2: return ''
        mn, mx = min(scores), max(scores)
        rng = mx - mn if mx != mn else 1
        pts = []
        for i, s in enumerate(scores):
            x = (i / (len(scores)-1)) * (width - 10) + 5
            y = height - 5 - ((s - mn) / rng) * (height - 10)
            pts.append(f'{x:.1f},{y:.1f}')
        poly = ' '.join(pts)
        last = pts[-1]
        return f'<svg width="{width}" height="{height}" style="vertical-align:middle;"><polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="{last.split(",")[0]}" cy="{last.split(",")[1]}" r="4" fill="{color}"/></svg>'

    # ── Customer logo (base64-encoded for inline embedding) ───────────
    _logo_html = ''
    _logo_path = os.environ.get('CUSTOMER_LOGO', '').strip().strip('"').strip("'")
    if _logo_path:
        # Normalize path separators for cross-platform compatibility
        _logo_path = _logo_path.replace('\\', '/')
        if os.path.isfile(_logo_path):
            try:
                _logo_size = os.path.getsize(_logo_path)
                if _logo_size <= 512_000:  # max 500 KB
                    _ext = os.path.splitext(_logo_path)[1].lower()
                    _mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                                 '.gif': 'image/gif', '.svg': 'image/svg+xml', '.bmp': 'image/bmp'}
                    _mime = _mime_map.get(_ext) or mimetypes.guess_type(_logo_path)[0] or ''
                    if _mime:
                        with open(_logo_path, 'rb') as _lf:
                            _logo_b64 = base64.b64encode(_lf.read()).decode()
                        _logo_html = f'<img src="data:{_mime};base64,{_logo_b64}" class="customer-logo" alt="Customer Logo" />'
                else:
                    print(f"[LOGO] Skipped — file too large ({_logo_size} bytes)", file=sys.stderr)
            except Exception as _logo_err:
                print(f"[LOGO] Error reading {_logo_path}: {_logo_err}", file=sys.stderr)
        else:
            print(f"[LOGO] File not found: {_logo_path}", file=sys.stderr)

    h = f'''<!DOCTYPE html>
    <html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>VCF Health Report — Virtual Control LLC — {esc(meta.get("date",""))}</title>
    <style>
    /* Customer logo */
    .customer-logo{{max-height:40px;vertical-align:middle;margin-right:10px;border-radius:4px}}
    .hdr-title-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
    /* Feature 14: Expandable result details */
    .rr .detail-toggle{{cursor:pointer;color:var(--text2);font-size:.75em;margin-left:8px}}
    .rr .detail-box{{display:none;margin:4px 0 4px 50px;padding:6px 10px;background:var(--hover);border-radius:4px;font-size:.82em;font-family:monospace;white-space:pre-wrap;word-break:break-all;color:var(--text2)}}
    .rr .detail-box.open{{display:block}}
    /* Feature 12: Dependency map */
    .dep-map{{text-align:center;padding:12px 0}}
    .dep-map svg text{{font-family:'Segoe UI',sans-serif}}
    /* Feature 13: ETA badges */
    .eta{{font-size:.72em;padding:1px 6px;border-radius:3px;background:var(--border);color:var(--text2);margin-left:6px;white-space:nowrap}}
    /* Feature 9: Diff view */
    .diff-bar{{display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap}}
    .diff-bar select{{padding:4px 8px;border:1px solid var(--border2);border-radius:4px;background:var(--card);color:var(--text);font-size:.82em}}
    .diff-result{{display:none}}.diff-result.open{{display:block}}
    .diff-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:.85em}}.diff-grid .dside{{background:var(--card);padding:10px;border-radius:6px;border:1px solid var(--border)}}
    .diff-grid .dside h4{{margin-bottom:6px;font-size:.9em}}
    .diff-added{{background:rgba(39,174,96,.1);padding:2px 4px;border-radius:2px}}
    .diff-removed{{background:rgba(231,76,60,.1);padding:2px 4px;border-radius:2px}}
    /* Feature 12: Executive/Technical toggle */
    .exec-view .card,.exec-view #details,.exec-view #trend,.exec-view #diff,.exec-view #depmap{{display:none}}
    .exec-view #summary,.exec-view .grade-row,.exec-view #exec-summary,.exec-view #components,.exec-view #failures,.exec-view #actions{{display:block!important}}
    .exec-view .grade-row{{display:flex!important}}
    /* Feature 14: SLA bars */
    .sla-bar{{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:.85em}}
    .sla-track{{flex:1;height:10px;background:var(--border);border-radius:5px;overflow:hidden}}
    .sla-fill{{height:100%;border-radius:5px}}
    .sla-pct{{width:50px;text-align:right;font-weight:600;font-size:.82em}}
    /* Feature 13: Full history chart */
    .hist-chart{{padding:8px 0}}
    /* Feature 15: Playbook export */
    .playbook-btn{{margin-top:8px}}
    /* Fix action log */
    .fix-item{{padding:4px 8px;margin:2px 0;background:rgba(39,174,96,.08);border-left:3px solid var(--green);border-radius:3px;font-size:.85em}}
    /* v7.0: Heatmap calendar */
    .heatmap{{display:flex;flex-wrap:wrap;gap:2px;padding:8px 0}}
    .hm-cell{{width:11px;height:11px;border-radius:2px;cursor:pointer;transition:transform .1s}}
    .hm-cell:hover{{transform:scale(1.6);z-index:1}}
    .hm-label{{font-size:.7em;color:var(--text2);width:25px;text-align:right;line-height:13px;padding-right:3px}}
    /* v7.0: Component mini timeline */
    .comp-timeline{{display:flex;gap:1px;height:18px;align-items:flex-end}}
    .ct-bar{{flex:1;min-width:3px;border-radius:1px 1px 0 0;transition:height .2s}}
    /* v7.0: Keyboard shortcut hints */
    .kbd{{display:inline-block;padding:1px 5px;font-size:.7em;background:var(--hover);border:1px solid var(--border2);border-radius:3px;font-family:monospace;color:var(--text2);margin-left:4px;vertical-align:middle}}
    /* v7.0: Focus indicators for a11y */
    a:focus-visible,.btn:focus-visible,input:focus-visible{{outline:2px solid var(--hdr2);outline-offset:2px;border-radius:3px}}
    .sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}}
    </style>
    <style>
    :root{{--bg:#f0f2f5;--card:#fff;--text:#2c3e50;--text2:#7f8c8d;--border:#ecf0f1;--border2:#dee2e6;--hover:#f8f9fa;--hdr1:#1a5276;--hdr2:#2980b9;--green:#27ae60;--yellow:#f39c12;--orange:#e67e22;--red:#e74c3c;--gray:#95a5a6}}
    [data-theme="dark"]{{--bg:#1a1a2e;--card:#16213e;--text:#e0e0e0;--text2:#8899aa;--border:#2a2a4a;--border2:#3a3a5a;--hover:#1e2a4a;--hdr1:#0d1b2a;--hdr2:#1b3a5c}}
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{font-family:'Segoe UI',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;transition:background .3s,color .3s}}
    .layout{{display:flex;min-height:100vh}}
    .sidebar{{width:220px;background:var(--card);border-right:1px solid var(--border);padding:16px 0;position:fixed;height:100vh;overflow-y:auto;z-index:100;transition:transform .3s}}
    .sidebar h4{{padding:8px 16px;font-size:.8em;text-transform:uppercase;color:var(--text2);letter-spacing:.05em}}
    .sidebar a{{display:block;padding:6px 16px;color:var(--text);text-decoration:none;font-size:.82em;border-left:3px solid transparent;transition:all .15s;word-wrap:break-word;overflow-wrap:break-word;line-height:1.3}}
    .sidebar a:hover,.sidebar a.active{{background:var(--hover);border-left-color:var(--hdr2)}}
    .sidebar .grade-badge{{display:inline-block;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px;font-size:.7em;font-weight:700;color:#fff;margin-right:6px}}
    .main{{margin-left:220px;padding:24px;max-width:1000px;flex:1}}
    .toolbar{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center}}
    .toolbar .spacer{{flex:1}}
    .btn{{padding:6px 14px;border:1px solid var(--border2);border-radius:6px;background:var(--card);color:var(--text);cursor:pointer;font-size:.82em;transition:all .15s;display:inline-flex;align-items:center;gap:4px}}
    .btn:hover{{background:var(--hover);border-color:var(--text2)}}
    .btn.active{{background:var(--hdr2);color:#fff;border-color:var(--hdr2)}}
    .filter-btn[data-active="true"]{{opacity:1}}.filter-btn[data-active="false"]{{opacity:.4}}
    .hdr{{background:linear-gradient(135deg,var(--hdr1),var(--hdr2));color:#fff;padding:32px;border-radius:12px;margin-bottom:20px}}
    .hdr h1{{font-size:1.6em;font-weight:700}}.hdr .sub{{opacity:.85;font-size:.9em;margin-top:2px}}
    .hdr .meta-row{{margin-top:12px;display:flex;gap:20px;font-size:.85em;opacity:.9;flex-wrap:wrap}}
    .grade-row{{display:flex;gap:24px;margin-bottom:20px;flex-wrap:wrap;align-items:stretch}}
    .grade-card{{background:var(--card);border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.08);flex:1;min-width:200px}}
    .grade-card.main-grade{{display:flex;align-items:center;gap:20px}}
    .circle{{width:90px;height:90px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2em;font-weight:800;color:#fff;flex-shrink:0}}
    .donut-card{{display:flex;align-items:center;gap:16px}}
    .donut-legend{{font-size:.85em}}.donut-legend div{{margin:3px 0}}.donut-legend .dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}}
    .bar-o{{background:var(--border);border-radius:8px;height:14px;width:100%;margin-top:8px;overflow:hidden}}
    .bar-i{{height:100%;border-radius:8px;transition:width .5s}}
    .card{{background:var(--card);border-radius:12px;padding:20px 24px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
    .card h3{{font-size:1.05em;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid var(--border);display:flex;align-items:center;justify-content:space-between;cursor:pointer}}
    .card h3 .toggle{{font-size:.7em;color:var(--text2);transition:transform .2s}}
    .card h3 .toggle.collapsed{{transform:rotate(-90deg)}}
    .card .body{{overflow:hidden;transition:max-height .3s ease}}
    .card .body.collapsed{{max-height:0!important;padding:0}}
    table{{width:100%;border-collapse:collapse;font-size:.88em}}
    th{{background:var(--hover);text-align:left;padding:8px 10px;font-weight:600;border-bottom:2px solid var(--border2)}}
    td{{padding:8px 10px;border-bottom:1px solid var(--border)}}
    tr:hover td{{background:var(--hover)}}.num{{text-align:center;font-weight:600}}
    .badge{{color:#fff;padding:2px 10px;border-radius:3px;font-weight:600;font-size:.82em}}
    .rr{{display:flex;align-items:center;padding:5px 0;border-bottom:1px solid var(--border);font-size:.88em}}
    .rr:last-child{{border-bottom:none}}.rb{{width:48px;text-align:center;flex-shrink:0;font-weight:700}}.rm{{flex:1}}
    .rr.filter-hidden{{display:none}}
    .fi,.wi{{padding:8px 12px;margin-bottom:5px;border-radius:6px;font-size:.88em}}
    .fi{{background:rgba(231,76,60,.08);border-left:4px solid var(--red)}}.wi{{background:rgba(243,156,18,.08);border-left:4px solid var(--yellow)}}
    .ri{{padding:10px 14px;margin-bottom:6px;border-radius:6px;font-size:.88em;display:flex;align-items:flex-start;gap:8px}}
    .ri.fail-ri{{background:rgba(231,76,60,.06);border-left:4px solid var(--red)}}
    .ri.warn-ri{{background:rgba(243,156,18,.06);border-left:4px solid var(--yellow)}}
    .ri .fix{{color:var(--text2);margin-top:4px;font-size:.86em}}
    .ri input[type=checkbox]{{margin-top:3px;flex-shrink:0;cursor:pointer}}
    .ri.checked{{opacity:.5;text-decoration:line-through}}
    .exec{{background:rgba(243,156,18,.1);border-left:4px solid var(--yellow);padding:12px 16px;border-radius:6px;margin-bottom:16px;font-size:.92em;display:flex;align-items:center;gap:10px}}
    .exec .copy-btn{{margin-left:auto;flex-shrink:0}}
    .sh{{font-weight:600;color:var(--text);padding:6px 0 3px;border-bottom:2px solid var(--hdr2);margin:8px 0 4px;font-size:.92em}}
    .dt td,.dt th{{text-align:center}}
    .du{{color:var(--red);font-weight:600}}.dd{{color:var(--green);font-weight:600}}.ds{{color:var(--gray)}}
    .sparkline-row{{display:flex;align-items:center;gap:12px;margin-top:8px;font-size:.85em;color:var(--text2)}}
    .ft{{text-align:center;color:var(--text2);font-size:.8em;margin-top:24px;padding:12px 0;border-top:1px solid var(--border)}}
    .ts-live{{font-size:.8em;color:var(--text2);margin-left:8px}}
    .toast{{position:fixed;bottom:24px;right:24px;background:#2c3e50;color:#fff;padding:10px 20px;border-radius:8px;font-size:.88em;opacity:0;transition:opacity .3s;z-index:999;pointer-events:none}}
    .toast.show{{opacity:1}}
    @media(max-width:768px){{.sidebar{{transform:translateX(-220px)}}.main{{margin-left:0}}.grade-row{{flex-direction:column}}.sidebar.open{{transform:translateX(0)}}.mob-toggle{{display:block!important}}}}
    @media print{{.sidebar,.toolbar,.mob-toggle,.copy-btn,.toggle,input[type=checkbox]{{display:none!important}}.main{{margin-left:0}}.card .body{{max-height:none!important}}body{{background:#fff;color:#000}}.card,.grade-card{{box-shadow:none;border:1px solid #ddd;break-inside:avoid}}.hdr{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}.badge{{print-color-adjust:exact;-webkit-print-color-adjust:exact}}}}
    </style></head><body>
    <div class="toast" id="toast" role="alert" aria-live="polite"></div>
    <a href="#summary" class="sr-only">Skip to main content</a>
    <button class="btn mob-toggle" style="display:none;position:fixed;top:8px;left:8px;z-index:200" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="Toggle navigation menu">Menu</button>
    <div class="layout">
    <nav class="sidebar" id="sidebar" role="navigation" aria-label="Report sections">
    <h4>Navigation</h4>
    <a href="#summary">Summary</a>
    <a href="#components">Components</a>
    '''

    # Sidebar section links
    for sec in sec_order:
        h += f'<a href="#sec-{esc(sec.replace(" ","-").replace("/","-"))}">{esc(sec)}</a>\n'

    h += '<a href="#depmap">Dependencies</a>\n'
    if failures: h += '<a href="#failures">Failures</a>\n'
    if warnings: h += '<a href="#warnings">Warnings</a>\n'
    if remediations: h += '<a href="#actions">Actions</a>\n'
    h += '<a href="#details">All Results</a>\n'
    if trends: h += '<a href="#trend">Trend</a>\n'
    if len(hist_reports) >= 2: h += '<a href="#diff">Diff View</a>\n'
    if sla_counts: h += '<a href="#sla">SLA Uptime</a>\n'
    if len(all_hist_scores) >= 2: h += '<a href="#history">History</a>\n'
    if fix_actions: h += '<a href="#fixlog">Auto-Fix Log</a>\n'
    if latency_data: h += '<a href="#latency">Latency</a>\n'
    if len(all_hist_scores) >= 2: h += '<a href="#heatmap">Heatmap</a>\n'

    h += f'''<div style="padding:16px;margin-top:auto;border-top:1px solid var(--border);">
    <div style="font-size:.8em;color:var(--text2);">Report generated</div>
    <div class="ts-live" id="ts-live">{esc(meta.get("date",""))}</div>
    </div>
    </nav>
    <main class="main" role="main" aria-label="Health check report">
    <div class="toolbar" role="toolbar" aria-label="Report controls">
    <button class="btn filter-btn" data-active="true" data-filter="PASS" onclick="toggleFilter('PASS',this)" style="color:var(--green)">Pass</button>
    <button class="btn filter-btn" data-active="true" data-filter="WARN" onclick="toggleFilter('WARN',this)" style="color:var(--yellow)">Warn</button>
    <button class="btn filter-btn" data-active="true" data-filter="FAIL" onclick="toggleFilter('FAIL',this)" style="color:var(--red)">Fail</button>
    <div class="spacer"></div>
    <button class="btn" onclick="toggleView()" id="view-btn" aria-label="Toggle executive view (E)">Executive View <span class="kbd">E</span></button>
    <button class="btn" onclick="toggleTheme()" id="theme-btn" aria-label="Toggle dark mode (D)">Dark Mode <span class="kbd">D</span></button>
    <button class="btn" onclick="exportCSV()" aria-label="Export CSV">CSV</button>
    <button class="btn" onclick="exportPlaybook()" aria-label="Export playbook (P)">Playbook <span class="kbd">P</span></button>
    <button class="btn" onclick="window.print()" aria-label="Print report">Print</button>
    </div>

    <div class="hdr" id="summary">
    <div class="hdr-title-row">{_logo_html}<h1>VCF 9.0 Environment Health Check</h1></div>
    <div class="sub">Automated infrastructure assessment &mdash; v8.0 &mdash; Powered by Virtual Control LLC'''
    customer = os.environ.get('CUSTOMER_NAME','')
    if customer: h += f' &mdash; Prepared for {esc(customer)}'
    h += f'''</div>
    <div class="meta-row">
    <span>Date: {esc(meta.get("date",""))}</span>
    <span>Duration: {esc(meta.get("duration",""))}</span>'''

    vc_v = meta.get('vc_version','')
    sddc_v = meta.get('sddc_version','')
    if vc_v and vc_v != '?': h += f'<span>vCenter: {esc(vc_v)}</span>'
    if sddc_v and sddc_v != '?': h += f'<span>SDDC: {esc(sddc_v)}</span>'
    h += '</div></div>\n'

    # Executive summary with copy button
    es = meta.get('exec_summary','')
    if es:
        h += f'<div class="exec" id="exec-summary"><strong>Executive Summary:</strong>&nbsp;{esc(es)}<button class="btn copy-btn" onclick="copySummary()">Copy</button></div>\n'

    # Grade row: grade circle + donut + sparkline
    donut = donut_svg(p_count, w_count, f_count)
    spark = sparkline_svg(trends)

    h += f'''<div class="grade-row">
    <div class="grade-card main-grade">
    <div class="circle" style="background:{color};">{esc(grade)}</div>
    <div style="flex:1;">
    <h2 style="color:{color};margin:0 0 2px;">{esc(meta.get("grade_label",""))}</h2>
    <div style="font-size:.88em;color:var(--text2);">{esc(meta.get("grade_desc",""))}</div>
    <div style="margin-top:6px;font-size:.9em;"><strong>{score}%</strong>
    &nbsp;<span style="color:var(--green);">{p_count}P</span>
    &nbsp;<span style="color:var(--yellow);">{w_count}W</span>
    &nbsp;<span style="color:var(--red);">{f_count}F</span>
    &nbsp;<span style="color:var(--text2);">/ {total}</span></div>
    <div class="bar-o"><div class="bar-i" style="width:{score}%;background:{color};"></div></div>
    </div></div>
    <div class="grade-card donut-card">
    {donut}
    <div class="donut-legend">
    <div><span class="dot" style="background:var(--green);"></span>Passed: {p_count}</div>
    <div><span class="dot" style="background:var(--yellow);"></span>Warnings: {w_count}</div>
    <div><span class="dot" style="background:var(--red);"></span>Failed: {f_count}</div>
    </div></div>'''

    if spark:
        h += f'''<div class="grade-card">
    <div style="font-size:.85em;font-weight:600;margin-bottom:4px;">Score Trend</div>
    {spark}
    <div class="sparkline-row">Last {len(trends)+1} runs</div>
    </div>'''

    h += '</div>\n'

    # Component breakdown
    # v7.0 Feature 15: Build per-component history from JSON reports
    comp_hist = {}
    if script_dir:
        for jf in sorted(glob_mod.glob(os.path.join(script_dir, 'VCF-Health-Report_*.json')))[-10:]:
            try:
                with open(jf, 'r') as fj:
                    jd = json.load(fj)
                    for c in jd.get('components', []):
                        cn = c.get('name','?')
                        if cn not in comp_hist: comp_hist[cn] = []
                        total = c.get('pass',0) + c.get('warn',0) + c.get('fail',0)
                        pct = round(c.get('pass',0) / max(total,1) * 100) if total > 0 else 0
                        comp_hist[cn].append(pct)
            except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
    # Add current run to comp_hist
    for c in components:
        cn = c['name']
        if cn not in comp_hist: comp_hist[cn] = []
        total = c['pass'] + c['warn'] + c['fail']
        pct = round(c['pass'] / max(total,1) * 100) if total > 0 else 0
        comp_hist[cn].append(pct)

    h += '<div class="card" id="components"><h3 onclick="toggleCard(this)">Component Breakdown <span class="toggle">&#9660;</span></h3><div class="body">\n<table>\n<tr><th>Component</th><th class="num">Pass</th><th class="num">Warn</th><th class="num">Fail</th><th class="num">Status</th><th class="num" style="width:80px;">Trend</th></tr>\n'
    for c in components:
        # v7.0 Feature 15: mini timeline bars
        timeline_html = ''
        ch = comp_hist.get(c['name'], [])
        if len(ch) >= 2:
            timeline_html = '<div class="comp-timeline">'
            for pct in ch[-10:]:
                bar_h = max(2, int(pct * 16 / 100))
                bar_c = '#27ae60' if pct >= 80 else ('#f39c12' if pct >= 50 else '#e74c3c')
                timeline_html += f'<div class="ct-bar" style="height:{bar_h}px;background:{bar_c};"></div>'
            timeline_html += '</div>'
        h += f'<tr><td>{esc(c["name"])}</td><td class="num">{c["pass"]}</td><td class="num">{c["warn"]}</td><td class="num">{c["fail"]}</td><td class="num">{badge(c["status"])}</td><td class="num">{timeline_html}</td></tr>\n'
    h += '</table></div></div>\n'

    # Trend
    if trends:
        h += f'<div class="card" id="trend"><h3 onclick="toggleCard(this)">Trend (Last {len(trends)} Runs) <span class="toggle">&#9660;</span></h3><div class="body">\n<table class="dt">\n'
        h += '<tr><th>Date</th><th>Grade</th><th>Pass</th><th>Warn</th><th>Fail</th><th>Score</th></tr>\n'
        h += f'<tr style="background:rgba(39,174,96,.08);"><td>{esc(meta.get("date","")[:16])}</td><td style="color:{color};font-weight:700;">{esc(grade)}</td><td>{p_count}</td><td>{w_count}</td><td>{f_count}</td><td>{score}%</td></tr>\n'
        for t in trends:
            h += f'<tr><td>{esc(t[0])}</td><td>{esc(t[1])}</td><td>{esc(t[2])}</td><td>{esc(t[3])}</td><td>{esc(t[4])}</td><td>{esc(t[5])}</td></tr>\n'
        h += '</table></div></div>\n'

    # Delta
    if history:
        h += f'<div class="card"><h3 onclick="toggleCard(this)">Delta from Last Run ({esc(history.get("prev_date",""))}) <span class="toggle">&#9660;</span></h3><div class="body">\n<table class="dt">\n'
        h += '<tr><th>Metric</th><th>Previous</th><th>Current</th><th>Delta</th></tr>\n'
        pg = history.get('prev_grade','?')
        gd_cls = 'ds' if grade == pg else ''
        gd_txt = '=' if grade == pg else f'{esc(pg)} &rarr; {esc(grade)}'
        h += f'<tr><td>Grade</td><td>{esc(pg)}</td><td style="color:{color};font-weight:700;">{esc(grade)}</td><td class="{gd_cls}">{gd_txt}</td></tr>\n'
        for lbl, ck, pk, good_dir in [('Passed','passed','prev_passed','up'),('Warnings','warnings','prev_warnings','down'),('Failed','failed','prev_failed','down')]:
            try:
                cv,pv = int(meta.get(ck,0)), int(history.get(pk,0))
                d = cv - pv
                sign = '+' if d > 0 else ''
                ds = f'{sign}{d}' if d != 0 else '='
                if d == 0: cls = 'ds'
                elif (d > 0 and good_dir == 'up') or (d < 0 and good_dir == 'down'): cls = 'dd'
                else: cls = 'du'
            except Exception: ds, cls, cv, pv = '?', 'ds', meta.get(ck,'?'), history.get(pk,'?')
            h += f'<tr><td>{lbl}</td><td>{pv}</td><td>{cv}</td><td class="{cls}">{ds}</td></tr>\n'
        h += '</table></div></div>\n'

    # Feature 12: Component Dependency Map (SVG)
    def dep_map_svg():
        nodes = [
            ('vCenter', 250, 40), ('SDDC Manager', 100, 140), ('NSX', 250, 140),
            ('ESXi Hosts', 250, 240), ('VCF Ops', 400, 140), ('Fleet', 400, 240)
        ]
        edges = [
            ('SDDC Manager', 'vCenter'), ('SDDC Manager', 'NSX'), ('NSX', 'ESXi Hosts'),
            ('vCenter', 'ESXi Hosts'), ('VCF Ops', 'vCenter'), ('Fleet', 'vCenter')
        ]
        node_map = {n[0]: n for n in nodes}
        comp_status = {}
        for c in components:
            cn = c['name']
            if 'vcenter' in cn.lower(): comp_status['vCenter'] = c['status']
            elif 'sddc' in cn.lower(): comp_status['SDDC Manager'] = c['status']
            elif 'nsx' in cn.lower(): comp_status['NSX'] = c['status']
            elif 'infra' in cn.lower(): comp_status['ESXi Hosts'] = c['status']
            elif 'ops' in cn.lower() or 'operation' in cn.lower(): comp_status['VCF Ops'] = c['status']
            elif 'fleet' in cn.lower() or 'vrslcm' in cn.lower(): comp_status['Fleet'] = c['status']
        fill = {'PASS':'#27ae60','WARN':'#f39c12','FAIL':'#e74c3c','N/A':'#95a5a6'}
        svg = '<svg width="500" height="290" viewBox="0 0 500 290">'
        for src, dst in edges:
            x1,y1 = node_map[src][1], node_map[src][2]
            x2,y2 = node_map[dst][1], node_map[dst][2]
            svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--border2)" stroke-width="2" stroke-dasharray="4"/>'
        for name, x, y in nodes:
            st = comp_status.get(name, 'N/A')
            fc = fill.get(st, '#95a5a6')
            svg += f'<rect x="{x-55}" y="{y-18}" width="110" height="36" rx="8" fill="{fc}" opacity="0.15" stroke="{fc}" stroke-width="2"/>'
            svg += f'<circle cx="{x-40}" cy="{y}" r="5" fill="{fc}"/>'
            svg += f'<text x="{x+2}" y="{y+5}" text-anchor="middle" font-size="11" fill="var(--text)" font-weight="600">{name}</text>'
        svg += '</svg>'
        return svg

    h += f'<div class="card" id="depmap"><h3 onclick="toggleCard(this)">Component Dependencies <span class="toggle">&#9660;</span></h3><div class="body"><div class="dep-map">{dep_map_svg()}</div></div></div>\n'

    # Feature 9: Diff View
    if len(hist_reports) >= 2:
        opts = ''.join(f'<option value="{esc(r["file"])}">{esc(r["date"])} — Grade {esc(r["grade"])} ({r["score"]}%){"  [Current]" if i==0 else ""}</option>' for i,r in enumerate(hist_reports))
        h += f'''<div class="card" id="diff"><h3 onclick="toggleCard(this)">Compare Runs (Diff View) <span class="toggle">&#9660;</span></h3><div class="body">
    <div class="diff-bar">
    <label>Run A:</label><select id="diff-a">{opts}</select>
    <label>Run B:</label><select id="diff-b">{opts}</select>
    <button class="btn" onclick="loadDiff()">Compare</button>
    </div>
    <div id="diff-result" class="diff-result"></div>
    </div></div>\n'''

    # Failures
    if failures:
        h += f'<div class="card" id="failures"><h3 style="color:var(--red);" onclick="toggleCard(this)">Failures ({len(failures)}) <span class="toggle">&#9660;</span></h3><div class="body">\n'
        for i,fl in enumerate(failures): h += f'<div class="fi">{i+1}. {esc(fl)}</div>\n'
        h += '</div></div>\n'
    if warnings:
        h += f'<div class="card" id="warnings"><h3 style="color:var(--yellow);" onclick="toggleCard(this)">Warnings ({len(warnings)}) <span class="toggle">&#9660;</span></h3><div class="body">\n'
        for i,wl in enumerate(warnings): h += f'<div class="wi">{i+1}. {esc(wl)}</div>\n'
        h += '</div></div>\n'

    # Recommendations with checkboxes + Feature 13 ETA
    if remediations:
        h += f'<div class="card" id="actions"><h3 style="color:var(--hdr2);" onclick="toggleCard(this)">Recommended Actions ({len(remediations)}) <span class="toggle">&#9660;</span></h3><div class="body">\n'
        for i, rem in enumerate(remediations):
            parts = rem.split('|', 3)
            if len(parts) >= 3:
                rt, rm, rr = parts[0], parts[1], parts[2]
                eta = parts[3] if len(parts) > 3 else '~15m'
                cls = 'fail-ri' if rt == 'FAIL' else 'warn-ri'
                eta_html = f'<span class="eta">{esc(eta)}</span>' if eta else ''
                h += f'<div class="ri {cls}" id="rem-{i}"><input type="checkbox" onchange="toggleChecked(this,{i})"><div><strong style="color:{"var(--red)" if rt=="FAIL" else "var(--yellow)"};">[{esc(rt)}]</strong> {esc(rm)}{eta_html}<div class="fix"><strong>Fix:</strong> {esc(rr)}</div></div></div>\n'
        h += '</div></div>\n'

    # Feature 14: SLA Uptime Tracker
    if sla_counts:
        h += '<div class="card" id="sla"><h3 onclick="toggleCard(this)">SLA Uptime Tracker <span class="toggle">&#9660;</span></h3><div class="body">\n'
        h += '<div style="font-size:.82em;color:var(--text2);margin-bottom:8px;">Based on {0} health check runs. A component is "UP" when it has zero failures.</div>\n'.format(max(v['total'] for v in sla_counts.values()) if sla_counts else 0)
        for cn in sorted(sla_counts.keys()):
            sc = sla_counts[cn]
            pct = round(sc['up'] / sc['total'] * 100, 1) if sc['total'] > 0 else 0
            bar_color = '#27ae60' if pct >= 99 else ('#f39c12' if pct >= 95 else '#e74c3c')
            h += f'<div class="sla-bar"><span style="width:140px;flex-shrink:0;">{esc(cn)}</span><div class="sla-track"><div class="sla-fill" style="width:{pct}%;background:{bar_color};"></div></div><span class="sla-pct" style="color:{bar_color};">{pct}%</span><span style="font-size:.75em;color:var(--text2);width:60px;">{sc["up"]}/{sc["total"]}</span></div>\n'
        h += '</div></div>\n'

    # Feature 13: Full History Chart
    if len(all_hist_scores) >= 2:
        sorted_hist = sorted(all_hist_scores, key=lambda x: x.get('date',''))
        chart_w, chart_h = 700, 160
        n = len(sorted_hist)
        pts_line = []
        for i, entry in enumerate(sorted_hist):
            x = 50 + (i / max(n-1, 1)) * (chart_w - 80)
            y = chart_h - 30 - (entry.get('score', 0) / 100) * (chart_h - 50)
            pts_line.append((x, y, entry))
        poly = ' '.join(f'{x:.1f},{y:.1f}' for x,y,_ in pts_line)
        fill_pts = f'50,{chart_h-30} ' + poly + f' {pts_line[-1][0]:.1f},{chart_h-30}'
        hist_svg = f'<svg width="100%" viewBox="0 0 {chart_w} {chart_h}" style="max-width:{chart_w}px;">'
        # Grid lines
        for pct in [25, 50, 75, 100]:
            gy = chart_h - 30 - (pct / 100) * (chart_h - 50)
            hist_svg += f'<line x1="50" y1="{gy:.1f}" x2="{chart_w-30}" y2="{gy:.1f}" stroke="var(--border)" stroke-width="1"/>'
            hist_svg += f'<text x="45" y="{gy+4:.1f}" text-anchor="end" font-size="10" fill="var(--text2)">{pct}%</text>'
        # Fill area
        hist_svg += f'<polygon points="{fill_pts}" fill="{color}" opacity="0.1"/>'
        # Line
        hist_svg += f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        # Points + labels
        for i, (x, y, entry) in enumerate(pts_line):
            gc_val = gc(entry.get('grade','?'))
            hist_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{gc_val}" stroke="#fff" stroke-width="1.5"/>'
            # Show date label for every Nth point
            if i % max(1, n // 8) == 0 or i == n - 1:
                lbl = entry.get('date','')[:10]
                hist_svg += f'<text x="{x:.1f}" y="{chart_h-12}" text-anchor="middle" font-size="9" fill="var(--text2)">{esc(lbl)}</text>'
        hist_svg += '</svg>'
        h += f'<div class="card" id="history"><h3 onclick="toggleCard(this)">Health Score History ({n} runs) <span class="toggle">&#9660;</span></h3><div class="body"><div class="hist-chart">{hist_svg}</div></div></div>\n'

    # Feature 7: Latency Table
    if latency_data:
        h += '<div class="card" id="latency"><h3 onclick="toggleCard(this)">Network Latency <span class="toggle">&#9660;</span></h3><div class="body">\n'
        h += '<table><tr><th>Endpoint</th><th class="num">Latency (ms)</th><th class="num">Status</th></tr>\n'
        for ld in latency_data:
            if len(ld) >= 2:
                host = ld[0]
                ms = float(ld[1]) if ld[1] != '-1' else -1
                if ms < 0:
                    st_badge = badge('FAIL')
                    ms_text = 'Unreachable'
                elif ms > 200:
                    st_badge = badge('WARN')
                    ms_text = f'{ms:.1f}'
                else:
                    st_badge = badge('PASS')
                    ms_text = f'{ms:.1f}'
                h += f'<tr><td>{esc(host)}</td><td class="num">{ms_text}</td><td class="num">{st_badge}</td></tr>\n'
        h += '</table></div></div>\n'

    # Feature 8: Fix Actions Log
    if fix_actions:
        h += f'<div class="card" id="fixlog"><h3 onclick="toggleCard(this)">Auto-Remediation Log ({len(fix_actions)} actions) <span class="toggle">&#9660;</span></h3><div class="body">\n'
        for fa in fix_actions:
            h += f'<div class="fix-item">{esc(fa)}</div>\n'
        h += '</div></div>\n'

    # v7.0 Feature 14: Heatmap Calendar (GitHub-style, last 90 days)
    if len(all_hist_scores) >= 2:
        from datetime import datetime,timezone, timedelta
        # Build date->grade map
        date_grades = {}
        for entry in all_hist_scores:
            d = entry.get('date','')[:10]
            if d: date_grades[d] = entry.get('grade','?')
        # Add current run
        cur_date = meta.get('date','')[:10]
        if cur_date: date_grades[cur_date] = grade
        # Generate 90-day grid
        today = datetime.now()
        hm_cells = ''
        for i in range(89, -1, -1):
            d = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            g = date_grades.get(d, '')
            if g:
                colors_map = {'A':'#27ae60','B+':'#2ecc71','B':'#f1c40f','C':'#e67e22','D':'#e74c3c','F':'#c0392b'}
                c = colors_map.get(g, '#95a5a6')
                hm_cells += f'<div class="hm-cell" style="background:{c};" title="{d}: Grade {g}"></div>'
            else:
                hm_cells += f'<div class="hm-cell" style="background:var(--border);" title="{d}: No data"></div>'
        h += f'<div class="card" id="heatmap"><h3 onclick="toggleCard(this)">Health Heatmap (90 days) <span class="toggle">&#9660;</span></h3><div class="body">'
        h += f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;font-size:.75em;color:var(--text2);"><span>90 days ago</span><div style="flex:1"></div><span>Today</span></div>'
        h += f'<div class="heatmap">{hm_cells}</div>'
        h += '<div style="display:flex;gap:4px;align-items:center;margin-top:6px;font-size:.72em;color:var(--text2);">Legend: '
        for lg, lc in [('A','#27ae60'),('B','#f1c40f'),('C','#e67e22'),('D/F','#e74c3c'),('No data','var(--border)')]:
            h += f'<div class="hm-cell" style="background:{lc};width:10px;height:10px;"></div><span>{lg}</span> '
        h += '</div></div></div>\n'

    # Detailed results with per-section collapsible cards
    h += f'<div id="details">\n'
    for sec in sec_order:
        sec_id = sec.replace(' ','-').replace('/','-')
        sec_results = sections[sec]
        sp = sum(1 for s,_ in sec_results if s=='PASS')
        sw = sum(1 for s,_ in sec_results if s=='WARN')
        sf = sum(1 for s,_ in sec_results if s=='FAIL')
        status_icon = '<span style="color:var(--red);">&#9679;</span>' if sf > 0 else ('<span style="color:var(--yellow);">&#9679;</span>' if sw > 0 else '<span style="color:var(--green);">&#9679;</span>')
        h += f'<div class="card" id="sec-{esc(sec_id)}"><h3 onclick="toggleCard(this)">{status_icon} {esc(sec)} <span style="font-weight:400;font-size:.8em;color:var(--text2);">({sp}P {sw}W {sf}F)</span> <span class="toggle">&#9660;</span></h3><div class="body">\n'
        for st, msg in sec_results:
            colors = {'PASS':'var(--green)','FAIL':'var(--red)','WARN':'var(--yellow)'}
            h += f'<div class="rr" data-status="{st}"><div class="rb" style="color:{colors.get(st,"#999")};">{st}</div><div class="rm">{esc(msg)}</div></div>\n'
        h += '</div></div>\n'
    h += '</div>\n'

    _cust = os.environ.get('CUSTOMER_NAME','')
    _env_label = os.environ.get('CUSTOMER_ENV_LABEL','VCF 9.0 Lab Environment')
    h += f'''<div class="ft" role="contentinfo">{_logo_html}VCF 9.0 Environment Health Check v8.0 &mdash; {esc(meta.get("date",""))}<br>
    Target: {esc(_env_label)} &mdash; Duration: {esc(meta.get("duration",""))}<br>'''
    if _cust: h += f'Prepared for {esc(_cust)}<br>'
    h += f'''&copy; 2026 Virtual Control LLC. All rights reserved.</div>
    </main></div>
    <script>
    // Dark mode
    function toggleTheme(){{
      const d=document.documentElement;
      const dark=d.getAttribute('data-theme')==='dark';
      d.setAttribute('data-theme',dark?'':'dark');
      document.getElementById('theme-btn').textContent=dark?'Dark Mode':'Light Mode';
      localStorage.setItem('vcf-theme',dark?'':'dark');
    }}
    (function(){{const t=localStorage.getItem('vcf-theme');if(t){{document.documentElement.setAttribute('data-theme',t);if(t==='dark')document.getElementById('theme-btn').textContent='Light Mode';}}}})();

    // Collapsible sections
    function toggleCard(el){{
      const body=el.nextElementSibling;
      const tog=el.querySelector('.toggle');
      if(body){{body.classList.toggle('collapsed');}}
      if(tog){{tog.classList.toggle('collapsed');}}
    }}

    // Filter
    function toggleFilter(status,btn){{
      const active=btn.getAttribute('data-active')==='true';
      btn.setAttribute('data-active',active?'false':'true');
      document.querySelectorAll('.rr[data-status="'+status+'"]').forEach(el=>{{
        el.classList.toggle('filter-hidden',active);
      }});
    }}

    // Copy summary
    function copySummary(){{
      const txt=document.getElementById('exec-summary')?.textContent.replace('Copy','').trim();
      if(txt)navigator.clipboard.writeText(txt).then(()=>showToast('Summary copied!'));
    }}
    function showToast(msg){{
      const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
      setTimeout(()=>t.classList.remove('show'),2000);
    }}

    // Checklist persistence
    function toggleChecked(cb,idx){{
      const ri=document.getElementById('rem-'+idx);
      if(ri)ri.classList.toggle('checked',cb.checked);
      const state=JSON.parse(localStorage.getItem('vcf-checklist')||'{{}}');
      state[idx]=cb.checked;localStorage.setItem('vcf-checklist',JSON.stringify(state));
    }}
    (function(){{const state=JSON.parse(localStorage.getItem('vcf-checklist')||'{{}}');
    Object.entries(state).forEach(([k,v])=>{{
      const ri=document.getElementById('rem-'+k);
      if(ri){{const cb=ri.querySelector('input');if(cb){{cb.checked=v;if(v)ri.classList.add('checked');}}}}
    }});}})();

    // Live timestamp
    (function(){{
      const el=document.getElementById('ts-live');
      if(!el)return;
      const gen=new Date('{esc(meta.get("date",""))}');
      if(isNaN(gen))return;
      function update(){{
        const diff=Math.floor((Date.now()-gen.getTime())/60000);
        if(diff<1)el.textContent='Just now';
        else if(diff<60)el.textContent=diff+'m ago';
        else if(diff<1440)el.textContent=Math.floor(diff/60)+'h '+diff%60+'m ago';
        else el.textContent=Math.floor(diff/1440)+'d ago';
      }}
      update();setInterval(update,60000);
    }})();

    // Sidebar active tracking
    (function(){{
      const links=document.querySelectorAll('.sidebar a[href^="#"]');
      const obs=new IntersectionObserver(entries=>{{
        entries.forEach(e=>{{if(e.isIntersecting){{
          links.forEach(l=>l.classList.remove('active'));
          const a=document.querySelector('.sidebar a[href="#'+e.target.id+'"]');
          if(a)a.classList.add('active');
        }}}});
      }},{{threshold:0.3}});
      document.querySelectorAll('[id]').forEach(el=>obs.observe(el));
    }})();

    // Feature 10: CSV Export from HTML
    function exportCSV(){{
      const rows=[['Status','Component','Message']];
      document.querySelectorAll('.rr[data-status]').forEach(el=>{{
        const st=el.getAttribute('data-status');
        const msg=el.querySelector('.rm')?.textContent||'';
        const card=el.closest('.card');
        const sec=card?card.querySelector('h3')?.textContent.replace(/[\\u25BC\\u25CF]/g,'').trim().split('(')[0].trim():'';
        rows.push([st,sec,msg]);
      }});
      const csv=rows.map(r=>r.map(c=>'"'+c.replace(/"/g,'""')+'"').join(',')).join('\\n');
      const blob=new Blob([csv],{{type:'text/csv'}});
      const a=document.createElement('a');
      a.href=URL.createObjectURL(blob);
      a.download='VCF-Health-Report.csv';
      a.click();
      showToast('CSV exported!');
    }}

    // Feature 9: Diff View — load two JSON reports and compare
    async function loadDiff(){{
      const a=document.getElementById('diff-a')?.value;
      const b=document.getElementById('diff-b')?.value;
      const out=document.getElementById('diff-result');
      if(!a||!b||!out)return;
      if(a===b){{showToast('Select two different runs');return;}}
      out.classList.add('open');
      out.innerHTML='Loading...';
      try{{
        const dir=window.location.href.substring(0,window.location.href.lastIndexOf('/')+1);
        const [ra,rb]=await Promise.all([fetch(dir+a).then(r=>r.json()),fetch(dir+b).then(r=>r.json())]);
        let html='<div class="diff-grid"><div class="dside"><h4>'+ra.date+' — Grade '+ra.grade+' ('+ra.score+'%)</h4>';
        html+='<div>Pass: '+ra.summary.passed+' | Warn: '+ra.summary.warnings+' | Fail: '+ra.summary.failed+'</div>';
        html+='</div><div class="dside"><h4>'+rb.date+' — Grade '+rb.grade+' ('+rb.score+'%)</h4>';
        html+='<div>Pass: '+rb.summary.passed+' | Warn: '+rb.summary.warnings+' | Fail: '+rb.summary.failed+'</div>';
        html+='</div></div>';
        // Find differences in results
        const setA=new Set((ra.results||[]).map(r=>r.status+'|'+r.message));
        const setB=new Set((rb.results||[]).map(r=>r.status+'|'+r.message));
        const added=[...setB].filter(x=>!setA.has(x));
        const removed=[...setA].filter(x=>!setB.has(x));
        if(added.length||removed.length){{
          html+='<div style="margin-top:12px;">';
          if(removed.length){{
            html+='<div style="margin-bottom:8px;font-weight:600;">Removed in Run B:</div>';
            removed.forEach(r=>html+='<div class="diff-removed">'+r+'</div>');
          }}
          if(added.length){{
            html+='<div style="margin:8px 0;font-weight:600;">New in Run B:</div>';
            added.forEach(r=>html+='<div class="diff-added">'+r+'</div>');
          }}
          html+='</div>';
        }}else{{html+='<div style="margin-top:12px;color:var(--text2);">No differences found.</div>';}}
        out.innerHTML=html;
      }}catch(e){{out.innerHTML='Error loading reports. Ensure JSON files are in the same directory.';}}
    }}

    // Feature 12: Executive / Technical view toggle
    function toggleView(){{
      const body=document.body;
      const btn=document.getElementById('view-btn');
      body.classList.toggle('exec-view');
      const isExec=body.classList.contains('exec-view');
      btn.textContent=isExec?'Technical View':'Executive View';
      if(isExec)btn.classList.add('active');else btn.classList.remove('active');
    }}

    // Feature 15: Export Remediation Playbook as Markdown
    function exportPlaybook(){{
      const actions=document.querySelectorAll('.ri');
      if(!actions.length){{showToast('No remediation actions to export');return;}}
      let md='# VCF Health Check — Remediation Playbook\\n';
      md+='Generated: '+new Date().toISOString().slice(0,19).replace("T"," ")+'\\n\\n';
      md+='## Summary\\n';
      const fails=document.querySelectorAll('.ri.fail-ri').length;
      const warns=document.querySelectorAll('.ri.warn-ri').length;
      md+='- **Critical (FAIL):** '+fails+'\\n';
      md+='- **Warnings (WARN):** '+warns+'\\n\\n';
      md+='## Critical Actions\\n\\n';
      let idx=1;
      actions.forEach(a=>{{
        if(!a.classList.contains('fail-ri'))return;
        const txt=a.querySelector('div>div, div')?.textContent||a.textContent||'';
        const parts=txt.replace(/\\[FAIL\\]/,'').trim().split('Fix:');
        const issue=parts[0]?.trim()||'';
        const fix=parts[1]?.trim()||'';
        md+='### '+idx+'. '+issue+'\\n';
        if(fix)md+='**Remediation:** '+fix+'\\n';
        md+='\\n';
        idx++;
      }});
      md+='## Warnings\\n\\n';
      actions.forEach(a=>{{
        if(!a.classList.contains('warn-ri'))return;
        const txt=a.querySelector('div>div, div')?.textContent||a.textContent||'';
        const parts=txt.replace(/\\[WARN\\]/,'').trim().split('Fix:');
        const issue=parts[0]?.trim()||'';
        const fix=parts[1]?.trim()||'';
        md+='### '+idx+'. '+issue+'\\n';
        if(fix)md+='**Remediation:** '+fix+'\\n';
        md+='\\n';
        idx++;
      }});
      md+='---\\n*Generated by VCF Health Check v8.0*\\n';
      const blob=new Blob([md],{{type:'text/markdown'}});
      const a=document.createElement('a');
      a.href=URL.createObjectURL(blob);
      a.download='VCF-Remediation-Playbook.md';
      a.click();
      showToast('Playbook exported!');
    }}

    // v7.0 Feature 16: Keyboard shortcuts
    document.addEventListener('keydown',function(e){{
      if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT'||e.target.tagName==='TEXTAREA')return;
      switch(e.key.toLowerCase()){{
        case 'd': toggleTheme(); break;
        case 'e': toggleView(); break;
        case 'p': if(!e.ctrlKey&&!e.metaKey){{exportPlaybook();e.preventDefault();}} break;
        case '?': showToast('Keys: D=dark mode, E=exec view, P=playbook, 1-9=sections'); break;
      }}
      // Number keys 1-9 jump to sections
      if(e.key>='1'&&e.key<='9'){{
        const links=document.querySelectorAll('.sidebar a[href^=\"#\"]');
        const idx=parseInt(e.key)-1;
        if(links[idx]){{links[idx].click();}}
      }}
    }});
    </script></body></html>'''

    with open(output_file, 'w', encoding='utf-8') as f: f.write(h)


def json_report():
    """Generate JSON health check report.
    Env: HTML_DATA_FILE, JSON_REPORT_FILE, CUSTOMER_NAME, CUSTOMER_ENV_LABEL"""
    import json, os, re

    data_file = os.environ.get('HTML_DATA_FILE', '')
    output_file = os.environ.get('JSON_REPORT_FILE', '')
    if not data_file or not output_file:
        import sys; sys.exit(0)

    results, failures, warnings, remediations = [], [], [], []
    components, meta, history, trends = [], {}, {}, []

    try:
        with open(data_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.rstrip('\n')
                if line.startswith('R:'): results.append(line[2:])
                elif line.startswith('F:'): failures.append(line[2:])
                elif line.startswith('W:'): warnings.append(line[2:])
                elif line.startswith('REM:'):
                    parts = line[4:].split('|', 2)
                    if len(parts)==3:
                        remediations.append({'type':parts[0],'message':parts[1],'fix':parts[2]})
                elif line.startswith('C:'):
                    parts = line[2:].split('|')
                    if len(parts)==5:
                        components.append({'name':parts[0],'pass':int(parts[1]),'warn':int(parts[2]),'fail':int(parts[3]),'status':parts[4]})
                elif line.startswith('META:'): k,v=line[5:].split('=',1); meta[k]=v
                elif line.startswith('HIST:'): k,v=line[5:].split('=',1); history[k]=v
                elif line.startswith('TREND:'):
                    parts=line[6:].split('|')
                    if len(parts)==6:
                        trends.append({'date':parts[0],'grade':parts[1],'passed':parts[2],'warnings':parts[3],'failed':parts[4],'score':parts[5]})

        # Parse results into structured format
        structured_results = []
        for r in results:
            m = re.match(r'\[(PASS|FAIL|WARN)\]\s*\[([^\]]+)\]\s*(.*)', r)
            if m:
                structured_results.append({'status':m.group(1),'component':m.group(2),'message':m.group(3)})

        report = {
            'version': '6.0',
            'date': meta.get('date',''),
            'duration': meta.get('duration',''),
            'grade': meta.get('grade',''),
            'grade_label': meta.get('grade_label',''),
            'score': int(meta.get('score','0')),
            'summary': {
                'passed': int(meta.get('passed','0')),
                'warnings': int(meta.get('warnings','0')),
                'failed': int(meta.get('failed','0')),
                'total': int(meta.get('total','0'))
            },
            'executive_summary': meta.get('exec_summary',''),
            'versions': {
                'vcenter': meta.get('vc_version',''),
                'sddc_manager': meta.get('sddc_version','')
            },
            'components': components,
            'results': structured_results,
            'failures': failures,
            'warnings': warnings,
            'remediations': remediations,
            'trend': trends,
            'delta': history if history else None,
            'customer': os.environ.get('CUSTOMER_NAME', ''),
            'environment_label': os.environ.get('CUSTOMER_ENV_LABEL', 'VCF 9.0 Lab Environment'),
            'copyright': '(c) 2026 Virtual Control LLC. All rights reserved.'
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        pass


def check_snapshots():
    """Check for stale VM snapshots. Reads VM list from stdin.
    Env: VC_SESSION, VCENTER, SNAP_HOURS"""
    import sys,json,urllib.request,ssl,os
    from concurrent.futures import ThreadPoolExecutor,as_completed
    from datetime import datetime,timezone,timedelta
    ctx=ssl._create_unverified_context()
    session=os.environ.get('VC_SESSION','')
    vcenter=os.environ.get('VCENTER','')
    if not session or not vcenter: print('ERROR'); sys.exit()
    try: vms=json.load(sys.stdin)
    except Exception: print('ERROR'); sys.exit()
    cutoff=datetime.now(timezone.utc)-timedelta(hours=int(os.environ.get('SNAP_HOURS','72')))
    def check_vm(vm):
        if not isinstance(vm,dict): return 0,[]
        vmid=vm.get('vm','')
        vmname=vm.get('name','?')
        try:
            req=urllib.request.Request(f'https://{vcenter}/api/vcenter/vm/{vmid}/snapshots',headers={'vmware-api-session-id':session})
            resp=urllib.request.urlopen(req,context=ctx,timeout=10)
            snaps=json.loads(resp.read())
            if not isinstance(snaps,list): return 0,[]
            found=[]
            for s in snaps:
                ct=s.get('creation_time',s.get('creationTime',''))
                if ct:
                    try:
                        sdt=datetime.fromisoformat(ct.replace('Z','+00:00'))
                        if sdt<cutoff:
                            age_h=int((datetime.now(timezone.utc)-sdt).total_seconds()/3600)
                            found.append(f'{vmname}:{s.get("name","?")},{age_h}h')
                    except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
            return len(snaps),found
        except Exception: return 0,[]
    total=0; stale=[]
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures={pool.submit(check_vm,vm):vm for vm in (vms if isinstance(vms,list) else [])}
        for f in as_completed(futures,timeout=120):
            try:
                cnt,found=f.result(timeout=30)
                total+=cnt; stale.extend(found)
            except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
    print(f'TOTAL:{total}')
    for s in stale[:5]: print(f'STALE:{s}')


def check_unclaimed_disks():
    """Check for unclaimed vSAN disks. Reads host list from stdin.
    Env: SESSION, VCENTER"""
    import sys,json,os,ssl,urllib.request
    from concurrent.futures import ThreadPoolExecutor,as_completed
    try:
        session=os.environ['SESSION']; vcenter=os.environ['VCENTER']
        ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        raw=json.load(sys.stdin)
        hosts=raw if isinstance(raw,list) else raw.get('elements',[]) if isinstance(raw,dict) else []
        def check_host(h):
            if not isinstance(h,dict): return None
            cs=str(h.get('connection_state',h.get('connectionState',''))).upper()
            if cs != 'CONNECTED': return None
            hid=h.get('host',h.get('name',''))
            hname=h.get('name',hid)
            try:
                body=json.dumps({'host':{'_typeName':'ManagedObjectReference','type':'HostSystem','value':hid}}).encode()
                req=urllib.request.Request(f'https://{vcenter}/sdk/vim25/9.0.0.0/vsan/VsanVcDiskManagementSystem/vsan-disk-management-system/QueryDisksForVsan',
                    data=body,headers={'vmware-api-session-id':session,'Content-Type':'application/json'},method='POST')
                resp=urllib.request.urlopen(req,context=ctx,timeout=15)
                disks=json.loads(resp.read())
                if isinstance(disks,dict): disks=disks.get('returnval',disks.get('result',[]))
                if not isinstance(disks,list): return None
                unclaimed=[d for d in disks if isinstance(d,dict) and str(d.get('state','')).lower()=='eligible']
                if unclaimed: return f'WARN|{hname}|{len(unclaimed)} unclaimed disk(s)'
            except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
            return None
        found_any=False
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures={pool.submit(check_host,h):h for h in hosts}
            for f in as_completed(futures,timeout=120):
                try:
                    r=f.result(timeout=30)
                    if r: found_any=True; print(r)
                except Exception as _e: sys.stderr.write(f'pyerr: {_e}\n')
        if not found_any: print('OK|all|0')
    except Exception as e: print(f'ERROR|{e}')


def check_cluster_capacity():
    """Check cluster CPU/memory capacity. Reads PropertyCollector response from stdin.
    Env: CPU_WARN, CPU_CRIT, MEM_WARN, MEM_CRIT"""
    import sys,json,os
    try:
        cpu_warn=int(os.environ.get('CPU_WARN',70)); cpu_crit=int(os.environ.get('CPU_CRIT',85))
        mem_warn=int(os.environ.get('MEM_WARN',70)); mem_crit=int(os.environ.get('MEM_CRIT',85))
        d=json.load(sys.stdin)
        objects=d.get('objects',[]); rv=d.get('returnval',None)
        if isinstance(rv,dict): objects=rv.get('objects',[])
        if not objects: print('ERROR|no data'); sys.exit(0)
        props={}
        for obj in objects:
            for p in obj.get('propSet',[]):
                props[p['name']]=p.get('val',p.get('value',''))
        # Try usageSummary (vSphere 8+)
        usage=props.get('summary.usageSummary',None)
        if isinstance(usage,dict):
            cpu_demand=usage.get('cpuDemandMhz',0); cpu_cap=usage.get('cpuCapacityMhz',0)
            mem_demand=usage.get('memDemandMb',0); mem_cap=usage.get('memCapacityMb',0)
            if cpu_cap>0:
                cpu_pct=int((cpu_demand/cpu_cap)*100)
                print(f'CPU|{cpu_pct}|{cpu_demand}|{cpu_cap}|{cpu_warn}|{cpu_crit}')
            if mem_cap>0:
                mem_pct=int((mem_demand/mem_cap)*100)
                print(f'MEM|{mem_pct}|{mem_demand}|{mem_cap}|{mem_warn}|{mem_crit}')
        else:
            # Fallback: effectiveCpu/totalCpu
            tc=props.get('summary.totalCpu',0); ec=props.get('summary.effectiveCpu',0)
            tm=props.get('summary.totalMemory',0); em=props.get('summary.effectiveMemory',0)
            tc=int(tc) if tc else 0; ec=int(ec) if ec else 0
            tm=int(tm) if tm else 0; em=int(em) if em else 0
            if tc>0:
                used_cpu=tc-ec; cpu_pct=int((used_cpu/tc)*100)
                print(f'CPU|{cpu_pct}|{used_cpu}|{tc}|{cpu_warn}|{cpu_crit}')
            if tm>0:
                used_mem=tm-em; mem_pct=int((used_mem/tm)*100)
                tm_gb=round(tm/1073741824,1); em_gb=round(em/1073741824,1)
                print(f'MEM|{mem_pct}|{round((tm-em)/1073741824,1)}|{tm_gb}|{mem_warn}|{mem_crit}')
    except Exception as e: print(f'ERROR|{e}')


if __name__ == "__main__":
    _commands = {
        "html-report": html_report,
        "json-report": json_report,
        "check-snapshots": check_snapshots,
        "check-unclaimed-disks": check_unclaimed_disks,
        "check-cluster-capacity": check_cluster_capacity,
    }
    _cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if _cmd not in _commands:
        print(f"Usage: {sys.argv[0]} <command>", file=sys.stderr)
        print("Commands: " + ", ".join(sorted(_commands)), file=sys.stderr)
        sys.exit(1)
    _commands[_cmd]()
