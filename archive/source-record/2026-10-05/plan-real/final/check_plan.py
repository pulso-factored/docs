#!/usr/bin/env python3
"""check_plan.py - machine checker of the Pulso real-system plan (final, v5).

Usage:  python check_plan.py PLAN.md [IMPROVEMENT_ENGINE_REPO] [INFRA_REPO]
        (PLAN.md may also be wp_table.csv-derived; the table, the FROZEN line, the `owners`,
        `newpaths`, `numbers` blocks and the ASK table are read from the plan file itself.)
Exit code 0 = PASS, non-zero = at least one violation (assert message names it).
With the repo arguments it also proves that every tracked path of improvement-engine main
(and every path of infra origin/main) has exactly one lane owner by the most specific glob.
"""
import re, sys, math, collections, subprocess

TIERS = 'T0 T0.5 T1a T1b T2 T3 TA T5'.split()
TI = {t: i for i, t in enumerate(TIERS)}
PACK = 'G0f G0gr CONTR CF0 FRZ0 BK0'.split()          # wave-0 enabling pack (Claude), published for Codex
DEFAULT_GATES = 'GT0 GT05 GT1A GT1B GT2 GT3'.split()    # must be reachable with every ask unanswered
USER_GATED = {'GT05m': 'model rung-up needs a local-model download (ASK-7)',
              'GTA': 'real AWS staging needs the AWS asks (ASK-17..21)'}
STANDIN = 'CMP GSI STP1 AUS PGC EVE ORC1 RPL1 SBL'.split()          # Claude stand-ins of Codex semantics
LIVEKIND = 'BKFL BKTL BKDL BKAL BKCL BKJL BKOL BKEL'.split()        # Claude live per-kind WPs
CAP = {'A': (14, 18), 'B': (18, 24), 'C': (35, 45)}                  # lane-hours per session, ASSUMPTIONS (LVL-A/B/C)
WAVES = ['W0', 'W1', 'W2', 'W3', 'W4', 'W5']


def parse(txt):
    lines = txt.splitlines()
    hi = next(i for i, l in enumerate(lines) if l.startswith('| id | name |'))
    hdr = [c.strip() for c in lines[hi].strip().strip('|').split('|')]
    rows = []
    for l in lines[hi + 2:]:
        if not l.startswith('|'):
            break
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        assert len(c) == len(hdr), ('column count', c[0], len(c), len(hdr))
        rows.append(dict(zip(hdr, c)))
    return rows


FENCE = chr(96) * 3


def block(txt, name):
    m = re.search(FENCE + name + r'\n(.*?)' + FENCE, txt, re.S)
    assert m, 'missing block ' + name
    return m.group(1)


def conv(p):
    o = ''; i = 0; b = 0
    while i < len(p):
        c = p[i]
        if p.startswith('**', i):
            o += '.*'; i += 2; continue
        if c == '*': o += '[^/]*'
        elif c == '{': o += '(?:'; b += 1
        elif c == '}': o += ')'; b -= 1
        elif c == ',' and b: o += '|'
        elif c == '.': o += r'\.'
        else: o += c
        i += 1
    return re.compile('^' + o + '$')


def rep(g):
    """a representative concrete path of a glob (for location-inside-lane checks)"""
    g = g.replace('**', 'x/y')
    g = re.sub(r'\{([^,}]*)[^}]*\}', r'\1', g)
    g = re.sub(r'\(([^|)]*)[^)]*\)', r'\1', g)
    g = re.sub(r'\[(.)[^\]]*\]', r'\1', g)
    return g.replace('*', 'x')


