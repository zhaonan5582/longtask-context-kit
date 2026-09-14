#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键生成"长任务上下文包"五层骨架 + 可粘贴的 agent prompt 片段。

用法: python init_task_docs.py <docs_dir> "<一句话任务描述>" [--force]
"""
import io, os, sys, datetime

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
            print('[WARN] missing template:', src); continue
        s = io.open(src, encoding='utf-8').read()
        s = s.replace('{{TASK}}', task).replace('{{DATE}}', today).replace('{{WHO}}', who)
        io.open(dst, 'w', encoding='utf-8').write(s)
        made.append(fn)

    # ★ 直接产出一份"可粘贴的 agent prompt 片段"，而不是只提醒用户去手写
    D = docs.replace('\\', '/')
    prompt_fp = os.path.join(docs, 'AGENT-PROMPT.md')
    if not os.path.exists(prompt_fp) or force:
        body = (
            '# 可直接粘贴进 agent prompt 的片段（由 init_task_docs.py 生成）\n'
            '\n'
            '> 把下面的 `{D}` 全部替换成你的 docs 路径。本次生成时为：`' + D + '`\n'
            '\n'
            '```\n'
            '【每轮开工顺序（必读；不读就动手 = 违规）】\n'
            '1. 读 {D}/00_LIVE.md —— 压缩后**第一个**读；覆盖式"此刻状态"，约 30 行\n'
            '2. 读 {D}/01_TASK.md —— 任务书（下一步 / 铁律 / 坐标 / 读法 / 文档地图）\n'
            '3. 只读上面两份**指到的那一节**；不要通读任何大文档\n'
            '\n'
            '【每轮收尾（必须做，否则下一个你会踩坑）】\n'
            '1. **覆盖重写** {D}/00_LIVE.md（<=30 行，覆盖不是追加）：此刻在做什么 / 本阶段已改文件 /\n'
            '   已确认结论 / 卡在哪待验证 / 下一步第一件事\n'
            '2. 有新技术结论 -> 在 {D}/02_METHOD.md 加条目（编号续写）+ 同步 §0 索引；\n'
            '   长案例/日志 -> 写 {D}/03_CASES.md，L2 只留结论 + 锚点\n'
            '3. 改库前：先查有没有 -> 问前人为什么这么写 -> 判"真不对"（改且留痕）还是"不同情况"\n'
            '   （【并存】+ 写清适用条件，绝不覆盖）。禁止凭一次印象改库\n'
            '4. 当日 memory 日志追加一条\n'
            '\n'
            '【上下文预算（硬限制）】00_LIVE <=30 行 / 01_TASK <=50 行 / 索引每条 <=1 行 /\n'
            '单条目 <=20 行。超限就**降级到下一层**，不要删。用 wc -l 自检。\n'
            '\n'
            '【工作方式】上下文有限、会中途结束（设计如此，不是失败）；一轮只做一个小闭环；\n'
            '改了代码必须当轮内编译 + 实测，绝不允许"改了没测"就结束；接力是正常工作方式。\n'
            '\n'
            '【完成态】达到"连续三遍无修改"后：在 01_TASK.md 最顶部加一行\n'
            '`> # 【已完成】YYYY-MM-DD HH:MM · 连续三遍无修改`；\n'
            '此后每轮开工读到它就**只确认没有新问题，然后立即结束**：\n'
            '不重复劳动、不为"显得有产出"而改已经正确的东西、不把"完成"改回"未完成"。\n'
            '```\n'
        )
        io.open(prompt_fp, 'w', encoding='utf-8').write(body)
        made.append('AGENT-PROMPT.md')

    print('generated:', ', '.join(made) if made else '(none)')
    if skipped:
        print('already exists (skipped):', ', '.join(skipped), ' -- use --force to overwrite')
    print()
    print('** NEXT STEP (otherwise the mechanism will not run) **')
    print('  1) paste the generated prompt fragment into your agent prompt / automation:')
    print('     ' + prompt_fp)
    print('     (read 00_LIVE -> 01_TASK -> only the pointed section; overwrite 00_LIVE at the end)')
    print('  2) record "where the docs live / what to read first after compaction"')
    print('     in the agent long-term memory, so it can find its way back.')


if __name__ == '__main__':
    main()
