# Quick Start Development Guide

## 🚀 Getting Started with Development

This guide will get you up and running with the new development workflow in under 5 minutes!

## Prerequisites
- Git installed
- Access to the Art App repository
- Basic familiarity with command line

## Quick Setup

### 1. Clone and Setup (First Time Only)
```bash
# Clone the repository
git clone https://github.com/darbyrush/Art-App.git
cd Art-App

# Checkout the dev branch
git checkout dev
git pull origin dev
```

### 2. Start Working on a Feature
```bash
# Use our helper script to create a feature branch
./scripts/dev_workflow.sh start-feature your-feature-name

# Or manually:
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 3. Develop Your Feature
```bash
# Make your changes...
# Edit files, add new code, etc.

# Stage and commit your changes
git add .
git commit -m "feat: add your feature description"

# Push your feature branch
git push origin feature/your-feature-name
```

### 4. Complete Your Feature
```bash
# Use our helper script to finish and merge
./scripts/dev_workflow.sh finish-feature your-feature-name

# Or manually:
git checkout dev
git pull origin dev
git merge feature/your-feature-name
git push origin dev
git branch -d feature/your-feature-name
```

## 🛠️ Helper Scripts

We've created a helper script to make development easier:

```bash
# Show current status
./scripts/dev_workflow.sh status

# Start a new feature
./scripts/dev_workflow.sh start-feature feature-name

# Finish a feature
./scripts/dev_workflow.sh finish-feature feature-name

# Start a bugfix
./scripts/dev_workflow.sh start-bugfix bug-description

# Sync with dev branch
./scripts/dev_workflow.sh sync-dev

# Show help
./scripts/dev_workflow.sh help
```

## 📋 Daily Workflow

### Morning Routine
```bash
# Check current status
./scripts/dev_workflow.sh status

# Sync with latest dev changes
./scripts/dev_workflow.sh sync-dev
```

### During Development
```bash
# Make changes
# Commit frequently with good messages
git add .
git commit -m "feat: add user profile editing"

# Push your work
git push origin feature/your-feature-name
```

### End of Day
```bash
# Commit any remaining work
git add .
git commit -m "feat: complete user profile form"

# Push to remote
git push origin feature/your-feature-name
```

## 🔒 Safety Features

- **Pre-commit hooks** prevent accidental commits to main
- **Conventional commit messages** are encouraged
- **Large file detection** warns about big files
- **Sensitive file protection** prevents secrets from being committed

## 🚨 Common Issues & Solutions

### "Direct commits to main not allowed"
```bash
# You're on main branch, switch to dev
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### "Merge conflicts detected"
```bash
# Resolve conflicts in your editor
# Then:
git add .
git commit -m "resolve merge conflicts"
```

### "Branch is behind dev"
```bash
# Sync your branch with dev
./scripts/dev_workflow.sh sync-dev
```

## 📚 Next Steps

1. **Read the full workflow**: [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)
2. **Practice with a small feature** to get comfortable
3. **Ask questions** if anything is unclear
4. **Follow the commit message conventions** for consistency

## 🎯 Best Practices

- **One feature per branch** - Keep branches focused
- **Commit frequently** - Small, atomic commits are better
- **Pull before pushing** - Avoid conflicts
- **Use descriptive branch names** - `feature/user-authentication` not `feature/thing`
- **Test before merging** - Ensure your feature works

## 🆘 Need Help?

- Check the full workflow document
- Use `./scripts/dev_workflow.sh help`
- Ask team members for guidance
- Review git documentation if needed

---

**Happy coding! 🎨✨**
