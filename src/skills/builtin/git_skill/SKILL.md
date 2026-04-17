---
name: git_operations
description: Git version control operations and best practices
---

# Git Operations

Use this skill when the user needs to:
- Commit code changes
- Pull or push code
- Create or manage branches
- Resolve merge conflicts
- View git history

## Instructions

### Basic Principles
- Check current state before destructive operations
- Always confirm operation safety, especially for history-rewriting commands
- Provide clear operation descriptions and expected results
- Use appropriate command parameters for efficiency

### Commit Workflow
1. Check status: `git status`
2. View changes: `git diff` (unstaged) or `git diff --staged` (staged)
3. Stage files: `git add <files>` or `git add .` (all changes)
4. Commit: `git commit -m "Clear commit message"`
   - Commit messages should be concise and describe what and why
   - Use Chinese or English based on project style
   - Avoid vague messages like "fix bug" or "update"

### Pull/Push Operations
1. Pull remote changes:
   - `git pull` (auto merge)
   - `git fetch` + `git merge` (safer two-step operation)
2. Push local changes:
   - `git push` (current branch)
   - `git push origin <branch-name>` (specific branch)
3. Before pushing:
   - Ensure local branch is up to date
   - Check for conflicts
   - Verify commit messages

### Branch Management
1. Create new branch: `git checkout -b <branch-name>`
2. Switch branch: `git checkout <branch-name>` or `git switch <branch-name>`
3. `git branch`: View all branches
4. Delete branch:
   - `git branch -d <branch-name>` (safe delete)
   - `git branch -D <branch-name>` (force delete)
5. Merge branches:
   - Switch to target: `git checkout <target-branch>`
   - Execute merge: `git merge <source-branch>`

### Conflict Resolution
1. Detect conflicts: Git marks conflicting files
2. View conflicts: `git status` shows conflicting files
3. Resolve manually: Edit conflict files, choose appropriate content
4. Mark resolved: `git add <resolved-files>`
5. Complete merge: `git commit`
6. Abort merge: `git merge --abort`

### Common Commands Reference
- `git log`: View commit history
- `git log --oneline --graph --all`: Graphical branch history
- `git reflog`: View all operation records (including deleted commits)
- `git stash`: Stash current work
- `git stash pop`: Restore stashed work
- `git reset --hard HEAD`: Discard all local changes (DANGEROUS)
- `git clean -fd`: Delete untracked files (DANGEROUS)

### Important Notes
- Never use `git push --force` on public branches unless you fully understand the consequences
- Create backup or new branch before important operations
- Use `.gitignore` to exclude files from version control
- Regularly pull remote updates to reduce conflict probability
- Use `git help <command>` for detailed help

### Error Handling
- "detached HEAD": You're on an unnamed commit
- "merge conflict": Manual resolution required
- "nothing to commit": Working directory is clean
- "rejected": Need to pull or use force push
