# GitHub Actions Runner Optimization Guide

This document outlines the runner sizing standards and best practices for cookiecutter-django workflows.

## Runner Sizing Guidelines

### Small Jobs (10-15 minutes)
**Runner:** `ubuntu-latest` (2-core, 7 GB RAM)
**Use cases:**
- Simple API calls (issue management, changelog updates)
- Lightweight script execution
- Pre-commit hook updates
- Security scanning

**Examples:**
- `issue-manager`
- `update-changelog`
- `update-contributors`
- `django-issue-checker`

### Medium Jobs (15-30 minutes)
**Runner:** `ubuntu-latest` (2-core, 7 GB RAM)
**Use cases:**
- Basic test suites
- Linting operations
- Documentation builds
- Simple builds without heavy dependencies

**Examples:**
- `linter` job in CI
- Basic pytest runs without Docker

### Large Jobs (30-45 minutes)
**Runner:** `ubuntu-latest` (2-core, 7 GB RAM)
**Use cases:**
- Docker builds and tests
- Full integration test suites
- Complex build pipelines
- Multi-service testing

**Examples:**
- `docker` job (Docker builds with multiple configurations)
- `pytest` job with Docker
- `bare` job (tests with services like PostgreSQL and Redis)

### Extra Large Jobs (45+ minutes)
**Runner:** `ubuntu-latest-4-cores` or similar
**Use cases:**
- Parallel matrix builds across multiple OS
- Extensive end-to-end testing
- Performance testing

**Examples:**
- `tests` job (matrix across ubuntu, windows, macOS)

## Timeout Configuration Standards

All jobs should have explicit `timeout-minutes` configured to prevent runaway workflows:

| Job Complexity | Timeout (minutes) | Rationale |
|---------------|-------------------|-----------|
| Simple automation | 10 | Quick operations, fail fast |
| Linting/formatting | 15 | Pre-commit checks, light processing |
| Basic tests | 30 | Standard test suite execution |
| Docker builds | 45 | Image building and testing |
| Matrix builds | 30 per job | Individual matrix job timeout |

## Job Execution Time Tracking

All resource-intensive jobs include execution time tracking:

```yaml
steps:
  - name: Start job timer
    id: timer
    run: echo "start_time=$(date +%s)" >> $GITHUB_OUTPUT

  # ... other steps ...

  - name: Report job execution time
    if: always()
    run: |
      end_time=$(date +%s)
      duration=$((end_time - ${{ steps.timer.outputs.start_time }}))
      echo "Job execution time: ${duration}s"
      echo "execution_time_seconds=${duration}" >> $GITHUB_STEP_SUMMARY
```

This tracking helps:
- Identify jobs that may need runner optimization
- Detect performance regressions
- Right-size timeout values

## Best Practices

### 1. Use Appropriate Timeouts
- Always set explicit `timeout-minutes`
- Set timeouts to 1.5-2x expected job duration
- Fail fast to free up resources

### 2. Optimize Resource Usage
- Use dependency caching (pip, npm, docker layers)
- Enable `DOCKER_BUILDKIT` for faster builds
- Use `concurrency` groups to cancel redundant runs

### 3. Monitor Performance
- Review job execution times in step summaries
- Adjust timeouts based on actual performance
- Consider splitting long-running jobs

### 4. Runner Selection
- Start with `ubuntu-latest` for most jobs
- Only upgrade to larger runners when metrics show need
- Use matrix strategies efficiently to parallelize work

## Cost Optimization

### Current Configuration
All workflows use GitHub-hosted runners:
- Free for public repositories
- Metered for private repositories

### Monitoring
Track workflow costs in GitHub billing:
- Review Actions usage regularly
- Identify expensive workflows
- Optimize based on actual usage patterns

## Future Considerations

### Self-Hosted Runners
Consider self-hosted runners when:
- Running many workflows in private repositories
- Needing specific hardware/software configurations
- Requiring faster execution times
- Cost optimization for high-volume usage

### Runner Tags for Self-Hosted
If implementing self-hosted runners, use consistent tags:
- `self-hosted-small` - 2 core, 4GB RAM
- `self-hosted-medium` - 4 core, 8GB RAM
- `self-hosted-large` - 8 core, 16GB RAM

## Maintenance

Review and update this guide:
- Quarterly performance reviews
- After significant workflow changes
- When adding new workflow types
- Based on GitHub Actions feature updates

---

Last Updated: 2024
