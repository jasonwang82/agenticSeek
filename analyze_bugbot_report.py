#!/usr/bin/env python3
"""
Analyze BugBot report to identify files with most issues
"""

import re
from collections import defaultdict

def analyze_report():
    # Read the report
    with open('bugbot_report.txt', 'r') as f:
        content = f.read()
    
    # Parse issues by file
    file_issues = defaultdict(list)
    current_issue = {}
    
    for line in content.split('\n'):
        if line.startswith('['):
            if current_issue:
                file_issues[current_issue['file']].append(current_issue)
            severity_match = re.match(r'\[(\w+)\]\s+(.+)', line)
            if severity_match:
                current_issue = {
                    'severity': severity_match.group(1),
                    'type': severity_match.group(2)
                }
        elif line.startswith('File:'):
            file_match = re.match(r'File:\s+(.+):(\d+)', line)
            if file_match:
                current_issue['file'] = file_match.group(1)
                current_issue['line'] = int(file_match.group(2))
        elif line.startswith('Description:'):
            desc_match = re.match(r'Description:\s+(.+)', line)
            if desc_match:
                current_issue['description'] = desc_match.group(1)
    
    # Don't forget the last issue
    if current_issue and 'file' in current_issue:
        file_issues[current_issue['file']].append(current_issue)
    
    # Sort files by number of issues
    sorted_files = sorted(file_issues.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("🔍 Files with Most Issues:")
    print("=" * 60)
    
    # Show top 10 files
    for i, (filename, issues) in enumerate(sorted_files[:10]):
        severity_count = defaultdict(int)
        for issue in issues:
            severity_count[issue['severity']] += 1
        
        print(f"\n{i+1}. {filename}")
        print(f"   Total issues: {len(issues)}")
        print("   By severity:", end="")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if severity_count[sev] > 0:
                print(f" {sev}:{severity_count[sev]}", end="")
        print()
        
        # Show most common issue types for this file
        issue_types = defaultdict(int)
        for issue in issues:
            issue_types[issue['type']] += 1
        
        most_common = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]
        print("   Most common issues:")
        for issue_type, count in most_common:
            print(f"     - {issue_type}: {count}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 Summary Statistics:")
    print(f"Total files with issues: {len(file_issues)}")
    print(f"Average issues per file: {sum(len(issues) for issues in file_issues.values()) / len(file_issues):.1f}")
    
    # Files with security issues
    security_files = []
    for filename, issues in file_issues.items():
        for issue in issues:
            if issue['severity'] in ['CRITICAL', 'HIGH']:
                security_files.append((filename, issue))
                break
    
    if security_files:
        print("\n⚠️  Files with Security Issues (CRITICAL/HIGH):")
        for filename, issue in security_files:
            print(f"  - {filename}")

if __name__ == "__main__":
    analyze_report()