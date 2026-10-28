"""供评分器使用的一次性进程。"""
import importlib.util, json, math, os, random, resource, sys, traceback, unittest
from pathlib import Path

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

def main():
    random.seed(int(os.getenv('NETLAB_RANDOM_SEED', '0')))
    file_limit = int(os.getenv('NETLAB_FILE_MB', '64')) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))
    resource.setrlimit(resource.RLIMIT_CPU, (int(os.getenv('NETLAB_CPU', '5')), int(os.getenv('NETLAB_CPU', '5')) + 1))
    memory = int(os.getenv('NETLAB_MEMORY_MB', '512')) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    path, action = sys.argv[1:3]
    name = '_netlab_test_module'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    tests = list(flatten(unittest.defaultTestLoader.loadTestsFromModule(module)))
    if action == 'collect':
        result = []
        for t in tests:
            method = getattr(t, t._testMethodName, None)
            if not hasattr(method, 'points') or not hasattr(method, 'category'):
                raise ValueError(f'{t.id()} 缺少 graded 元数据')
            if not isinstance(method.category, str) or not method.category or isinstance(method.points, bool) or not isinstance(method.points, (int, float)) or not math.isfinite(method.points) or method.points <= 0:
                raise ValueError(f'{t.id()} 的评分元数据无效')
            if any(entry['id'] == t.id() for entry in result): raise ValueError(f'重复测试 {t.id()}')
            result.append({'id': t.id(), 'points': method.points, 'category': method.category})
        print(json.dumps(result))
    else:
        test = next(t for t in tests if t.id() == action)
        result = unittest.TestResult()
        test.run(result)
        errors = result.errors + result.failures
        print(json.dumps({'ok': result.wasSuccessful() and not result.skipped, 'detail': '\n'.join(x[1] for x in errors) or (str(result.skipped) if result.skipped else '')}))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        traceback.print_exc()
        sys.exit(1)
