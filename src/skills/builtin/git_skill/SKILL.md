# Git 操作技能

## 描述
提供 Git 版本控制操作的指导和最佳实践，帮助用户高效地进行代码版本管理。

## 使用场景
当用户需要进行以下 Git 操作时：
- 提交代码更改
- 拉取或推送代码
- 创建和管理分支
- 处理合并冲突
- 查看历史记录

## 指导
作为 AI Agent，在协助用户进行 Git 操作时，请遵循以下指导：

### 基本原则
- 在执行破坏性操作前，先检查当前状态（如是否有没有提交的更改）
- 始终先确认操作的安全性，特别是涉及到历史重写的命令
- 提供清晰的操作说明和预期结果
- 使用合适的命令参数以提高操作效率

### Commit 提交流程
1. 查看当前状态：`git status`
2. 查看具体更改：`git diff`（未暂存）或 `git diff --staged`（已暂存）
3. 添加文件到暂存区：`git add <files>` 或 `git add .`（所有更改）
4. 提交更改：`git commit -m "清晰的提交信息"`
   - 提交信息应该简洁明了，描述做了什么和为什么
   - 使用中文或英文根据项目风格
   - 避免使用 "fix bug" 或 "update" 这种模糊的信息

### Pull/Push 操作
1. 拉取远程更改：
   - `git pull`（自动合并）
   - `git fetch` + `git merge`（更安全的两步操作）
2. 推送本地更改：
   - `git push`（推送当前分支）
   - `git push origin <branch-name>`（推送到指定分支）
3. 推送前确认：
   - 确保本地分支是最新的
   - 检查是否有冲突需要解决
   - 确认提交信息是否合适

### 分支管理
1. 创建新分支：`git checkout -b <branch-name>`
2. 切换分支：`git checkout <branch-name>` 或 `git switch <branch-name>`
3. `git branch`：查看所有分支
4. 删除分支：
   - `git branch -d <branch-name>`（安全删除）
   - `git branch -D <branch-name>`（强制删除）
5. 合并分支：
   - 先切换到目标分支：`git checkout <target-branch>`
   - 执行合并：`git merge <source-branch>`

### 冲突解决
1. 检测冲突：Git 会标记冲突文件
2. 查看冲突：`git status` 会显示冲突文件
3. 手动解决冲突：编辑冲突文件，选择合适的内容
4. 标记为已解决：`git add <resolved-files>`
5. 完成合并：`git commit`
6. 放弃合并：`git merge --abort`

### 常用命令参考
- `git log`：查看提交历史
- `git log --oneline --graph --all`：图形化查看分支历史
- `git reflog`：查看所有操作记录（包括被删除的提交）
- `git stash`：暂存当前工作
- `git stash pop`：恢复暂存的工作
- `git reset --hard HEAD`：放弃所有本地更改（危险操作）
- `git clean -fd`：删除未跟踪的文件（危险操作）

### 注意事项
- 不要在公共分支上执行 `git push --force`，除非非常清楚后果
- 重要操作前建议先备份或创建新分支
- 使用 `.gitignore` 文件忽略不需要版本控制的文件
- 定期拉取远程更新以减少冲突概率
- 学习使用 `git help <command>` 查看详细帮助

### 错误处理
- 如果遇到 "detached HEAD" 状态，说明你处于一个未命名的提交上
- 如果遇到 "merge conflict"，需要手动解决冲突
- 如果遇到 "nothing to commit"，说明工作目录是干净的
- 如果遇到 "rejected" 错误，通常需要先 pull 或使用强制推送
