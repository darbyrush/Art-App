#!/bin/bash

# Development Workflow Helper Script
# This script helps manage the development workflow for the Art App

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository. Please run this script from your project root."
        exit 1
    fi
}

# Function to check current branch
check_current_branch() {
    local current_branch=$(git branch --show-current)
    print_status "Current branch: $current_branch"
    echo $current_branch
}

# Function to start new feature
start_feature() {
    local feature_name=$1
    
    if [ -z "$feature_name" ]; then
        print_error "Please provide a feature name"
        echo "Usage: $0 start-feature <feature-name>"
        exit 1
    fi
    
    print_header "Starting new feature: $feature_name"
    
    # Ensure we're on dev and it's up to date
    print_status "Switching to dev branch..."
    git checkout dev
    
    print_status "Pulling latest changes from dev..."
    git pull origin dev
    
    # Create and checkout new feature branch
    local branch_name="feature/$feature_name"
    print_status "Creating feature branch: $branch_name"
    git checkout -b "$branch_name"
    
    print_status "Feature branch created and checked out!"
    print_status "You can now start developing your feature."
    print_status "When ready to commit, use: git add . && git commit -m 'feat: $feature_name'"
}

# Function to finish feature
finish_feature() {
    local feature_name=$1
    
    if [ -z "$feature_name" ]; then
        print_error "Please provide a feature name"
        echo "Usage: $0 finish-feature <feature-name>"
        exit 1
    fi
    
    local branch_name="feature/$feature_name"
    
    print_header "Finishing feature: $feature_name"
    
    # Check if we're on the feature branch
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "$branch_name" ]; then
        print_warning "You're not on the feature branch $branch_name"
        print_status "Switching to $branch_name..."
        git checkout "$branch_name"
    fi
    
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "You have uncommitted changes. Please commit or stash them first."
        exit 1
    fi
    
    # Switch to dev and merge
    print_status "Switching to dev branch..."
    git checkout dev
    
    print_status "Pulling latest changes from dev..."
    git pull origin dev
    
    print_status "Merging feature branch..."
    git merge "$branch_name"
    
    print_status "Pushing updated dev branch..."
    git push origin dev
    
    # Delete local feature branch
    print_status "Deleting local feature branch..."
    git branch -d "$branch_name"
    
    print_status "Feature completed and merged to dev!"
}

# Function to start bugfix
start_bugfix() {
    local bug_description=$1
    
    if [ -z "$bug_description" ]; then
        print_error "Please provide a bug description"
        echo "Usage: $0 start-bugfix <bug-description>"
        exit 1
    fi
    
    print_header "Starting bugfix: $bug_description"
    
    # Ensure we're on dev and it's up to date
    print_status "Switching to dev branch..."
    git checkout dev
    
    print_status "Pulling latest changes from dev..."
    git pull origin dev
    
    # Create and checkout new bugfix branch
    local branch_name="bugfix/$bug_description"
    print_status "Creating bugfix branch: $branch_name"
    git checkout -b "$branch_name"
    
    print_status "Bugfix branch created and checked out!"
}

# Function to show status
show_status() {
    print_header "Git Status"
    
    print_status "Current branch: $(git branch --show-current)"
    print_status "Remote tracking: $(git branch -vv | grep '*' | awk '{print $4}')"
    
    echo
    print_header "Working Directory Status"
    git status --short
    
    echo
    print_header "Recent Commits"
    git log --oneline -5
}

# Function to sync with dev
sync_dev() {
    print_header "Syncing with dev branch"
    
    local current_branch=$(git branch --show-current)
    
    if [ "$current_branch" = "dev" ]; then
        print_status "Already on dev branch, pulling latest changes..."
        git pull origin dev
    else
        print_status "Switching to dev branch..."
        git checkout dev
        print_status "Pulling latest changes..."
        git pull origin dev
        print_status "Switching back to $current_branch..."
        git checkout "$current_branch"
        print_status "Merging latest dev changes..."
        git merge dev
    fi
    
    print_status "Sync complete!"
}

# Function to show help
show_help() {
    echo "Development Workflow Helper Script"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  start-feature <name>    Start a new feature branch"
    echo "  finish-feature <name>   Finish and merge a feature branch"
    echo "  start-bugfix <desc>     Start a new bugfix branch"
    echo "  status                  Show current git status"
    echo "  sync-dev                Sync current branch with dev"
    echo "  help                    Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start-feature user-authentication"
    echo "  $0 finish-feature user-authentication"
    echo "  $0 start-bugfix login-error"
    echo "  $0 status"
    echo "  $0 sync-dev"
}

# Main script logic
main() {
    check_git_repo
    
    case "$1" in
        "start-feature")
            start_feature "$2"
            ;;
        "finish-feature")
            finish_feature "$2"
            ;;
        "start-bugfix")
            start_bugfix "$2"
            ;;
        "status")
            show_status
            ;;
        "sync-dev")
            sync_dev
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
