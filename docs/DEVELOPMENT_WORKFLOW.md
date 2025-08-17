# Development Workflow & Branching Strategy

## Overview
This document outlines the development workflow and branching strategy for the Art App project to maintain a clean, organized development environment.

## Branch Structure

### Main Branches
- **`main`** - Production-ready code, always stable
- **`dev`** - Integration branch for features, updated frequently

### Feature Branches
- **`feature/feature-name`** - Individual feature development
- **`bugfix/bug-description`** - Bug fixes
- **`hotfix/urgent-fix`** - Critical production fixes
- **`refactor/component-name`** - Code refactoring

## Development Workflow

### 1. Starting New Work
```bash
# Ensure you're on dev and it's up to date
git checkout dev
git pull origin dev

# Create a new feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/bug-description
```

### 2. Development Process
```bash
# Make your changes
# ... code, code, code ...

# Stage and commit your changes
git add .
git commit -m "feat: add new feature description"

# Push your feature branch
git push origin feature/your-feature-name
```

### 3. Completing Work
```bash
# Switch back to dev
git checkout dev
git pull origin dev

# Merge your feature branch
git merge feature/your-feature-name

# Push updated dev
git push origin dev

# Delete local feature branch (optional)
git branch -d feature/your-feature-name
```

### 4. Releasing to Production
```bash
# When ready to release
git checkout main
git pull origin main
git merge dev
git push origin main

# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Commit Message Convention

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add user authentication system
fix: resolve image loading issue on mobile
docs: update API documentation
refactor: restructure component hierarchy
```

## Branch Naming Conventions

- **Features**: `feature/descriptive-name`
- **Bug fixes**: `bugfix/issue-description`
- **Hotfixes**: `hotfix/critical-issue`
- **Refactoring**: `refactor/component-name`
- **Documentation**: `docs/topic-update`

## Best Practices

1. **Never commit directly to main** - Always work through feature branches
2. **Keep branches focused** - One feature/bug per branch
3. **Regular updates** - Pull from dev frequently to avoid conflicts
4. **Clean commits** - Make atomic, well-described commits
5. **Test before merging** - Ensure your feature works before merging to dev
6. **Delete merged branches** - Keep the repository clean

## Current Branch Status

- `main` - Production branch
- `dev` - Development integration branch
- `feature/exhibit-filters` - Exhibit filtering functionality
- `feature/frontend-enhancements` - Frontend improvements
- `backend-optimization` - Backend performance improvements

## Getting Started

1. Clone the repository
2. Checkout the `dev` branch
3. Create a feature branch for your work
4. Follow the development workflow above
5. Create a pull request when ready to merge

## Troubleshooting

### Merge Conflicts
```bash
# Resolve conflicts in your editor
git add .
git commit -m "resolve merge conflicts"
```

### Stashing Changes
```bash
# Save current work temporarily
git stash

# Apply stashed changes
git stash pop
```

### Resetting to Clean State
```bash
# Reset to match remote dev (WARNING: loses local changes)
git reset --hard origin/dev
```

## Code Review Process

1. Create a pull request from your feature branch to `dev`
2. Request review from team members
3. Address feedback and make necessary changes
4. Merge only after approval and tests pass
5. Delete the feature branch after successful merge

This workflow ensures a clean, organized development process while maintaining code quality and stability.
