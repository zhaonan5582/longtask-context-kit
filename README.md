# longtask-context-kit

**A drop-in documentation scaffold that keeps long-running / unattended AI agents alive across context compaction.**

> English | [中文说明](#中文说明)

---

## The problem

Long-running agent tasks don't fail because the model is dumb.
They fail because **you can't tell whether it actually did the work.**

> "It said the run was complete. Why did it break the moment I tried it?"

Three ways this happens, over and over:

1. **Compaction erases the working state** — uncontrollably, out of order. The current sub-task and three-day-old small talk are treated as equally disposable.
2. **Acceptance is self-certified with stale data** — the agent verifies *a* path that happens to work, not the path the user actually walks.
3. **Skipped cases vanish from the statistics** — a case marked "skip" silently leaves the denominator, so "94/97 covered" holds on paper and collapses in production.

## What this kit actually is

**Not** "memory management for agents". It is **anti-self-deception, with verifiable traces**:

> **It doesn't make the agent smarter. It makes the agent's bullshit un-hideable.**

Every rule is a tripwire:

| Rule | What it catches |
|---|---|
| Snapshot is **overwritten**, must not go stale | Didn't update it? The old file is still there — **mtime gives you away** |
| **Skipped != passed** | Anything skipped must be declared `NOT-TESTED` — it cannot quietly stay in the denominator |
| Acceptance uses **fresh data** | No self-certifying with "the old dataset that already worked" |
| **Completion state + idle guard** | No "produce something to look busy" edits on already-correct work |
| **External night watch** | Verification does not rely on the agent's own report — a third party checks mtimes |

Saving tokens is a **side effect, not the pitch**. The pitch is:
**can you hand it a long task, walk away, and trust tomorrow's result?**

## The fix: five layers, read as little as possible

| Layer | File | Contains | How much to read |
|---|---|---|---|
| **L0.5 Snapshot** | `00_LIVE.md` | What I am doing *right now* | **First thing after compaction**, full (~30 lines) |
| **L0 Task book** | `01_TASK.md` | What to do / hard rules / coordinates / how to read | **Every run**, full (<=50 lines) |
| **L1 Index** | `02_METHOD.md` section 0 | One-line summary per entry | Glance, to locate |
| **L2 Entries** | `02_METHOD.md` | Symptom -> root cause -> how to detect -> fix | **Only the entry you were pointed to** |
| **L3 Cases** | `03_CASES.md` | Logs, long reasoning, raw originals | Only when traceability is needed |

The critical distinction people mix up:

- **L0 Task book answers "what should be done"** (slow-changing)
- **L0.5 Snapshot answers "how far did I get"** (fast-changing)

## Three rules that carry most of the value

### 1. The snapshot is overwritten, never appended — and never stale

`00_LIVE.md` is **not a log**. Overwrite it, keep it reflecting *this moment*, cap it at **~30 lines**.

> **A stale snapshot is worse than no snapshot** — it makes people act on a state that no longer exists.

### 2. Change the library with evidence — and let differing cases COEXIST

Never "hit a problem, then go rewrite the library". Before touching an existing entry:

1. **Search whether it already exists.**
2. **If it does — ask why the previous author wrote it that way.** Do not touch it before reading it fully.
3. **Judge the nature:**

| Verdict | Action |
|---|---|
| **Genuinely wrong** (falsified by evidence) | Change it, but **keep the trace**: old -> new, plus `evidence: <log / repro / diff>` |
| **Different situation** (the old statement holds in *its* conditions) | **Coexist.** Add an "applicable conditions / counter-examples" section. **Never overwrite.** |

> Overwriting wipes out someone else's boundary conditions — and the next person steps into the same hole.

### 3. Skipped != passed

Any case skipped because conditions were not available must be marked **`NOT-TESTED`**, never `PASS`.

> Skipped cases disappear from the statistics — that is exactly how "94/97 covered" stays true on paper and falls apart in production.

## Acceptance standard

**Written in -> retrievable -> visible in the next step.** All three segments need evidence.

- "The endpoint returned 200" / "one path works" — **neither counts as done**.
- Acceptance must use **fresh data** (never self-certify with the old dataset that already worked).
- When reporting coverage, **always report the `NOT-TESTED` count and list** alongside it.

## Quick start

```bash
python scripts/init_task_docs.py ./docs "Take system X from zero through to Y"
```

Generates the five-layer skeleton with placeholders filled.

**Then wire it into your agent** (otherwise the mechanism will not turn itself):

1. Put **"start each run by reading `00_LIVE.md` -> then `01_TASK.md` -> then only the section you were pointed to"** into your agent prompt / automation;
2. Put **"end each run by overwriting `00_LIVE.md`"** into the same prompt;
3. Record **where the docs live and what to read first after compaction** in the agent long-term memory — so it can find its way back **even after its context is wiped**.

## Repository layout

```
SKILL.md                     Skill description
README.md                    This file (EN + Chinese)
LICENSE                      MIT
scripts/init_task_docs.py    One-command skeleton generator
templates/00_LIVE.md         Snapshot (overwrite, <=30 lines)
templates/01_TASK.md         Task book (hard rules / coordinates / read map)
templates/02_METHOD.md       Method library (index + entry format)
templates/03_CASES.md        L3 case layer
templates/04_RULES.md        Library structure and update discipline
push_to_github.sh            Create repo + push in one go
```

## Field-tested, not whiteboarded

This kit was **extracted from a real unattended run**, and then verified in that same run (2026-09-14):

| Check | Evidence | Verdict |
|---|---|---|
| Reads the snapshot on start | Session UI log — **first action** = `view file: 00_LIVE.md` | ✅ |
| Overwrites the snapshot on finish | `00_LIVE.md` mtime advanced; content self-labelled `role: executor` | ✅ |
| Syncs the task book | The task book's "next steps" had completed items struck through and re-pointed | ✅ |
| Syncs the method library | A new method entry was appended to the library | ✅ |

The same run also **found the user's real blocker** — a page that silently navigated to an
archived "empty new-record" shell after save — which no amount of "the endpoint returns 200"
testing would ever have surfaced. That is the difference this kit is about.

## Pitfalls (learned the hard way, Windows + mainland China network)

1. **`winget install GitHub.cli` can "fake-succeed"** — the task reports completed, but `winget list` does not show it; nothing was actually installed. **Verify with `gh --version`, not with the task status.**
2. **GitHub releases are not reachable directly from mainland China** (curl `exit 56` / requests `ProxyError`). **A mirror prefix works**: `https://ghproxy.net/https://github.com/...`.
3. **`GH_CONFIG_DIR` must be given as a Windows path.** With a Git Bash path like `/d/xxx`, `gh` (a Windows binary) does not understand it: **auth reports `Authentication complete` but the token never gets saved**, and you are "logged out" again. Use `D:/xxx`. (On some machines `~/.config/gh` cannot even be created — then `GH_CONFIG_DIR` is mandatory.)
4. **Behind a proxy that only tunnels HTTP for some clients, `git push` fails** with `CONNECT tunnel failed, response 502` while `gh api` works fine. **Use `gh api` to upload files instead of `git push`:**

```bash
C=$(base64 -w0 README.md | tr -d '\n')
gh api -X PUT "repos/<owner>/<repo>/contents/README.md" \
  -f message="update README" -f content="$C" \
  -f sha="$(gh api repos/<owner>/<repo>/contents/README.md -q .sha)" -f branch=main
```

> Pitfalls 1 and 3 are the same disease as this kit own thesis: **"looks like it succeeded" != "it actually succeeded".**

## Relation to Obsidian

Same family of ideas — atomic notes, links, layers, on-demand expansion — but with a **different reader**: Obsidian serves humans who *click links*; an **agent only locates by index and reads that section**. So "links" are realized as **an index + anchor paths**, which costs far less context than a graph would.

## License

MIT

---
---

# 中文说明

**一套"即插即用"的文档脚手架，让长程 / 无人值守的 AI agent 在上下文被压缩后依然活着。**

## 它解决什么问题

长程 agent 任务翻车，**不是因为模型笨**，而是因为 —— **你没法判断它到底干没干。**

> **"不是跑通了吗？我上来怎么就卡住了。"**

这事的成因反复就三条：

1. **上下文压缩把工作状态抹掉** —— 不可控、无序，把"当前小任务"和"三天前的寒暄"同等对待；
2. **验收用老数据自证** —— 它验的是*某条*恰好能走的路，不是用户真正走的那条；
3. **跳过项在统计里消失** —— 标了"跳过"的用例悄无声息地离开分母，"覆盖率 94/97"于是纸面成立、真机崩塌。

## 这套东西**真正**是什么

**不是**"给 agent 做记忆管理"，而是 —— **防自欺，而且留下可查证的痕迹**：

> **它不让 agent 更聪明，它让 agent 的"糊弄"藏不住。**

每一条纪律都是一道**抓现行的机关**：

| 纪律 | 抓什么 |
|---|---|
| 快照**覆盖式**、不许过期 | 没更新？旧文件还在 —— **mtime 一眼看穿** |
| **跳过 ≠ 通过** | 想跳过的必须显式认账 `NOT-TESTED`，**不能悄悄留在分母里** |
| 验收用**全新数据** | 不许拿"那条已经跑通过的老数据"自证 |
| **完成态声明 + 空转防护** | 不许为了"显得有产出"去改已经正确的东西 |
| **外部守夜人** | **不靠 agent 自述** —— 第三方查 mtime 客观验证 |

**省 token 是顺带的结果，不是卖点。** 卖点是：
**你敢不敢把一个长任务丢给它、人走开，然后相信明天的结果？**

## 解法：五层结构，用多少读多少

| 层 | 文件 | 装什么 | 读多少 |
|---|---|---|---|
| **L0.5 快照** | `00_LIVE.md` | 此刻在做什么 | **压缩后第一个读**，全文（约 30 行） |
| **L0 任务书** | `01_TASK.md` | 要干什么 / 铁律 / 坐标 / 读法 | **每轮必读**，全文（<=50 行） |
| **L1 索引** | `02_METHOD.md` 第 0 节 | 每条一句话摘要 | 扫一眼定位 |
| **L2 条目** | `02_METHOD.md` | 症状 -> 根因 -> 判据 -> 修法 | **只读被指到的那条** |
| **L3 案例** | `03_CASES.md` | 日志 / 长推演 / 原文 | 只在需要溯源时读 |

最容易搞混的一对：

- **L0 任务书 = "要干什么"**（变化慢）
- **L0.5 快照 = "干到哪了"**（变化快，每个小闭环重写一次）

## 三条最值钱的纪律

### 1. 快照覆盖式、不许过期

`00_LIVE.md` **不是日志**。覆盖它，让它永远只反映**此刻**，控制在 **30 行**以内。

> **过期的快照比没有快照更坏** —— 它会让人照着已经不存在的状态干活。

### 2. 改库有据，不同情况**并存**

绝不"遇到个问题回来哐哐就改库"。动已有条目之前：

1. **先查有没有**；
2. 有则**先问"前人为什么这么写"** —— 不读完旧条目不许动笔；
3. **判性质**：

| 判定 | 处置 |
|---|---|
| **真不对**（被实证推翻） | 改，但**留痕**：旧 -> 新 + 依据（日志/复现/比对） |
| **不同情况**（旧说法在其条件下成立） | **【并存】** —— 加"适用条件 / 反例"分节，**绝不覆盖** |

> 直接覆盖等于把别人的边界条件一起抹掉，下一个人还得再踩一遍。

### 3. 跳过 != 通过

因条件不具备而跳过的用例，必须标 **`NOT-TESTED`**，绝不能标 `PASS`。

> 跳过项会从统计口径里消失 —— "覆盖率 94/97"在纸面成立、在生产崩塌，就是这么来的。

## 验收口径

**写进去 -> 能查到 -> 下一环节看得见**，三段都要有证据。

- "接口返回 200" / "某条路径能走" —— **都不算做完**；
- 验收必须用**全新数据**（不许拿"那条已经跑通过的老数据"自证）；
- 报覆盖率时，**必须同时报 `NOT-TESTED` 的数量和清单**。

## 快速开始

```bash
python scripts/init_task_docs.py ./docs "把 X 系统从零走通到 Y"
```

生成五层骨架（占位说明已填好）。

**然后把机制接进你的 agent**（否则它不会自己转起来）：

1. 把 **"每轮开工先读 `00_LIVE.md` -> 再读 `01_TASK.md` -> 只读被指到的那节"** 写进 agent prompt / automation；
2. 把 **"每轮收尾必须覆盖重写 `00_LIVE.md`"** 写进同一个 prompt；
3. 把 **"文档在哪、压缩后先读哪个"** 写进 agent 的长期记忆 —— 这样**即使上下文被抹掉，它也能自己找回来**。

## 实战验证过，不是纸上设计

这套东西是**从一次真实的无人值守运行里抽出来的**，并且**在同一次运行里得到验证**（2026-09-14）：

| 检查项 | 证据 | 结论 |
|---|---|---|
| 开工读快照 | 会话 UI 日志 —— **第一个动作**就是 `查看文件: 00_LIVE.md` | ✅ |
| 收尾覆盖写快照 | `00_LIVE.md` 的 mtime 前移；内容里自称"执行岗" | ✅ |
| 同步任务书 | 任务书"下一步"里已完成项被划掉、重新指向 | ✅ |
| 同步方法论 | 方法论库追加了新条目 | ✅ |

同一次运行还**挖出了用户真正卡住的根因** —— 保存后页面**悄悄跳转**到一张被归档成"新增态空壳"的页；
这种洞，"接口返回 200"式的验收**永远测不出来**。这正是本 kit 存在的意义。

## 踩过的坑

1. **`winget install GitHub.cli` 会"假成功"** —— 任务显示 completed，但 `winget list` 里找不到，实际没装上。**判据：用 `gh --version` 实测，不要看任务状态。**
2. **国内直连 GitHub releases 不通**（curl `exit 56` / requests `ProxyError`）。**加镜像前缀可用**：`https://ghproxy.net/https://github.com/...`。
3. **`GH_CONFIG_DIR` 必须给 Windows 路径形式**。给 Git Bash 的 `/d/xxx` 时，`gh`（Windows 程序）不认识：**授权显示 `Authentication complete`，但 token 存不下来**，回头又变"未登录"。用 `D:/xxx`。某些机器上 `~/.config/gh` 创建不了，此时必须显式指定。
4. **代理只放行部分客户端的 HTTP 时，`git push` 会以 `CONNECT tunnel failed, response 502` 失败**，而 `gh api` 正常。**改用 `gh api` 传文件，别用 `git push`**（命令见英文节）。

> 第 1、3 条和本 kit 的主张是同一种病：**"看起来成功了" != "真成功了"**。

## 和 Obsidian 的关系

同类思路 —— 原子化笔记、互链、分层、按需展开 —— 但**读者不同**：Obsidian 面向**人**（靠点链接跳转），**agent 只会"按索引定位再读那一段"**。所以把"链接"落地成 **索引 + 锚点路径**，比做图谱省得多。

## 许可

MIT
