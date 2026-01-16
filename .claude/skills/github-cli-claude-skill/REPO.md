# Repository Management

Comprehensive guide for managing GitHub repositories using the gh CLI.

## Table of Contents
- [Viewing Repositories](#viewing-repositories)
- [Creating Repositories](#creating-repositories)
- [Cloning Repositories](#cloning-repositories)
- [Forking Repositories](#forking-repositories)
- [Repository Settings](#repository-settings)
- [Branch Management](#branch-management)
- [Common Workflows](#common-workflows)

## Viewing Repositories

### View current repository
```bash
# View details of current repository
gh repo view

# View in browser
gh repo view --web

# Get JSON output
gh repo view --json name,description,url,isPrivate,defaultBranchRef
```

### View any repository
```bash
# View specific repository
gh repo view owner/repo

# View repository README
gh repo view owner/repo --json readme --jq .readme

# View repository topics
gh repo view owner/repo --json repositoryTopics --jq '.repositoryTopics[].topic.name'
```

### List repositories
```bash
# List your repositories
gh repo list

# List repositories for a user/org
gh repo list octocat

# Filter by criteria
gh repo list --limit 50 --public
gh repo list --language python --topic machine-learning

# Get JSON output for processing
gh repo list --json name,url,isPrivate,pushedAt --limit 100
```

## Creating Repositories

### Interactive creation
```bash
# Create repository interactively
gh repo create

# Follow prompts for:
# - Repository name
# - Description
# - Visibility (public/private/internal)
# - Initialize with README
# - Add .gitignore
# - Add license
```

### Non-interactive creation
```bash
# Create public repository with README
gh repo create my-project --public --description "My awesome project" --add-readme

# Create private repository with .gitignore and license
gh repo create my-app --private --gitignore Node --license MIT

# Create repository from template
gh repo create my-site --template owner/template-repo --public

# Create and clone in one command
gh repo create my-project --public --clone

# Create in organization
gh repo create my-org/my-project --public --description "Org project"
```

### Create from existing local directory
```bash
# Initialize git and create remote repository
cd my-existing-project
git init
git add .
git commit -m "Initial commit"
gh repo create --source=. --public --push
```

## Cloning Repositories

### Basic cloning
```bash
# Clone repository
gh repo clone owner/repo

# Clone to specific directory
gh repo clone owner/repo target-directory

# Clone your own repository (shorter syntax)
gh repo clone repo-name
```

### Clone with options
```bash
# Clone with all submodules
gh repo clone owner/repo -- --recurse-submodules

# Shallow clone (faster for large repos)
gh repo clone owner/repo -- --depth 1

# Clone specific branch
gh repo clone owner/repo -- --branch develop
```

## Forking Repositories

### Fork a repository
```bash
# Fork repository to your account
gh repo fork owner/repo

# Fork and clone in one command
gh repo fork owner/repo --clone

# Fork to organization
gh repo fork owner/repo --org my-organization

# Fork without cloning
gh repo fork owner/repo --clone=false

# Fork with custom remote name
gh repo fork owner/repo --remote-name upstream
```

### Sync fork with upstream
```bash
# Sync fork with upstream (updates default branch)
gh repo sync

# Sync specific branch
gh repo sync --branch main

# Sync fork of another repository
gh repo sync owner/repo

# Force sync (overwrite local changes)
gh repo sync --force
```

## Repository Settings

### Edit repository settings
```bash
# Edit repository description and homepage
gh repo edit --description "New description" --homepage "https://example.com"

# Change default branch
gh repo edit --default-branch develop

# Update visibility
gh repo edit --visibility private
gh repo edit --visibility public

# Enable/disable features
gh repo edit --enable-issues
gh repo edit --disable-wiki
gh repo edit --enable-projects
gh repo edit --disable-merge-commit
gh repo edit --enable-squash-merge
gh repo edit --enable-rebase-merge

# Add/remove topics
gh repo edit --add-topic frontend,typescript,react
gh repo edit --remove-topic deprecated
```

### Archive repository
```bash
# Archive repository (read-only)
gh repo archive owner/repo

# Unarchive repository
gh repo unarchive owner/repo
```

### Delete repository
```bash
# Delete repository (DANGEROUS - requires confirmation)
gh repo delete owner/repo

# Delete with confirmation flag
gh repo delete owner/repo --yes
```

## Branch Management

### List branches
```bash
# List branches in current repository
gh api repos/:owner/:repo/branches --jq '.[].name'

# List protected branches
gh api repos/:owner/:repo/branches --jq '.[] | select(.protected == true) | .name'
```

### View branch protection
```bash
# View branch protection rules
gh api repos/:owner/:repo/branches/main/protection

# View required status checks
gh api repos/:owner/:repo/branches/main/protection/required_status_checks
```

### Set branch protection
```bash
# Enable branch protection (requires API call)
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -f required_status_checks='{"strict":true,"contexts":["ci/test"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":2}' \
  -f restrictions=null

# Require signed commits
gh api -X POST repos/:owner/:repo/branches/main/protection/required_signatures

# Require linear history
gh api -X PATCH repos/:owner/:repo \
  -f allow_merge_commit=false \
  -f allow_rebase_merge=true \
  -f allow_squash_merge=true
```

## Common Workflows

### Workflow 1: Start a new project

```bash
# Create repository and initialize
gh repo create my-new-project --public --add-readme --gitignore Node --license MIT

# Clone locally
gh repo clone my-new-project

# Navigate to directory
cd my-new-project

# Add files and make initial commit
echo "console.log('Hello, world!');" > index.js
git add index.js
git commit -m "Add initial code"
git push
```

### Workflow 2: Contribute to an existing project

```bash
# Fork and clone the repository
gh repo fork upstream-owner/repo --clone

# Navigate to directory
cd repo

# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to your fork
git push -u origin feature/my-feature

# Create pull request
gh pr create --fill
```

### Workflow 3: Set up team repository

```bash
# Create organization repository
gh repo create my-org/team-project \
  --public \
  --description "Team collaboration project" \
  --gitignore Python \
  --license Apache-2.0

# Clone and set up
gh repo clone my-org/team-project
cd team-project

# Configure branch protection
gh api -X PUT repos/my-org/team-project/branches/main/protection \
  -f required_pull_request_reviews='{"required_approving_review_count":2}' \
  -f enforce_admins=false

# Enable issues and projects
gh repo edit --enable-issues --enable-projects
```

### Workflow 4: Mirror repository

```bash
# Clone with mirror flag
git clone --mirror https://github.com/source/repo.git
cd repo.git

# Create new repository
gh repo create destination/repo --public

# Push mirror to new repository
git push --mirror https://github.com/destination/repo.git
```

### Workflow 5: Batch repository operations

```bash
# Clone multiple repositories
repos=("owner/repo1" "owner/repo2" "owner/repo3")
for repo in "${repos[@]}"; do
  gh repo clone "$repo"
done

# Update all local repositories
for dir in */; do
  cd "$dir"
  echo "Updating $dir"
  git pull
  cd ..
done

# List all repositories with specific topic
gh repo list my-org --topic production --json name,url --limit 100
```

## Advanced Techniques

### Using gh API for custom operations

```bash
# Get repository statistics
gh api repos/:owner/:repo --jq '{stars: .stargazers_count, forks: .forks_count, size: .size}'

# List all collaborators
gh api repos/:owner/:repo/collaborators --jq '.[].login'

# Get repository languages
gh api repos/:owner/:repo/languages --jq 'to_entries | map({language: .key, bytes: .value})'

# Check repository vulnerability alerts
gh api repos/:owner/:repo/vulnerability-alerts
```

### Repository templates

```bash
# Create template repository
gh repo create my-template --public --template
gh repo edit --enable-template

# Create repository from template
gh repo create my-new-project --template owner/my-template --public

# List template repositories
gh repo list --json name,isTemplate --jq '.[] | select(.isTemplate == true)'
```

### Working with GitHub Pages

```bash
# Enable GitHub Pages (via API)
gh api repos/:owner/:repo/pages -X POST -f source='{"branch":"main","path":"/"}'

# Get Pages information
gh api repos/:owner/:repo/pages --jq '{url: .html_url, status: .status}'

# Disable GitHub Pages
gh api repos/:owner/:repo/pages -X DELETE
```

## Troubleshooting

### Authentication issues
```bash
# Check authentication status
gh auth status

# Re-authenticate
gh auth login

# Switch accounts
gh auth switch
```

### Permission errors
```bash
# Verify you have access to the repository
gh repo view owner/repo

# Check your permissions
gh api repos/:owner/:repo --jq '.permissions'
```

### Repository not found
```bash
# Verify repository exists
gh repo view owner/repo

# Check spelling and organization name
gh repo list owner --limit 100 | grep repo-name
```

## Tips and Best Practices

1. **Use JSON output for automation**: Add `--json` flag for structured data
2. **Specify repository explicitly**: Use `-R owner/repo` when not in repository directory
3. **Template repositories**: Create templates for common project structures
4. **Branch protection**: Always enable on main/production branches
5. **Regular syncing**: Keep forks synchronized with upstream
6. **Descriptive names**: Use clear repository names and descriptions
7. **Topics**: Add relevant topics for discoverability
8. **README files**: Always include comprehensive README
9. **License selection**: Choose appropriate license at creation
10. **Backup important repositories**: Clone locally or mirror to multiple locations

## Quick Reference

```bash
# View
gh repo view [owner/repo]                     # View repository details
gh repo list [owner]                          # List repositories

# Create
gh repo create [name]                         # Create repository
gh repo create --template owner/template      # Create from template

# Clone/Fork
gh repo clone owner/repo                      # Clone repository
gh repo fork owner/repo --clone               # Fork and clone

# Sync
gh repo sync                                  # Sync fork with upstream

# Edit
gh repo edit --description "text"             # Edit description
gh repo edit --visibility private             # Change visibility
gh repo edit --enable-issues                  # Enable features

# Archive/Delete
gh repo archive owner/repo                    # Archive repository
gh repo delete owner/repo                     # Delete repository (careful!)
```