def analyze(txt, repo=None, infra=None, out=print, check_numbers=True, critical_out=None):
    rows = parse(txt)
    by = {r['id']: r for r in rows}
    assert len(by) == len(rows), 'duplicate id'
    F = set(re.search(r'^FROZEN: (.*)$', txt, re.M).group(1).split())
    lo = lambda r: int(r['hours_low']); hi = lambda r: int(r['hours_high']); mid = lambda r: (lo(r) + hi(r)) / 2
    deps = lambda r: [d for d in r['deps'].split(',') if d != '-']
    hard = lambda r: [d for d in deps(r) if d[0] != '~']
    opt = lambda r: [d[1:] for d in deps(r) if d[0] == '~']
    needs = lambda r: [d for d in r['needs'].split(',') if d != '-']
    asks = set(re.findall(r'^\| (ASK-\d+) \|', txt, re.M))
    assert asks, 'no ASK table'
    bare = []
    for r in rows:
        assert lo(r) <= hi(r) and lo(r) > 0, ('hours', r['id'])
        assert r['critical'] in ('Y', 'N') and r['demo_path'] in ('Y', 'N'), r['id']
        assert r['owner'] in ('CL', 'CX') and r['wave'] in WAVES and r['tier'] in TI, r['id']
        assert r['first_red'] and r['acceptance'] and r['paths'], ('empty cell', r['id'])
        assert not r['first_red'].lower().startswith('review checklist'), ('first_red is not a RED', r['id'])
        if not re.search(r'\d|green|exit|reject|equal|match|publish|merged|closed|digest|label|recorded|survive|receipt|pass|fail|refus|enforc|fire|resolv|answer|compil|valid|accepted|read back|resum|stop|replay|hash|signed|identical', r['acceptance'], re.I): bare.append(r['id'])
        for d in hard(r) + opt(r):
            assert d in by, ('dangling dep', r['id'], d)
        for d in hard(r):
            assert TI[by[d]['tier']] <= TI[r['tier']] and by[d]['wave'] <= r['wave'], ('monotone', r['id'], d)
        for n in needs(r):
            assert n in asks, ('unknown ask', r['id'], n)
    assert not bare, ('bare acceptance cells (no number, exit code, named artefact or verdict)', bare)
    # acyclic
    order = []; seen = set()
    def vis(n, p=()):
        assert n not in p, 'cycle ' + n
        if n in seen: return
        for d in hard(by[n]): vis(d, p + (n,))
        seen.add(n); order.append(n)
    for n in by: vis(n)
    lane = collections.defaultdict(set)
    for r in rows: lane[r['lane']].add(r['owner'])
    assert all(len(v) == 1 for v in lane.values()), 'lane with two owners'
    own_of = {l: next(iter(v)) for l, v in lane.items()}
    N = collections.OrderedDict()
    P = lambda *a: out(' '.join(str(x) for x in a))
    # ---- independence
    c2x = [(r['id'], d) for r in rows if r['owner'] == 'CL' for d in hard(r) if by[d]['owner'] == 'CX']
    x2c = [(r['id'], d) for r in rows if r['owner'] == 'CX' for d in hard(r) if by[d]['owner'] == 'CL' and d not in F]
    x2f = [(r['id'], d) for r in rows if r['owner'] == 'CX' for d in hard(r) if by[d]['owner'] == 'CL' and d in F]
    sw = [(r['id'], d) for r in rows for d in opt(r)]
    assert all(by[a]['owner'] == 'CL' and by[d]['owner'] == 'CX' for a, d in sw), 'optional edge must be Claude swap-in <- Codex'
    assert all(by[f]['owner'] == 'CL' for f in F), 'FROZEN must be Claude artifacts'
    assert not c2x and not x2c, ('independence violated', c2x, x2c)
    N['c2x_hard'] = len(c2x); N['x2c_nonfrozen'] = len(x2c); N['x2frozen'] = len(x2f); N['swapin_edges'] = len(sw)
    P('Claude->Codex hard edges:', len(c2x), '| Codex->Claude edges to non-frozen:', len(x2c), '| Codex->frozen:', len(x2f), '| optional swap-in edges:', len(sw))
    def anc(n, a=None):
        a = set() if a is None else a
        for d in hard(by[n]):
            if d not in a: a.add(d); anc(d, a)
        return a
    def cpm(g):
        A = anc(g) | {g}; ES = {}
        for n in [n for n in order if n in A]: ES[n] = max([ES[d] + mid(by[d]) for d in hard(by[n])] + [0])
        end = ES[g] + mid(by[g]); LF = {n: end for n in A}
        for n in reversed([n for n in order if n in A]):
            for d in hard(by[n]): LF[d] = min(LF[d], LF[n] - mid(by[n]))
        return A, ES, end, {n: LF[n] - mid(by[n]) - ES[n] for n in A}
    gates = [r['id'] for r in rows if r['id'].startswith('GT')]
    for g in DEFAULT_GATES + list(USER_GATED): assert g in gates, ('missing gate', g)
    depth = {}; chain = {}
    for g in gates:
        A = anc(g)
        assert not [x for x in A if (by[x]['owner'] == 'CX' and x not in F) or opt(by[x])], ('gate depends on Codex or swap-in', g)
        A2, ES, end, fl = cpm(g)
        n = g; ch = [g]
        while hard(by[n]):
            n = max(hard(by[n]), key=lambda d: ES[d] + mid(by[d])); ch.append(n)
        depth[g] = end; chain[g] = list(reversed(ch))
        P(g, 'serial depth %.1f h' % end, '| gate ancestors', len(A), '(all Claude or frozen) | chain', ' > '.join(chain[g]))
        N['anc_' + g] = len(A)
        N['chain_' + g] = ' > '.join(chain[g])
        N['hours_' + g] = '%d-%d' % (sum(lo(by[x]) for x in A | {g}), sum(hi(by[x]) for x in A | {g}))
        N['depth_' + g] = '%.1f' % end
    # default gates reachable with every ask unanswered
    for g in DEFAULT_GATES:
        bad = [x for x in anc(g) | {g} if needs(by[x])]
        assert not bad, ('gate needs a user ask', g, bad)
    for g, why in USER_GATED.items():
        assert [x for x in anc(g) | {g} if needs(by[x])], ('user-gated gate has no ask', g)
    P('default-reachable gates (no ask in any ancestor):', ' '.join(DEFAULT_GATES), '| user-gated:', ' '.join(USER_GATED))
    # critical column
    A, ES, end, fl = cpm('GT1B')
    crit = {n for n in A if fl[n] <= 4}
    if critical_out is not None:
        critical_out.extend(sorted(crit)); return None
    assert {r['id'] for r in rows if r['critical'] == 'Y'} == crit, 'critical column mismatch'
    ncrit = sum(r['critical'] == 'Y' for r in rows); hcrit = sum(mid(by[n]) for n in A if fl[n] <= 4)
    N['critical_wps'] = ncrit; N['critical_hours_mid'] = '%.1f' % hcrit
    P('critical to GT1B', ncrit, 'WPs, midpoint hours', hcrit)
    # demo path = exact ancestor set of GT0, Claude-only, closed, no ENV stream, no Jev, no ask
    D = {r['id'] for r in rows if r['demo_path'] == 'Y'}
    assert D == anc('GT0') | {'GT0'}, ('demo_path != ancestors of GT0', D ^ (anc('GT0') | {'GT0'}))
    assert all(by[n]['owner'] == 'CL' and not opt(by[n]) and by[n]['stream'] != 'ENV' for n in D), 'demo path must be Claude-only, no ENV stream'
    assert 'M5a' not in D, 'M5a must be out of the GT0 ancestors'
    # ---- sums, splits
    def S(f): return sum(lo(r) for r in rows if f(r)), sum(hi(r) for r in rows if f(r))
    def share(f):
        a = S(f); b = S(lambda r: f(r) and r['owner'] == 'CL')
        return a, b, '%.1f%% / %.1f%%' % (100 * b[0] / a[0], 100 * b[1] / a[1])
    a, b, s = share(lambda r: True)
    for k, f in (('all', lambda r: True), ('t1b', lambda r: TI[r['tier']] <= 3)):
        aa, bb, ss = share(f)
        assert 70 <= 100 * bb[0] / aa[0] <= 80 and 70 <= 100 * bb[1] / aa[1] <= 80, ('Claude share outside 70-80', k, ss)
        assert 20 <= 100 * (aa[0] - bb[0]) / aa[0] <= 30 and 20 <= 100 * (aa[1] - bb[1]) / aa[1] <= 30, ('Codex share outside 20-30', k, ss)
        N[k + '_total'] = '%d-%d' % aa; N[k + '_claude'] = '%d-%d' % bb; N[k + '_codex'] = '%d-%d' % (aa[0] - bb[0], aa[1] - bb[1])
        N[k + '_share_claude'] = ss; N[k + '_mid'] = '%.0f' % ((aa[0] + aa[1]) / 2)
        N[k + '_share_codex'] = '%.1f%% / %.1f%%' % (100 * (aa[0] - bb[0]) / aa[0], 100 * (aa[1] - bb[1]) / aa[1])
        P('split', k, 'total %d-%d | Claude %d-%d | Claude share %s' % (aa + bb + (ss,)))
    N['wps'] = len(rows); N['lanes'] = len(lane); N['lanes_cl'] = sum(v == 'CL' for v in own_of.values()); N['lanes_cx'] = sum(v == 'CX' for v in own_of.values())
    N['churn_total'] = '%.0f' % (1.1 * (a[0] + a[1]) / 2)
    P('WPs', len(rows), 'lanes', len(lane), '(CL %d, CX %d)' % (N['lanes_cl'], N['lanes_cx']), '| all', share(lambda r: True))
    for t in TIERS:
        sh = share(lambda r: r['tier'] == t); N['tier_' + t] = '%d-%d (CX %d-%d)' % (sh[0] + (sh[0][0] - sh[1][0], sh[0][1] - sh[1][1]))
        N['tiershare_' + t] = '%.1f' % (100 * sh[1][0] / sh[0][0]) if sh[0][0] else '-'
        P('tier', t, N['tier_' + t], 'Claude share of lows', N['tiershare_' + t])
    for w in WAVES:
        sh = share(lambda r: r['wave'] == w)
        nw = sum(r['wave'] == w for r in rows); lw = {r['lane'] for r in rows if r['wave'] == w}
        cl = sum(own_of[l] == 'CL' for l in lw)
        N['wave_' + w] = '%d-%d (%s; %d WPs; %d lanes: %d CL + %d CX)' % (sh[0] + (sh[2], nw, len(lw), cl, len(lw) - cl))
        P('wave', w, N['wave_' + w])
    dm = S(lambda r: r['id'] in D); ev = S(lambda r: r['id'] not in D)
    N['demo_wps'] = len(D); N['demo_hours'] = '%d-%d' % dm; N['demo_mid'] = '%.1f' % ((dm[0] + dm[1]) / 2)
    N['demo_pct'] = '%.1f%% / %.1f%%' % (100 * dm[0] / (dm[0] + ev[0]), 100 * dm[1] / (dm[1] + ev[1]))
    N['evolution_hours'] = '%d-%d' % ev
    P('demo path', dm, 'WPs', len(D), 'evolution', ev, N['demo_pct'])
    # independence cost of the rule
    sa = S(lambda r: r['id'] in STANDIN); sb = S(lambda r: r['id'] in LIVEKIND)
    N['indep_cost'] = '%d-%d' % (sa[0] + sb[0], sa[1] + sb[1]); N['indep_cost_standins'] = '%d-%d' % sa; N['indep_cost_livekind'] = '%d-%d' % sb
    P('independence cost (Claude stand-ins + live per-kind WPs)', N['indep_cost'])
    pk = S(lambda r: r['id'] in PACK); N['pack_hours'] = '%d-%d' % pk; N['pack_mid'] = '%.1f' % ((pk[0] + pk[1]) / 2)
    # ---- sessions model
    def sess(h, dep, c):
        cl, ch = CAP[c]; cc = (cl + ch) / 2
        f = 1.10 * dep / 7.5
        return max(1.10 * h / cc, f), max(1.10 * h / ch, f), max(1.10 * h / cl, f)
    def sfmt(h, dep, c):
        x, y, z = sess(h, dep, c); return '%.1f (%.1f-%.1f)' % (x, y, z)
    for g in DEFAULT_GATES + list(USER_GATED):
        AA = anc(g) | {g}; h = sum(mid(by[x]) for x in AA)
        for c in 'ABC': N['sess_%s_%s' % (g, c)] = sfmt(h, depth[g], c)
    AA = anc('GT0') | {'GT0'} | set(PACK); h = sum(mid(by[x]) for x in AA)
    dep = max(depth['GT0'], max(cpm(p)[2] for p in PACK))
    N['demo_pack_mid'] = '%.1f' % h
    for c in 'ABC': N['sess_GT0pack_' + c] = sfmt(h, dep, c)
    for g in DEFAULT_GATES + list(USER_GATED):
        P('sessions', g, 'depth', N['depth_' + g], 'A', N['sess_%s_A' % g], 'B', N['sess_%s_B' % g], 'C', N['sess_%s_C' % g])
    P('sessions GT0+pack', 'A', N['sess_GT0pack_A'], 'B', N['sess_GT0pack_B'], 'C', N['sess_GT0pack_C'])
    # ---- PRs per wave per team (ceil(mid/30)), lanes, ASAP width
    for w in WAVES:
        for t in ('CL', 'CX'):
            m = sum(mid(r) for r in rows if r['wave'] == w and r['owner'] == t)
            N['prs_%s_%s' % (t, w)] = math.ceil(m / 30) if m else 0
    N['prs_CL'] = ' '.join(str(N['prs_CL_' + w]) for w in WAVES); N['prs_CX'] = ' '.join(str(N['prs_CX_' + w]) for w in WAVES)
    N['prs_total_CL'] = sum(N['prs_CL_' + w] for w in WAVES); N['prs_total_CX'] = sum(N['prs_CX_' + w] for w in WAVES)
    P('PRs per wave Claude', N['prs_CL'], '(%d) | Codex' % N['prs_total_CL'], N['prs_CX'], '(%d)' % N['prs_total_CX'])
    lvl = {}
    for n in order: lvl[n] = 1 + max([lvl[d] for d in hard(by[n])] + [0])
    cnt = collections.Counter(lvl.values()); N['asap_width'] = max(cnt.values()); N['asap_levels'] = max(cnt)
    N['lanes_per_wave'] = ' '.join(str(len({r['lane'] for r in rows if r['wave'] == w})) for w in WAVES)
    P('width: lanes per wave', N['lanes_per_wave'], '| ASAP level width', N['asap_width'], 'over', N['asap_levels'], 'levels')
    # ---- lane table
    N['lane_table'] = ';'.join('%s:%d:%d-%d' % (l, sum(r['lane'] == l for r in rows), sum(lo(r) for r in rows if r['lane'] == l), sum(hi(r) for r in rows if r['lane'] == l)) for l in sorted(lane))
    # ---- paths: location inside lane
    own = block(txt, 'owners')
    RU = [(l.split(': ')[0], conv(g), len(g.replace('*', ''))) for l in own.splitlines() if l.strip() for g in l.split(': ', 1)[1].split(' ; ')]
    def owner(f):
        m = sorted([(s, l) for l, r, s in RU if r.match(f)], reverse=True)
        return None if not m or (len(m) > 1 and m[0][0] == m[1][0] and m[0][1] != m[1][1]) else m[0][1]
    assert {l.split(': ')[0] for l in own.splitlines() if l.strip()} >= set(lane), 'lane without path map'
    nexp = 0
    for r in rows:
        if r['paths'] == '@lane': continue
        nexp += 1
        for g in r['paths'].split():
            assert owner(rep(g)) == r['lane'], ('WP path outside its lane', r['id'], r['lane'], g, owner(rep(g)))
    N['wps_explicit_paths'] = nexp
    P('paths: %d WPs with explicit globs all resolve inside their lane; %d use @lane' % (nexp, len(rows) - nexp))
    npb = [l for l in block(txt, 'newpaths').splitlines() if l.strip()]
    for l in npb:
        p, ln = [x.strip() for x in l.split('->')]
        assert owner(p) == ln, ('planned new path has wrong owner', p, ln, owner(p))
    N['newpaths_checked'] = len(npb)
    P('planned new paths checked:', len(npb))
    if repo:
        fs = [f for f in subprocess.check_output(['git', '-C', repo, 'ls-files']).decode().split('\n') if f]
        if infra:
            fs += ['infra:' + f for f in subprocess.check_output(['git', '-C', infra, 'ls-tree', '-r', '--name-only', 'origin/main']).decode().split('\n') if f]
        bad = [f for f in fs if not owner(f)]
        P(len(fs), 'tracked paths (repo + infra origin/main),', len(bad), 'unowned or tied'); assert not bad, bad[:10]
        N['tracked_paths'] = len(fs)
    # ---- numbers block of the document must equal the computed values
    if not check_numbers:
        return N
    nb = {}
    for l in block(txt, 'numbers').splitlines():
        if l.strip():
            k, v = l.split(' = ', 1); nb[k.strip()] = v.strip()
    comp = {k: str(v) for k, v in N.items() if k not in ('tracked_paths',)}
    diff = {k: (nb.get(k), comp.get(k)) for k in set(nb) | set(comp) if nb.get(k) != comp.get(k) and k != 'tracked_paths'}
    assert not diff, ('numbers block differs from computation', diff)
    P('numbers block: %d values equal the computation' % len(nb))
    return N


if __name__ == '__main__':
    txt = open(sys.argv[1], encoding='utf-8').read()
    analyze(txt, sys.argv[2] if len(sys.argv) > 2 else None, sys.argv[3] if len(sys.argv) > 3 else None)
    print('PASS')
