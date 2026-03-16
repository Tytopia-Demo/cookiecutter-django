#!/usr/bin/env python3
"""
Workflow Performance Analysis Tool

This script analyzes GitHub Actions workflows to identify optimization opportunities
and track performance over time.

Usage:
    python scripts/analyze_workflow_performance.py

Requirements:
    - PyGithub (install via: pip install PyGithub)
    - GITHUB_TOKEN environment variable set
"""

import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

try:
    from github import Github
except ImportError:
    print("Error: PyGithub is required. Install with: pip install PyGithub")
    sys.exit(1)


def analyze_workflows(repo_name, days=30):
    """
    Analyze workflow runs over the specified time period.

    Args:
        repo_name: Full repository name (e.g., 'cookiecutter/cookiecutter-django')
        days: Number of days to analyze (default: 30)
    """
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return

    g = Github(token)
    repo = g.get_repo(repo_name)

    since = datetime.now() - timedelta(days=days)

    print(f"Analyzing workflows for {repo_name}")
    print(f"Period: Last {days} days (since {since.strftime('%Y-%m-%d')})")
    print("=" * 80)

    # Collect workflow statistics
    workflow_stats = defaultdict(lambda: {
        'runs': 0,
        'total_duration': 0,
        'min_duration': float('inf'),
        'max_duration': 0,
        'successes': 0,
        'failures': 0,
        'cancelled': 0,
    })

    workflow_runs = repo.get_workflow_runs(created=f">={since.isoformat()}")

    for run in workflow_runs:
        workflow_name = run.name
        stats = workflow_stats[workflow_name]

        stats['runs'] += 1

        if run.status == 'completed':
            duration = (run.updated_at - run.created_at).total_seconds()
            stats['total_duration'] += duration
            stats['min_duration'] = min(stats['min_duration'], duration)
            stats['max_duration'] = max(stats['max_duration'], duration)

            if run.conclusion == 'success':
                stats['successes'] += 1
            elif run.conclusion == 'failure':
                stats['failures'] += 1
            elif run.conclusion == 'cancelled':
                stats['cancelled'] += 1

    # Display results
    for workflow_name in sorted(workflow_stats.keys()):
        stats = workflow_stats[workflow_name]

        print(f"\nWorkflow: {workflow_name}")
        print(f"  Total runs: {stats['runs']}")
        print(f"  Success: {stats['successes']} | Failure: {stats['failures']} | Cancelled: {stats['cancelled']}")

        if stats['total_duration'] > 0:
            avg_duration = stats['total_duration'] / (stats['successes'] + stats['failures'])
            print(f"  Duration - Avg: {avg_duration:.0f}s | Min: {stats['min_duration']:.0f}s | Max: {stats['max_duration']:.0f}s")

            # Recommendations
            if avg_duration > 3600:  # > 1 hour
                print("  ⚠️  Consider: Job is taking over 1 hour - review for optimization opportunities")
            if stats['max_duration'] > 1.5 * avg_duration:
                print("  ⚠️  Consider: High duration variance - investigate outliers")

        success_rate = (stats['successes'] / stats['runs'] * 100) if stats['runs'] > 0 else 0
        print(f"  Success rate: {success_rate:.1f}%")

        if success_rate < 90:
            print("  ⚠️  Consider: Low success rate - investigate test flakiness")

    print("\n" + "=" * 80)
    print("Analysis complete")


def main():
    """Main entry point."""
    # Default to analyzing cookiecutter-django
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'cookiecutter/cookiecutter-django')
    analyze_workflows(repo_name, days=30)


if __name__ == '__main__':
    main()
