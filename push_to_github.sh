#!/usr/bin/env bash
# 一键：登录 GitHub → 创建仓库 → 推送 longtask-context-kit
#
# 用法（二选一）：
#   A) 带 token：  bash push_to_github.sh <你的_GITHUB_TOKEN> [仓库名]
#   B) 已登录过：  bash push_to_github.sh            # 直接用已有的 gh 登录态
#
# 说明：
#   · token 只需一次；脚本不会把它写进任何文件（只喂给 `gh auth login --with-token`）
#   · 仓库默认 public；要私有就改下面的 VISIBILITY
set -euo pipefail

SKILL_DIR="C:/Users/Admin/.workbuddy/skills/longtask-context-kit"
REPO_NAME="${2:-longtask-context-kit}"
VISIBILITY="public"          # 改成 private 即私有仓库
DESC="抗上下文压缩的长程 agent 任务文档体系：五层分层 + 覆盖式快照 + 任务书 + 改库纪律"

TOKEN="${1:-}"

# gh 的绝对路径（不依赖 PATH；本机已由 winget/免安装包放到 ~/.local/bin）
GH="$HOME/.local/bin/gh.exe"
[ -x "$GH" ] || GH="/c/Program Files/GitHub CLI/gh.exe"
if [ ! -x "$GH" ]; then
  if command -v gh >/dev/null 2>&1; then GH="gh"; else
    echo "[X] 没找到 gh（已查 ~/.local/bin 与 Program Files）。"; exit 1
  fi
fi
echo "     使用 gh: $GH"

# 1) 认证
if [ -n "$TOKEN" ]; then
  echo "[1/4] 用 token 登录 gh ..."
  printf '%s' "$TOKEN" | "$GH" auth login --with-token
else
  echo "[1/4] 未提供 token —— 检查已有登录态 ..."
  if ! "$GH" auth status >/dev/null 2>&1; then
    echo "[X] 未登录。请先跑一次：  gh auth login       （浏览器里点几下即可）"
    echo "    或改用：  bash push_to_github.sh <你的_TOKEN>"
    exit 1
  fi
fi
"$GH" auth status 2>&1 | sed 's/^/     /'

# 2) 确认本地仓库与分支
cd "$SKILL_DIR"
git rev-parse --git-dir >/dev/null 2>&1 || { echo "[X] $SKILL_DIR 不是 git 仓库"; exit 1; }
git branch -M main 2>/dev/null || true
echo "[2/4] 本地仓库就绪，分支：$(git rev-parse --abbrev-ref HEAD)，提交数：$(git rev-list --count HEAD)"

# 3) 创建远程仓库并推送（--source 会自动配好 remote，无需手加）
echo "[3/4] 创建远程仓库 $REPO_NAME（$VISIBILITY）并推送 ..."
"$GH" repo create "$REPO_NAME" "--$VISIBILITY" --source=. --remote=origin --push \
   --description "$DESC" 2>&1 | sed 's/^/     /' || {
     echo "[!] 创建失败（可能是同名仓库已存在）—— 改为直接推送"
     git remote get-url origin >/dev/null 2>&1 || \
       git remote add origin "https://github.com/$("$GH" api user -q .login)/$REPO_NAME.git"
     git push -u origin main
   }

# 4) 收尾
echo "[4/4] 完成。仓库地址："
"$GH" repo view "$REPO_NAME" --json url -q .url 2>/dev/null || echo "     （用 gh repo list 查看）"
