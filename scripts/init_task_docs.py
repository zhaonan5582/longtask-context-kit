#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键生成"长任务上下文包"五层骨架。

用法: python init_task_docs.py <docs_dir> "<一句话任务描述>" [--force]
"""
import io, os, sys, datetime, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, '..', 'templates')
FILES = ['00_LIVE.md', '01_TASK.md', '02_METHOD.md', '03_CASES.md', '04_RULES.md']


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    docs = sys.argv[1]
    task = sys.argv[2]
    force = '--force' in sys.argv
    os.makedirs(docs, exist_ok=True)
    today = datetime.date.today().isoformat()
    who = os.environ.get('USERNAME') or os.environ.get('USER') or 'agent'
    made, skipped = [], []
    for fn in FILES:
        dst = os.path.join(docs, fn)
        if os.path.exists(dst) and not force:
            skipped.append(fn); continue
        src = os.path.join(TPL, fn)
        if not os.path.isfile(src):
            print('[WARN] 缺模板:', src); continue
        s = io.open(src, encoding='utf-8').read()
        s = s.replace('{{TASK}}', task).replace('{{DATE}}', today).replace('{{WHO}}', who)
        io.open(dst, 'w', encoding='utf-8').write(s)
        made.append(fn)
    print('已生成:', ', '.join(made) or '(无)')
    if skipped:
        print('已存在(跳过):', ', '.join(skipped), '  —— 加 --force 覆盖')
    print()
    print('★ 接下来必须做两件事，否则机制不会自己转：')
    print('  1) 把"每轮开工先读 00_LIVE.md → 再读 01_TASK.md → 只读指到的那节"写进 agent prompt；')
    print('  2) 把"每轮收尾必须覆盖重写 00_LIVE.md"同样写进 prompt；')
    print('  3) 并在 agent 的长期记忆里写明"文档体系在哪、压缩后先读哪个"。')


if __name__ == '__main__':
    main()
