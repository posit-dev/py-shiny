# GitHub Actions & Workflow Management

Comprehensive guide for managing GitHub Actions workflows using the gh CLI.

## Table of Contents
- [Viewing Workflows](#viewing-workflows)
- [Triggering Workflows](#triggering-workflows)
- [Viewing Workflow Runs](#viewing-workflow-runs)
- [Managing Workflow Runs](#managing-workflow-runs)
- [Downloading Artifacts](#downloading-artifacts)
- [Workflow Logs](#workflow-logs)
- [Secrets and Variables](#secrets-and-variables)
- [Common Workflows](#common-workflows)

## Viewing Workflows

### List workflows
```bash
# List all workflows
gh workflow list

# List workflows with details
gh workflow list --all

# Get JSON output
gh workflow list --json name,id,state,path

# List only active workflows
gh workflow list --json name,state | jq '.[] | select(.state == "active")'

# List disabled workflows
gh workflow list --json name,state | jq '.[] | select(.state == "disabled_manually")'
```

### View specific workflow
```bash
# View workflow by name
gh workflow view "CI"

# View workflow by filename
gh workflow view ci.yml

# View workflow in browser
gh workflow view ci.yml --web

# Get workflow details as JSON
gh workflow view ci.yml --json name,id,path,state,createdAt,updatedAt

# View workflow YAML
gh workflow view ci.yml --yaml
```

## Triggering Workflows

### Run workflow
```bash
# Run workflow (interactive)
gh workflow run

# Run specific workflow by name
gh workflow run "CI"

# Run specific workflow by filename
gh workflow run ci.yml

# Run workflow on specific branch
gh workflow run ci.yml --ref develop

# Run workflow with inputs
gh workflow run deploy.yml --ref main -f environment=production -f version=v1.2.3

# Run workflow with raw inputs (JSON)
gh workflow run workflow.yml --raw-field 'config={"key":"value"}'

# Run workflow with boolean input
gh workflow run workflow.yml -f debug=true
```

### Manual workflow dispatch example
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - development
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: true
        type: string
      dry_run:
        description: 'Perform a dry run'
        required: false
        type: boolean
        default: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"
          echo "Dry run: ${{ inputs.dry_run }}"
```

```bash
# Trigger with inputs
gh workflow run deploy.yml \
  -f environment=production \
  -f version=v1.2.3 \
  -f dry_run=false
```

### Enable/Disable workflows
```bash
# Enable workflow
gh workflow enable ci.yml

# Disable workflow
gh workflow disable ci.yml

# Get workflow status
gh workflow view ci.yml --json state --jq .state
```

## Viewing Workflow Runs

### List workflow runs
```bash
# List recent workflow runs
gh run list

# List runs for specific workflow
gh run list --workflow ci.yml

# List runs on specific branch
gh run list --branch main

# List failed runs
gh run list --status failure

# List runs by event
gh run list --event push
gh run list --event pull_request
gh run list --event workflow_dispatch

# List runs by actor
gh run list --user username

# Limit results
gh run list --limit 50

# Get JSON output
gh run list --json number,status,conclusion,headBranch,event,createdAt

# List runs created in last 24 hours
gh run list --created ">=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)"
```

### View specific run
```bash
# View run details
gh run view <run-id>

# View latest run
gh run view

# View run in browser
gh run view <run-id> --web

# View run with job details
gh run view <run-id> --verbose

# Get run details as JSON
gh run view <run-id> --json status,conclusion,headBranch,workflowName,event,createdAt

# View run attempt (for re-runs)
gh run view <run-id> --attempt 2
```

### Watch workflow run
```bash
# Watch run in real-time
gh run watch <run-id>

# Watch latest run
gh run watch

# Watch with exit on failure
gh run watch <run-id> --exit-status

# Watch specific interval
gh run watch <run-id> --interval 5
```

## Managing Workflow Runs

### Re-run workflows
```bash
# Re-run entire workflow
gh run rerun <run-id>

# Re-run only failed jobs
gh run rerun <run-id> --failed

# Re-run specific job
gh run rerun <run-id> --job <job-id>

# Re-run with debug logging
gh run rerun <run-id> --debug
```

### Cancel workflow runs
```bash
# Cancel specific run
gh run cancel <run-id>

# Cancel all runs for a workflow
gh run list --workflow ci.yml --json databaseId --jq '.[].databaseId' \
  | xargs -I {} gh run cancel {}

# Cancel all in-progress runs
gh run list --status in_progress --json databaseId --jq '.[].databaseId' \
  | xargs -I {} gh run cancel {}
```

### Delete workflow runs
```bash
# Delete specific run
gh run delete <run-id>

# Confirm deletion
gh run delete <run-id> --confirm

# Delete old runs (older than 30 days)
gh run list --json databaseId,createdAt --limit 1000 \
  | jq --arg date "$(date -u -d '30 days ago' +%Y-%m-%d)" \
    '.[] | select(.createdAt < $date) | .databaseId' \
  | xargs -I {} gh run delete {} --confirm

# Delete all failed runs
gh run list --status failure --json databaseId --jq '.[].databaseId' \
  | xargs -I {} gh run delete {} --confirm
```

## Downloading Artifacts

### Download artifacts
```bash
# Download artifacts from latest run
gh run download

# Download artifacts from specific run
gh run download <run-id>

# Download specific artifact
gh run download <run-id> --name artifact-name

# Download to specific directory
gh run download <run-id> --dir ./downloads

# List available artifacts
gh run view <run-id> --json artifacts --jq '.artifacts[] | {name: .name, size: .sizeInBytes}'
```

### Download using API
```bash
# Get artifact download URL
gh api repos/:owner/:repo/actions/artifacts/:artifact-id/zip > artifact.zip

# List all artifacts
gh api repos/:owner/:repo/actions/artifacts --jq '.artifacts[] | {name: .name, id: .id}'

# Download specific artifact by name
ARTIFACT_ID=$(gh api repos/:owner/:repo/actions/runs/<run-id>/artifacts \
  --jq '.artifacts[] | select(.name == "build-output") | .id')
gh api repos/:owner/:repo/actions/artifacts/$ARTIFACT_ID/zip > build-output.zip
```

## Workflow Logs

### View logs
```bash
# View logs for specific run
gh run view <run-id> --log

# View logs for specific job
gh run view <run-id> --job <job-id> --log

# View failed job logs only
gh run view <run-id> --log-failed

# Save logs to file
gh run view <run-id> --log > workflow.log

# View logs in browser
gh run view <run-id> --web
```

### Download logs
```bash
# Download all logs as zip
gh run download <run-id> --log

# Download logs to specific directory
gh run download <run-id> --log --dir ./logs

# Extract logs
unzip -d logs logs.zip
```

### Parse logs
```bash
# Search logs for errors
gh run view <run-id> --log | grep -i error

# Extract failed steps
gh run view <run-id> --log | grep -A 5 "Error:"

# Count warnings
gh run view <run-id> --log | grep -c "warning"
```

## Secrets and Variables

### List secrets
```bash
# List repository secrets
gh secret list

# List organization secrets
gh secret list --org my-org

# List environment secrets
gh secret list --env production

# Get secret metadata (not value)
gh api repos/:owner/:repo/actions/secrets/SECRET_NAME
```

### Set secrets
```bash
# Set secret interactively
gh secret set SECRET_NAME

# Set secret from value
echo "secret-value" | gh secret set SECRET_NAME

# Set secret from file
gh secret set SECRET_NAME < secret.txt

# Set secret for specific environment
gh secret set SECRET_NAME --env production

# Set organization secret
gh secret set SECRET_NAME --org my-org
```

### Delete secrets
```bash
# Delete repository secret
gh secret delete SECRET_NAME

# Delete environment secret
gh secret delete SECRET_NAME --env production

# Delete organization secret
gh secret delete SECRET_NAME --org my-org
```

### Variables
```bash
# List variables
gh variable list

# Set variable
gh variable set VAR_NAME --body "value"

# Set variable for environment
gh variable set VAR_NAME --body "value" --env production

# Get variable
gh variable get VAR_NAME

# Delete variable
gh variable delete VAR_NAME
```

## Common Workflows

### Workflow 1: Run CI and wait for results

```bash
# Trigger CI workflow
gh workflow run ci.yml --ref feature/branch

# Get the latest run ID for this workflow
RUN_ID=$(gh run list --workflow ci.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# Watch the run
gh run watch $RUN_ID --exit-status

# If successful, check results
if [ $? -eq 0 ]; then
  echo "CI passed!"
  gh run view $RUN_ID
else
  echo "CI failed!"
  gh run view $RUN_ID --log-failed
fi
```

### Workflow 2: Deploy to production

```bash
# Trigger deployment workflow
gh workflow run deploy.yml \
  --ref main \
  -f environment=production \
  -f version=v2.1.0

# Get run ID
echo "Waiting for deployment to start..."
sleep 5
RUN_ID=$(gh run list --workflow deploy.yml --limit 1 --json databaseId --jq '.[0].databaseId')

# Watch deployment
gh run watch $RUN_ID

# Verify deployment
gh run view $RUN_ID --web
```

### Workflow 3: Debug failing workflow

```bash
# Find failed run
gh run list --workflow ci.yml --status failure --limit 1

# Get run ID
RUN_ID=$(gh run list --workflow ci.yml --status failure --limit 1 --json databaseId --jq '.[0].databaseId')

# View failed jobs
gh run view $RUN_ID --log-failed

# Download artifacts for inspection
gh run download $RUN_ID

# Re-run with debug logging
gh run rerun $RUN_ID --debug

# Watch re-run
NEW_RUN_ID=$(gh run list --workflow ci.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch $NEW_RUN_ID
```

### Workflow 4: Cleanup old workflow runs

```bash
# Delete runs older than 90 days
CUTOFF_DATE=$(date -u -d '90 days ago' +%Y-%m-%d)

gh run list --json databaseId,createdAt,conclusion --limit 1000 \
  | jq --arg date "$CUTOFF_DATE" \
    '.[] | select(.createdAt < $date) | .databaseId' \
  | while read -r run_id; do
      echo "Deleting run $run_id"
      gh run delete "$run_id" --confirm
    done

# Delete all cancelled runs
gh run list --status cancelled --json databaseId --jq '.[].databaseId' \
  | xargs -I {} gh run delete {} --confirm

# Delete failed runs for specific workflow
gh run list --workflow ci.yml --status failure --json databaseId --jq '.[].databaseId' \
  | xargs -I {} gh run delete {} --confirm
```

### Workflow 5: Batch workflow operations

```bash
# Trigger multiple workflows
for workflow in ci.yml test.yml lint.yml; do
  echo "Running $workflow"
  gh workflow run "$workflow" --ref main
done

# Wait for all to complete
echo "Waiting for workflows to complete..."
sleep 10

# Check status of all
for workflow in ci.yml test.yml lint.yml; do
  RUN_ID=$(gh run list --workflow "$workflow" --limit 1 --json databaseId --jq '.[0].databaseId')
  STATUS=$(gh run view "$RUN_ID" --json status,conclusion --jq '{status, conclusion}')
  echo "$workflow: $STATUS"
done
```

### Workflow 6: Monitor workflow queue

```bash
# Monitor queued and in-progress runs
watch -n 5 'gh run list --status queued,in_progress --json workflowName,status,createdAt'

# Check workflow concurrency
gh run list --status in_progress --json workflowName \
  | jq 'group_by(.workflowName) | map({workflow: .[0].workflowName, count: length})'

# Alert on long-running workflows (over 30 minutes)
gh run list --status in_progress --json databaseId,workflowName,createdAt \
  | jq --arg cutoff "$(date -u -d '30 minutes ago' +%Y-%m-%dT%H:%M:%SZ)" \
    '.[] | select(.createdAt < $cutoff) | "⚠️ \(.workflowName) (Run \(.databaseId)) running for >30min"' -r
```

## Advanced Techniques

### Custom workflow filters
```bash
# Find workflows with specific conclusion
gh run list --json workflowName,conclusion --jq '
  group_by(.conclusion) |
  map({conclusion: .[0].conclusion, count: length, workflows: [.[].workflowName] | unique})
'

# Calculate success rate
gh run list --limit 100 --json conclusion --jq '
  group_by(.conclusion) |
  map({conclusion: .[0].conclusion, count: length}) |
  {total: (map(.count) | add), details: .}
'

# Find slowest workflow runs
gh run list --limit 50 --json workflowName,updatedAt,createdAt \
  | jq 'map({
      workflow: .workflowName,
      duration: (((.updatedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) / 60)
    }) | sort_by(.duration) | reverse | .[0:10]'
```

### Matrix strategy workflows
```yaml
# .github/workflows/matrix.yml
name: Matrix Build
on: [push]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [14, 16, 18]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

```bash
# Trigger matrix workflow
gh workflow run matrix.yml

# View matrix results
RUN_ID=$(gh run list --workflow matrix.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view $RUN_ID --verbose

# Re-run only failed matrix jobs
gh run rerun $RUN_ID --failed
```

### Workflow caching analysis
```bash
# Check cache usage in workflow
gh api repos/:owner/:repo/actions/cache/usage

# View cache entries
gh api repos/:owner/:repo/actions/caches --jq '.actions_caches[] | {key: .key, size_mb: (.size_in_bytes / 1024 / 1024)}'

# Delete specific cache
gh api repos/:owner/:repo/actions/caches/:cache-id -X DELETE

# Clear all caches
gh api repos/:owner/:repo/actions/caches --jq '.actions_caches[].id' \
  | xargs -I {} gh api repos/:owner/:repo/actions/caches/{} -X DELETE
```

### Workflow billing and usage
```bash
# Get Actions usage (minutes)
gh api repos/:owner/:repo/actions/runs \
  --jq 'reduce .workflow_runs[] as $run (0; . + ($run.run_duration_ms // 0)) | . / 60000 | "Total minutes: \(.)"'

# Get artifact storage usage
gh api repos/:owner/:repo/actions/artifacts \
  --jq 'reduce .artifacts[] as $a (0; . + $a.size_in_bytes) | . / 1024 / 1024 / 1024 | "Total GB: \(.)"'

# Monthly run count
gh run list --created ">=$(date -u -d 'month ago' +%Y-%m-%d)" --limit 1000 --json databaseId \
  | jq 'length | "Runs this month: \(.)"'
```

## Tips and Best Practices

1. **Use workflow dispatch**: Add `workflow_dispatch` for manual triggers
2. **Monitor queue times**: Track queued runs to optimize concurrency
3. **Clean up regularly**: Delete old runs to save storage
4. **Use artifacts wisely**: Artifacts consume storage quota
5. **Cache dependencies**: Use caching to speed up workflows
6. **Fail fast**: Configure matrix builds to fail fast
7. **Separate workflows**: Split into multiple workflows for better parallelism
8. **Use environments**: Configure environment protection rules
9. **Secrets management**: Rotate secrets regularly
10. **Monitor costs**: Track Actions minutes usage
11. **Debug locally**: Use act or similar tools for local testing
12. **Required checks**: Configure required status checks for PRs

## Quick Reference

```bash
# Workflows
gh workflow list                               # List all workflows
gh workflow view ci.yml                        # View workflow details
gh workflow run ci.yml                         # Run workflow
gh workflow enable ci.yml                      # Enable workflow
gh workflow disable ci.yml                     # Disable workflow

# Runs
gh run list                                    # List recent runs
gh run list --workflow ci.yml                  # List runs for workflow
gh run view <run-id>                           # View run details
gh run watch <run-id>                          # Watch run in real-time
gh run rerun <run-id>                          # Re-run workflow
gh run rerun <run-id> --failed                 # Re-run failed jobs
gh run cancel <run-id>                         # Cancel run
gh run delete <run-id>                         # Delete run

# Logs & Artifacts
gh run view <run-id> --log                     # View logs
gh run view <run-id> --log-failed              # View failed logs
gh run download <run-id>                       # Download artifacts
gh run download <run-id> --name artifact       # Download specific artifact

# Secrets & Variables
gh secret list                                 # List secrets
gh secret set NAME                             # Set secret
gh secret delete NAME                          # Delete secret
gh variable list                               # List variables
gh variable set NAME --body "value"            # Set variable

# Common patterns
gh run list --status failure                   # Find failed runs
gh run list --workflow ci.yml --limit 5        # Recent CI runs
gh run watch $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')  # Watch latest
```
