"""按测试隔离执行评分。"""
import argparse, json, math, os, signal, subprocess, sys, time, shlex, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
from netlab.testing import ROOT

LABS = ['lab01_packets','lab02_reassembly','lab03_transport','lab04_router','lab05_routing','lab06_proxy']

def run(path, action, env, timeout):
    stdout = tempfile.TemporaryFile(); stderr = tempfile.TemporaryFile()
    proc = subprocess.Popen([sys.executable, '-m', 'netlab.worker', str(path), action], stdout=stdout, stderr=stderr, env=env, start_new_session=True, cwd=ROOT)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        stderr.seek(0); err = stderr.read(1048576).decode('utf8', 'replace'); stdout.close(); stderr.close()
        return None, f'测试超时（预算 {timeout} 秒），已终止进程组；退出码 {proc.returncode}。\n' + err
    # 即使工作进程已经返回，也清理其残留子进程。
    try: os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError: pass
    def tail(stream):
        stream.seek(0, 2); size = stream.tell(); stream.seek(max(0, size - 1048576))
        return ('[输出超过 1 MiB，已截断前部]\n' if size > 1048576 else '') + stream.read().decode('utf8', 'replace')
    out = tail(stdout); err = tail(stderr)
    stdout.close(); stderr.close()
    if proc.returncode:
        return None, f'进程退出码 {proc.returncode}\n' + (err or out)
    try: return json.loads(out.splitlines()[-1]), err
    except (ValueError, IndexError): return None, '结果无法解析：' + out + err

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lab', choices=LABS)
    parser.add_argument('--mode', choices=['student','reference'], default='student')
    parser.add_argument('--suite', choices=['public','full'], default='public')
    parser.add_argument('--impl-root')
    parser.add_argument('--hidden-root', default=os.environ.get('HIDDEN_ROOT', str(ROOT / 'instructor/tests')))
    parser.add_argument('--timeout', type=float, default=float(os.environ.get('NETLAB_TIMEOUT', '8')))
    parser.add_argument('--test', help='仅执行完整测试 ID 或其后缀，所得分数仅用于调试')
    parser.add_argument('--report-dir', default='reports')
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0: parser.error('超时时间必须是有限正数')
    started = time.monotonic()
    env = os.environ.copy()
    env['PYTHONHASHSEED'] = '0'
    env['NETLAB_RANDOM_SEED'] = '0'
    if args.impl_root: env['NETLAB_IMPL_ROOT'] = str(Path(args.impl_root).resolve())
    elif args.mode == 'reference': env['NETLAB_IMPL_ROOT'] = str(ROOT / 'instructor/reference')
    elif not os.environ.get('NETLAB_IMPL_ROOT'): env.pop('NETLAB_IMPL_ROOT', None)
    reports = []
    for lab in [args.lab] if args.lab else LABS:
        groups = [('public', ROOT / 'labs' / lab / 'test_public.py')]
        if args.suite == 'full': groups.append(('hidden', Path(args.hidden_root) / f'test_{lab}.py'))
        score = 0
        for group, path in groups:
            weight = 1 if args.suite == 'public' else (.6 if group == 'public' else .4)
            tests, error = run(path, 'collect', env, args.timeout)
            if not tests:
                print(f"失败 {lab} {group} 测试收集失败：{error or '没有测试'}\n复现：make grade LAB={lab} MODE={args.mode} SUITE={args.suite}", file=sys.stderr)
                reports.append({'lab':lab,'suite':group,'test':'收集失败','points':100*weight,'earned':0,'ok':False,'detail':error or '没有测试'})
                continue
            total = sum(t['points'] for t in tests)
            if abs(total - 100) > 1e-6:
                reports.append({'lab':lab,'suite':group,'test':'评分配置错误','points':100*weight,'earned':0,'ok':False,'detail':f'测试权重合计 {total}，应为 100'})
                continue
            for t in tests:
                if args.test and not (t['id'] == args.test or t['id'].endswith(args.test)):
                    continue
                result, error = run(path, t['id'], env, args.timeout)
                ok = bool(result and result['ok'])
                earned = t['points'] * weight if ok else 0
                score += earned
                parts = [sys.executable, '-m', 'netlab.grade', '--lab', lab, '--mode', args.mode, '--suite', args.suite, '--test', t['id']]
                if env.get('NETLAB_IMPL_ROOT'): parts += ['--impl-root', env['NETLAB_IMPL_ROOT']]
                if args.suite == 'full': parts += ['--hidden-root', str(Path(args.hidden_root).resolve())]
                command = shlex.join(parts)
                detail = (result or {}).get('detail', '') or error
                reports.append({'lab':lab,'suite':group,'test':t['id'],'category':t['category'],'points':t['points']*weight,'earned':earned,'ok':ok,'detail':detail,'reproduce':command})
                if not ok: print(f'失败 {lab} {t["id"]}\n{detail}\n复现：{command}', file=sys.stderr)
        maximum = sum(r['points'] for r in reports if r['lab'] == lab) if args.test else 100
        print(f'{lab}: {score:.2f}/{maximum:.2f}' + ('（单测调试）' if args.test else ''))
    if args.test and not reports:
        reports.append({'lab':args.lab or '全部', 'suite':args.suite, 'test':'筛选失败', 'points':0, 'earned':0, 'ok':False, 'detail':'没有匹配的测试'})
    out = Path(args.report_dir); out.mkdir(parents=True, exist_ok=True)
    by_lab = {}
    for r in reports:
        item = by_lab.setdefault(r['lab'], {'earned':0, 'maximum':0, 'categories':{}})
        item['earned'] += r['earned']; item['maximum'] += r['points']
        cat = item['categories'].setdefault(r.get('category', 'collection'), {'earned':0, 'maximum':0})
        cat['earned'] += r['earned']; cat['maximum'] += r['points']
    report = {'mode':args.mode, 'suite':args.suite, 'python':sys.version, 'duration_seconds':round(time.monotonic()-started, 3), 'limits':{'timeout_seconds':args.timeout, 'cpu_seconds':int(env.get('NETLAB_CPU','5')), 'memory_mb':int(env.get('NETLAB_MEMORY_MB','512')), 'file_mb':int(env.get('NETLAB_FILE_MB','64'))}, 'filtered':bool(args.test), 'test_filter':args.test, 'results':reports, 'labs':by_lab, 'score':sum(r['earned'] for r in reports), 'maximum':sum(r['points'] for r in reports) if args.test else 100*(1 if args.lab else len(LABS))}
    (out / 'grade.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    suite = ET.Element('testsuite', tests=str(len(reports)), failures=str(sum(not r['ok'] for r in reports)))
    for r in reports:
        case = ET.SubElement(suite, 'testcase', classname=r['lab'], name=r['test'])
        if not r['ok']: ET.SubElement(case, 'failure', message='测试失败').text = r['detail'] + '\n复现：' + r.get('reproduce','')
    ET.ElementTree(suite).write(out / 'junit.xml', encoding='utf-8', xml_declaration=True)
    return int(any(not r['ok'] for r in reports))
if __name__ == '__main__': sys.exit(main())
