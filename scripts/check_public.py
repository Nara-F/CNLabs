"""学生公开版的静态检查和 starter 基线检查。"""
import argparse, ast, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS = ['lab01_packets', 'lab02_reassembly', 'lab03_transport', 'lab04_router', 'lab05_routing', 'lab06_proxy']
BASELINE = dict(zip(LABS, [0, 4, 4, 0, 0, 5]))
HEADINGS = ['Overview','Learning Objectives','Prerequisites','Background','Required Readings','Architecture Overview','Starter Code Guide','Tasks','Interface Specifications','Behavioral Requirements','Edge Cases','Build & Run','Debugging Guide','Testing','Grading','Submission','FAQ','Further Exploration']

def audit():
    errors = []
    for lab in LABS:
        folder = ROOT/'labs'/lab
        for name in ('README.md','HINTS.md','api.py','student.py','test_public.py'):
            if not (folder/name).is_file(): errors.append(f'{lab} 缺少 {name}')
        headings = re.findall(r'^##\s+(.+)$',(folder/'README.md').read_text(encoding='utf8'),re.M)
        if len(headings)!=18 or any(expected not in actual for expected,actual in zip(HEADINGS,headings)):
            errors.append(f'{lab} 的 18 节结构不匹配')
        tree=ast.parse((folder/'test_public.py').read_text(encoding='utf8'))
        tests=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')]
        points=[]
        for test in tests:
            decorations=[d for d in test.decorator_list if isinstance(d,ast.Call) and isinstance(d.func,ast.Name) and d.func.id=='graded']
            try:
                if len(decorations)!=1: raise ValueError()
                args={k.arg:ast.literal_eval(k.value) for k in decorations[0].keywords}
                if not isinstance(args['category'],str) or not args['category'] or isinstance(args['points'],bool) or not isinstance(args['points'],(int,float)) or args['points']<=0: raise ValueError()
                points.append(args['points'])
            except (ValueError,KeyError,TypeError): errors.append(f'{lab} {test.name} 评分元数据无效')
        if not tests or abs(sum(points)-100)>1e-9: errors.append(f'{lab} 公开测试权重不是 100')
    for path in ROOT.rglob('*.py'):
        if any(p in path.parts for p in ('__pycache__','.git','dist','reports')): continue
        tree=ast.parse(path.read_text(encoding='utf8'))
        for node in ast.walk(tree):
            modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            if any(m=='instructor' or m.startswith('instructor.') for m in modules): errors.append(f'{path.relative_to(ROOT)} 导入教师内容')
    for path in ROOT.rglob('*.md'):
        if any(p in path.parts for p in ('.git','dist','reports')): continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf8')):
            target=target.split('#')[0]
            if target and not re.match(r'\w+://|mailto:',target) and not (path.parent/target).exists(): errors.append(f'{path.relative_to(ROOT)} 链接不存在: {target}')
    forbidden = [p for p in ('instructor','evidence','scripts/validate.py','scripts/course_audit.py','scripts/snapshot_validation.py') if (ROOT/p).exists()]
    if forbidden: errors.append('存在教师私有材料: '+', '.join(forbidden))
    if errors: print('\n'.join(errors),file=sys.stderr); return False
    print('公开版静态检查通过：六实验结构、测试权重、导入和文档链接。'); return True

def validate_starter():
    env=os.environ.copy(); env.pop('NETLAB_IMPL_ROOT',None); env.pop('HIDDEN_ROOT',None)
    command=[sys.executable,'-m','netlab.grade','--mode','student','--suite','public','--report-dir','reports/starter-baseline']
    path=ROOT/'reports/starter-baseline/grade.json'
    path.unlink(missing_ok=True)
    result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if not path.exists(): print('未生成评分报告：'+result.stderr,file=sys.stderr); return False
    data=json.loads(path.read_text(encoding='utf8')); tests=data['results']
    scores={lab:round(value['earned'],6) for lab,value in data['labs'].items()}
    ok=(result.returncode!=0 and len(tests)==130 and scores==BASELINE and not any(t['test'] in ('收集失败','评分配置错误') for t in tests))
    print(f'公开 starter 基线：{scores}，测试 {len(tests)} 项。')
    if not ok: print('starter 基线不符，查看 reports/starter-baseline/grade.json 和 junit.xml。',file=sys.stderr)
    return ok

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--audit',action='store_true'); parser.add_argument('--validate-starter',action='store_true'); args=parser.parse_args()
    if not args.audit and not args.validate_starter: parser.error('请选择检查')
    ok=True
    if args.audit: ok=audit() and ok
    if args.validate_starter: ok=validate_starter() and ok
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
