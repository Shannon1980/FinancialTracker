#!/bin/bash

# 🚀 SEAS Financial Tracker - Auto-Sync to GitHub Script
# This script automates the process of syncing local changes to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="FinancialTracker"
GITHUB_USER="Shannon1980"
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Check if we're in the right directory
check_directory() {
    if [[ ! -d ".git" ]]; then
        error "Not in a Git repository. Please run this script from the project root."
    fi
    
    if [[ ! -f "app_refactored.py" ]]; then
        error "Not in SEAS Financial Tracker project. Please run from the correct directory."
    fi
}

# Check Git status
check_git_status() {
    log "Checking Git status..."
    
    # Check if there are uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        info "Found uncommitted changes:"
        git status --short
        
        read -p "Do you want to commit these changes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            commit_changes
        else
            warning "Changes not committed. Please commit manually before continuing."
            exit 1
        fi
    else
        success "No uncommitted changes found."
    fi
}

# Commit changes with smart commit message
commit_changes() {
    log "Committing changes..."
    
    # Get list of changed files
    CHANGED_FILES=$(git status --porcelain | awk '{print $2}' | head -5)
    
    # Generate commit message based on file types
    if echo "$CHANGED_FILES" | grep -q "\.py$"; then
        COMMIT_MSG="🐍 Update Python code"
    elif echo "$CHANGED_FILES" | grep -q "\.md$"; then
        COMMIT_MSG="📚 Update documentation"
    elif echo "$CHANGED_FILES" | grep -q "\.yml$\|\.yaml$"; then
        COMMIT_MSG="⚙️ Update configuration"
    elif echo "$CHANGED_FILES" | grep -q "\.sh$"; then
        COMMIT_MSG="🔧 Update scripts"
    else
        COMMIT_MSG="✨ Update project files"
    fi
    
    # Add all changes
    git add .
    
    # Commit with generated message
    git commit -m "$COMMIT_MSG"
    
    success "Changes committed: $COMMIT_MSG"
}

# Sync with GitHub
sync_to_github() {
    log "Syncing with GitHub..."
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    info "Current branch: $CURRENT_BRANCH"
    
    # Check if we need to push
    if [[ -n $(git log @{u}..HEAD) ]]; then
        log "Pushing changes to GitHub..."
        git push origin "$CURRENT_BRANCH"
        success "Changes pushed to GitHub successfully!"
        
        # Show CI/CD status
        show_cicd_status
    else
        success "No new commits to push."
    fi
}

# Show CI/CD pipeline status
show_cicd_status() {
    log "Checking CI/CD pipeline status..."
    
    # Check if GitHub CLI is available
    if command -v gh &> /dev/null; then
        info "GitHub CLI detected. Checking workflow runs..."
        
        # Get latest workflow run
        LATEST_RUN=$(gh run list --workflow="SEAS Financial Tracker CI/CD Pipeline" --limit=1 --json status,conclusion,url)
        
        if [[ -n "$LATEST_RUN" ]]; then
            STATUS=$(echo "$LATEST_RUN" | jq -r '.[0].status')
            CONCLUSION=$(echo "$LATEST_RUN" | jq -r '.[0].conclusion')
            URL=$(echo "$LATEST_RUN" | jq -r '.[0].url')
            
            case $STATUS in
                "completed")
                    if [[ "$CONCLUSION" == "success" ]]; then
                        success "✅ CI/CD pipeline completed successfully!"
                    else
                        warning "❌ CI/CD pipeline failed. Check: $URL"
                    fi
                    ;;
                "in_progress")
                    info "🔄 CI/CD pipeline is running... Check: $URL"
                    ;;
                "queued")
                    info "⏳ CI/CD pipeline is queued... Check: $URL"
                    ;;
                *)
                    info "ℹ️ CI/CD pipeline status: $STATUS"
                    ;;
            esac
        else
            info "No recent workflow runs found."
        fi
    else
        info "GitHub CLI not found. Install with: brew install gh"
        info "Check CI/CD status at: https://github.com/$GITHUB_USER/$REPO_NAME/actions"
    fi
}

