#!/usr/bin/env python3
"""
BugBot - Automated Bug Analysis for AgenticSeek
Searches for common bugs, security issues, and code quality problems
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class BugBot:
    def __init__(self):
        self.bugs_found = []
        self.security_issues = []
        self.code_smells = []
        self.stats = {
            'total_files': 0,
            'files_analyzed': 0,
            'total_issues': 0
        }
    
    def analyze_project(self, root_dir: str = '.'):
        """Main entry point for project analysis"""
        print("🤖 BugBot Starting Analysis...")
        print("=" * 60)
        
        # Analyze Python files
        self.analyze_python_files(root_dir)
        
        # Check for common security issues
        self.check_security_issues(root_dir)
        
        # Check for code quality issues
        self.check_code_quality(root_dir)
        
        # Generate report
        self.generate_report()
    
    def analyze_python_files(self, root_dir: str):
        """Analyze all Python files for bugs"""
        for root, dirs, files in os.walk(root_dir):
            # Skip virtual environments and .git
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    self.stats['total_files'] += 1
                    filepath = os.path.join(root, file)
                    self.analyze_single_file(filepath)
    
    def analyze_single_file(self, filepath: str):
        """Analyze a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.stats['files_analyzed'] += 1
            
            # Check for common Python bugs
            self.check_exception_handling(filepath, content)
            self.check_resource_leaks(filepath, content)
            self.check_type_errors(filepath, content)
            self.check_undefined_variables(filepath, content)
            self.check_infinite_loops(filepath, content)
            
        except Exception as e:
            self.bugs_found.append({
                'file': filepath,
                'line': 0,
                'type': 'FILE_READ_ERROR',
                'description': f'Failed to read file: {str(e)}'
            })
    
    def check_exception_handling(self, filepath: str, content: str):
        """Check for poor exception handling"""
        # Catch bare except
        bare_except = re.finditer(r'^(\s*)except\s*:', content, re.MULTILINE)
        for match in bare_except:
            line_no = content[:match.start()].count('\n') + 1
            self.code_smells.append({
                'file': filepath,
                'line': line_no,
                'type': 'BARE_EXCEPT',
                'description': 'Bare except clause catches all exceptions (including SystemExit)',
                'severity': 'MEDIUM'
            })
        
        # Catch except Exception as e: raise e
        redundant_raise = re.finditer(r'except\s+\w+\s+as\s+(\w+):\s*\n\s*raise\s+\1(?:\s|$)', content, re.MULTILINE)
        for match in redundant_raise:
            line_no = content[:match.start()].count('\n') + 1
            self.code_smells.append({
                'file': filepath,
                'line': line_no,
                'type': 'REDUNDANT_EXCEPTION_RAISE',
                'description': 'Catching and immediately re-raising exception without logging',
                'severity': 'LOW'
            })
    
    def check_resource_leaks(self, filepath: str, content: str):
        """Check for potential resource leaks"""
        # File operations without context manager
        file_open = re.finditer(r'(\w+)\s*=\s*open\s*\(', content)
        for match in file_open:
            var_name = match.group(1)
            line_no = content[:match.start()].count('\n') + 1
            
            # Check if it's closed
            if f'{var_name}.close()' not in content:
                self.bugs_found.append({
                    'file': filepath,
                    'line': line_no,
                    'type': 'RESOURCE_LEAK',
                    'description': f'File opened but may not be closed: {var_name}',
                    'severity': 'HIGH'
                })
    
    def check_type_errors(self, filepath: str, content: str):
        """Check for potential type errors"""
        # String concatenation with non-strings
        string_concat = re.finditer(r'["\'].*["\'].*\+(?!\s*["\'])', content)
        for match in string_concat:
            line_no = content[:match.start()].count('\n') + 1
            self.bugs_found.append({
                'file': filepath,
                'line': line_no,
                'type': 'POTENTIAL_TYPE_ERROR',
                'description': 'Possible string concatenation with non-string',
                'severity': 'MEDIUM'
            })
    
    def check_undefined_variables(self, filepath: str, content: str):
        """Check for potentially undefined variables"""
        try:
            tree = ast.parse(content)
            # This is a simplified check - would need more sophisticated analysis
        except SyntaxError:
            pass
    
    def check_infinite_loops(self, filepath: str, content: str):
        """Check for potential infinite loops"""
        # while True without break
        while_true = re.finditer(r'while\s+True\s*:', content)
        for match in while_true:
            line_no = content[:match.start()].count('\n') + 1
            # Simple check - look for break in next 20 lines
            next_lines = content[match.end():].split('\n')[:20]
            if not any('break' in line for line in next_lines):
                self.code_smells.append({
                    'file': filepath,
                    'line': line_no,
                    'type': 'POTENTIAL_INFINITE_LOOP',
                    'description': 'while True without obvious break condition',
                    'severity': 'MEDIUM'
                })
    
    def check_security_issues(self, root_dir: str):
        """Check for security vulnerabilities"""
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for hardcoded credentials
                        self.check_hardcoded_credentials(filepath, content)
                        
                        # Check for dangerous functions
                        self.check_dangerous_functions(filepath, content)
                        
                        # Check for SQL injection vulnerabilities
                        self.check_sql_injection(filepath, content)
                        
                    except Exception:
                        pass
    
    def check_hardcoded_credentials(self, filepath: str, content: str):
        """Check for hardcoded passwords or API keys"""
        # Common patterns for credentials
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'HARDCODED_PASSWORD'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'HARDCODED_API_KEY'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'HARDCODED_SECRET'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'HARDCODED_TOKEN')
        ]
        
        for pattern, issue_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                # Skip if it's a placeholder
                if 'xxx' in match.group() or 'example' in match.group().lower():
                    continue
                
                self.security_issues.append({
                    'file': filepath,
                    'line': line_no,
                    'type': issue_type,
                    'description': f'Possible hardcoded credential: {match.group()[:30]}...',
                    'severity': 'CRITICAL'
                })
    
    def check_dangerous_functions(self, filepath: str, content: str):
        """Check for use of dangerous functions"""
        dangerous = [
            ('eval\\s*\\(', 'EVAL_USAGE', 'Use of eval() is dangerous'),
            ('exec\\s*\\(', 'EXEC_USAGE', 'Use of exec() without sandboxing'),
            ('shell\\s*=\\s*True', 'SHELL_TRUE', 'subprocess with shell=True is dangerous'),
            ('pickle\\.loads', 'PICKLE_LOADS', 'Unpickling untrusted data is dangerous'),
            ('__import__', 'DYNAMIC_IMPORT', 'Dynamic imports can be dangerous')
        ]
        
        for pattern, issue_type, description in dangerous:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                self.security_issues.append({
                    'file': filepath,
                    'line': line_no,
                    'type': issue_type,
                    'description': description,
                    'severity': 'HIGH'
                })
    
    def check_sql_injection(self, filepath: str, content: str):
        """Check for potential SQL injection vulnerabilities"""
        # Look for string formatting in SQL queries
        sql_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE).*%\s*[^%]',
            r'(SELECT|INSERT|UPDATE|DELETE).*\.format\(',
            r'(SELECT|INSERT|UPDATE|DELETE).*\+\s*["\']'
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_no = content[:match.start()].count('\n') + 1
                self.security_issues.append({
                    'file': filepath,
                    'line': line_no,
                    'type': 'SQL_INJECTION_RISK',
                    'description': 'Potential SQL injection - use parameterized queries',
                    'severity': 'CRITICAL'
                })
    
    def check_code_quality(self, root_dir: str):
        """Check for code quality issues"""
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Check for code complexity
                        self.check_function_length(filepath, content)
                        self.check_magic_numbers(filepath, content)
                        self.check_todos(filepath, content)
                        
                    except Exception:
                        pass
    
    def check_function_length(self, filepath: str, content: str):
        """Check for overly long functions"""
        function_defs = re.finditer(r'^(\s*)def\s+(\w+)', content, re.MULTILINE)
        
        for match in function_defs:
            indent = len(match.group(1))
            func_name = match.group(2)
            start_line = content[:match.start()].count('\n') + 1
            
            # Find end of function (simplified)
            lines = content[match.end():].split('\n')
            func_lines = 0
            for line in lines:
                if line.strip() and not line.startswith(' ' * (indent + 1)):
                    break
                func_lines += 1
            
            if func_lines > 50:
                self.code_smells.append({
                    'file': filepath,
                    'line': start_line,
                    'type': 'LONG_FUNCTION',
                    'description': f'Function {func_name} is {func_lines} lines long (>50)',
                    'severity': 'LOW'
                })
    
    def check_magic_numbers(self, filepath: str, content: str):
        """Check for magic numbers in code"""
        # Look for numeric literals not in common cases
        magic_numbers = re.finditer(r'[^0-9\.](\d{2,})[^0-9]', content)
        for match in magic_numbers:
            number = match.group(1)
            if int(number) not in [10, 100, 1000, 404, 200, 500, 60, 24, 365]:
                line_no = content[:match.start()].count('\n') + 1
                self.code_smells.append({
                    'file': filepath,
                    'line': line_no,
                    'type': 'MAGIC_NUMBER',
                    'description': f'Magic number {number} should be a named constant',
                    'severity': 'LOW'
                })
    
    def check_todos(self, filepath: str, content: str):
        """Check for TODO/FIXME comments"""
        todos = re.finditer(r'#\s*(TODO|FIXME|HACK|XXX|BUG).*', content, re.IGNORECASE)
        for match in todos:
            line_no = content[:match.start()].count('\n') + 1
            self.code_smells.append({
                'file': filepath,
                'line': line_no,
                'type': 'TODO_COMMENT',
                'description': match.group().strip(),
                'severity': 'INFO'
            })
    
    def generate_report(self):
        """Generate and display the bug report"""
        total_issues = len(self.bugs_found) + len(self.security_issues) + len(self.code_smells)
        
        print("\n🤖 BugBot Analysis Complete!")
        print("=" * 60)
        print(f"Files analyzed: {self.stats['files_analyzed']}/{self.stats['total_files']}")
        print(f"Total issues found: {total_issues}")
        print("=" * 60)
        
        # Security Issues (CRITICAL/HIGH)
        if self.security_issues:
            print("\n🔴 SECURITY ISSUES:")
            print("-" * 60)
            for issue in sorted(self.security_issues, key=lambda x: x['severity']):
                print(f"[{issue['severity']}] {issue['type']}")
                print(f"  File: {issue['file']}:{issue['line']}")
                print(f"  {issue['description']}")
                print()
        
        # Bugs (HIGH/MEDIUM)
        if self.bugs_found:
            print("\n🐛 BUGS FOUND:")
            print("-" * 60)
            for bug in self.bugs_found:
                severity = bug.get('severity', 'MEDIUM')
                print(f"[{severity}] {bug['type']}")
                print(f"  File: {bug['file']}:{bug['line']}")
                print(f"  {bug['description']}")
                print()
        
        # Code Smells (LOW/INFO)
        if self.code_smells:
            print("\n💨 CODE SMELLS:")
            print("-" * 60)
            smell_count = {}
            for smell in self.code_smells:
                smell_type = smell['type']
                smell_count[smell_type] = smell_count.get(smell_type, 0) + 1
            
            for smell_type, count in sorted(smell_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {smell_type}: {count} occurrences")
        
        # Summary
        print("\n📊 SUMMARY BY SEVERITY:")
        print("-" * 60)
        all_issues = self.bugs_found + self.security_issues + self.code_smells
        severity_count = {}
        for issue in all_issues:
            sev = issue.get('severity', 'MEDIUM')
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if severity in severity_count:
                print(f"  {severity}: {severity_count[severity]}")
        
        # Save detailed report
        with open('bugbot_report.txt', 'w') as f:
            f.write("BugBot Detailed Report\n")
            f.write("=" * 60 + "\n\n")
            
            for issue in sorted(all_issues, key=lambda x: (x.get('severity', 'Z'), x['file'], x['line'])):
                f.write(f"[{issue.get('severity', 'MEDIUM')}] {issue['type']}\n")
                f.write(f"File: {issue['file']}:{issue['line']}\n")
                f.write(f"Description: {issue['description']}\n")
                f.write("-" * 40 + "\n")
        
        print("\n📄 Detailed report saved to: bugbot_report.txt")
        print("=" * 60)

def main():
    """Run BugBot analysis"""
    bot = BugBot()
    bot.analyze_project('.')

if __name__ == "__main__":
    main()