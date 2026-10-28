"""实现加载和测试评分元数据。"""
from __future__ import annotations
import math
import importlib.util
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

def load_impl(labid: str):
    if not labid.isidentifier():
        raise ValueError(f"无效实验名称: {labid!r}")
    impl_root = os.environ.get('NETLAB_IMPL_ROOT')
    path = Path(impl_root) / f'{labid}.py' if impl_root else ROOT / 'labs' / labid / 'student.py'
    path = path.resolve()
    name = f'_netlab_impl_{labid}'
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'无法加载实现: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        # 直接编译当前源码，避免快速修改时复用过期字节码。
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module

def graded(*, category: str, points: float):
    if not isinstance(category, str) or not category or isinstance(points, bool) or not isinstance(points, (int, float)) or not math.isfinite(points) or points <= 0:
        raise ValueError('category 必须非空且 points 必须为正数')
    def decorate(method):
        method.category = category
        method.points = points
        return method
    return decorate