# Create feature branch
create_feature_branch() {
    log "Creating feature branch..."
    
    read -p "Enter feature name (e.g., 'add-new-chart'): " FEATURE_NAME
    
    if [[ -z "$FEATURE_NAME" ]]; then
        error "Feature name cannot be empty."
    fi
    
    # Sanitize feature name
    FEATURE_NAME=$(echo "$FEATURE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    
    # Switch to develop branch first
    log "Switching to develop branch..."
    git checkout develop
    git pull origin develop
    
    # Create and switch to feature branch
    FEATURE_BRANCH="feature/$FEATURE_NAME"
    git checkout -b "$FEATURE_BRANCH"
    
    success "Created feature branch: $FEATURE_BRANCH"
    info "You can now make changes and commit them."
}

# Merge feature to develop
merge_to_develop() {
    log "Merging feature to develop..."
    
    CURRENT_BRANCH=$(git branch --show-current)
    
    if [[ ! "$CURRENT_BRANCH" =~ ^feature/ ]]; then
        error "Not on a feature branch. Current branch: $CURRENT_BRANCH"
    fi
    
    # Switch to develop
    git checkout develop
    git pull origin develop
    
    # Merge feature branch
    git merge "$CURRENT_BRANCH"
    
    # Push to develop (triggers staging deployment)
    git push origin develop
    
    success "Feature merged to develop and pushed to GitHub!"
    info "Staging deployment will start automatically."
    
    # Clean up feature branch
    read -p "Delete feature branch '$CURRENT_BRANCH'? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git branch -d "$CURRENT_BRANCH"
        git push origin --delete "$CURRENT_BRANCH"
        success "Feature branch deleted."
    fi
}

# Create release
create_release() {
    log "Creating release..."
    
    # Get current version from git tags
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    info "Latest tag: $LATEST_TAG"
    
    # Parse version number
    VERSION_NUM=$(echo "$LATEST_TAG" | sed 's/v//')
    MAJOR=$(echo "$VERSION_NUM" | cut -d. -f1)
    MINOR=$(echo "$VERSION_NUM" | cut -d. -f2)
    PATCH=$(echo "$VERSION_NUM" | cut -d. -f3)
    
    # Suggest next version
    read -p "Version type (major/minor/patch) [patch]: " VERSION_TYPE
    VERSION_TYPE=${VERSION_TYPE:-patch}
    
    case $VERSION_TYPE in
        major)
            NEW_MAJOR=$((MAJOR + 1))
            NEW_VERSION="v$NEW_MAJOR.0.0"
            ;;
        minor)
            NEW_MINOR=$((MINOR + 1))
            NEW_VERSION="v$MAJOR.$NEW_MINOR.0"
            ;;
        patch)
            NEW_PATCH=$((PATCH + 1))
            NEW_VERSION="v$MAJOR.$MINOR.$NEW_PATCH"
            ;;
        *)
            error "Invalid version type. Use major, minor, or patch."
            ;;
    esac
    
    info "New version: $NEW_VERSION"
    
    # Create and push tag
    git tag "$NEW_VERSION"
    git push origin "$NEW_VERSION"
    
    success "Release tag $NEW_VERSION created and pushed!"
    info "Production deployment will start automatically."
    info "Create release notes at: https://github.com/$GITHUB_USER/$REPO_NAME/releases"
}

# Show repository status
show_status() {
    log "Repository Status:"
    echo "─────────────────────────────────────────────"
    
    # Current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "📍 Current branch: $CURRENT_BRANCH"
    
    # Remote status
    REMOTE_STATUS=$(git status --porcelain=2 --branch | grep '^# branch.upstream' | cut -d' ' -f3-)
    if [[ -n "$REMOTE_STATUS" ]]; then
        echo "🔄 Remote status: $REMOTE_STATUS"
    else
        echo "🔄 Remote status: Up to date"
    fi
    
    # Uncommitted changes
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [[ $UNCOMMITTED -gt 0 ]]; then
        echo "📝 Uncommitted changes: $UNCOMMITTED files"
    else
        echo "📝 Uncommitted changes: None"
    fi
    
    # Recent commits
    echo "📚 Recent commits:"
    git log --oneline -5
    
    echo "─────────────────────────────────────────────"
}

# Main menu
show_menu() {
    echo
    echo "🚀 SEAS Financial Tracker - GitHub Sync Menu"
    echo "═══════════════════════════════════════════════"
    echo "1. 🔄 Sync changes to GitHub"
    echo "2. 🌿 Create feature branch"
    echo "3. 🔀 Merge feature to develop"
    echo "4. 🏷️ Create release"
    echo "5. 📊 Show repository status"
    echo "6. 🚀 Quick sync (commit + push)"
    echo "0. ❌ Exit"
    echo "═══════════════════════════════════════════════"
    read -p "Choose an option: " -n 1 -r
    echo
}

# Main function
main() {
    log "Starting SEAS Financial Tracker GitHub Sync..."
    
    # Check prerequisites
    check_directory
    
    # Show menu
    while true; do
        show_menu
        
        case $REPLY in
            1)
                check_git_status
                sync_to_github
                ;;
            2)
                create_feature_branch
                ;;
            3)
                merge_to_develop
                ;;
            4)
                create_release
                ;;
            5)
                show_status
                ;;
            6)
                commit_changes
                sync_to_github
                ;;
            0)
                log "Goodbye! 👋"
                exit 0
                ;;
            *)
                error "Invalid option. Please try again."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
