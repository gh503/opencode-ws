#!/usr/bin/env python3
"""
Rule Evolution Pipeline - CLI Tool

Command-line interface for rule evolution operations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import pipeline modules
from analyze_errors import (
    analyze_errors,
    AnalysisResult,
    DEFAULT_ERROR_LOGS_DIR,
    DEFAULT_THRESHOLD,
)
from generate_rule import generate_rules_from_analysis, DEFAULT_OUTPUT_DIR, DEFAULT_DB_PATH
from rule_db import (
    RuleDatabaseManager,
    print_rule,
    print_history,
    DEFAULT_DB_PATH,
)


def print_report(result: AnalysisResult) -> None:
    """Print analysis report to console."""
    
    print("\n" + "=" * 60)
    print("ERROR ANALYSIS REPORT")
    print("=" * 60)
    print(f"Generated: {result.timestamp}")
    print()
    
    print(f"Total Errors:     {result.total_errors}")
    print(f"Unique Categories: {result.unique_categories}")
    print(f"Unique Error Codes: {result.unique_error_codes}")
    print(f"Error Clusters:   {len(result.clusters)}")
    print(f"Candidate Rules:  {len(result.candidate_rules)}")
    print()
    
    if result.candidate_rules:
        print("-" * 60)
        print("CANDIDATE RULES (>= {} occurrences)".format(DEFAULT_THRESHOLD))
        print("-" * 60)
        
        for i, candidate in enumerate(result.candidate_rules, 1):
            print(f"\n{i}. {candidate['rule_name']}")
            print(f"   Occurrences: {candidate['occurrences']}")
            print(f"   Category: {candidate['trigger_condition']['category']}")
            print(f"   Error Code: {candidate['trigger_condition']['error_code']}")
            if candidate.get('root_cause'):
                print(f"   Root Cause: {candidate['root_cause'][:60]}...")
            if candidate.get('suggested_fix'):
                print(f"   Fix: {candidate['suggested_fix'][:60]}...")
    
    print("\n" + "=" * 60)


def cmd_analyze(args) -> int:
    """Execute analyze command."""
    
    result = analyze_errors(
        logs_dir=args.logs_dir,
        threshold=args.threshold,
        verbose=args.verbose,
    )
    
    # Print report
    if args.verbose or not args.json:
        print_report(result)
    
    # Save to JSON if requested
    if args.output:
        from analyze_errors import save_analysis_result
        save_analysis_result(result, args.output)
        print(f"\n[INFO] Analysis saved to: {args.output}")
    
    # Print JSON to stdout if requested
    if args.json:
        print(json.dumps(result.__dict__, indent=2, default=str))
    
    # Output GitHub Actions format if GITHUB_OUTPUT is set
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"candidate_count={len(result.candidate_rules)}\n")
            f.write(f"total_errors={result.total_errors}\n")
            f.write(f"unique_clusters={len(result.clusters)}\n")
    
    return 0


def cmd_generate(args) -> int:
    """Execute generate command."""
    
    input_file = args.input
    
    if not Path(input_file).exists():
        print(f"[ERROR] Input file not found: {input_file}")
        return 1
    
    generated = generate_rules_from_analysis(
        analysis_file=input_file,
        output_dir=args.output_dir,
    )
    
    if generated:
        print(f"\n[RESULT] Successfully generated {len(generated)} rule files")
        
        if args.verbose:
            for f in generated:
                print(f"  - {f}")
        
        return 0
    else:
        print("[RESULT] No rules generated")
        return 1


def cmd_report(args) -> int:
    """Execute report command - show summary of all rules."""
    
    # Check rules directories
    rules_dirs = [
        Path("rules/global"),
        Path("rules/candidates"),
        Path("rules/deprecated"),
    ]
    
    print("\n" + "=" * 60)
    print("RULES STATUS REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.utcnow().isoformat()}")
    print()
    
    total_rules = 0
    
    for rules_dir in rules_dirs:
        if not rules_dir.exists():
            continue
        
        rules = list(rules_dir.glob("*.md"))
        status = rules_dir.name
        
        print(f"{status.upper()} ({len(rules)} rules)")
        
        for rule in rules:
            print(f"  - {rule.name}")
        
        total_rules += len(rules)
        print()
    
    print(f"Total Rules: {total_rules}")
    print("=" * 60)
    
    if total_rules == 0:
        print("\n[INFO] No rules found. Run 'analyze' to generate candidate rules.")
    
    return 0


# Database commands

def cmd_db_list(args) -> int:
    """Execute db-list command - show all rules in database."""
    db_path = args.db or DEFAULT_DB_PATH
    manager = RuleDatabaseManager(db_path)
    
    rules = manager.list_rules(status=args.status, category=args.category)
    
    print("\n" + "=" * 60)
    print("RULE DATABASE")
    print("=" * 60)
    print(f"Database: {db_path}")
    print()
    
    stats = manager.get_statistics()
    print(f"Total: {stats['total_rules']}")
    print(f"  - Candidate: {stats['candidate_rules']}")
    print(f"  - Global: {stats['global_rules']}")
    print(f"  - Deprecated: {stats['deprecated_rules']}")
    print(f"  - Stale: {stats['stale_rules']}")
    print()
    
    if not rules:
        print("No rules found.")
        return 0
    
    print("Rules:")
    for rule in rules:
        print(f"  {rule.rule_id} | {rule.status:10} | v{rule.current_version} | {rule.category}")
    
    return 0


def cmd_db_show(args) -> int:
    """Execute db-show command - show detailed rule information."""
    db_path = args.db or DEFAULT_DB_PATH
    manager = RuleDatabaseManager(db_path)
    
    rule = manager.get_rule(args.rule_id)
    if not rule:
        print(f"[ERROR] Rule not found: {args.rule_id}")
        return 1
    
    print_rule(rule)
    
    if args.history:
        history = manager.get_history(args.rule_id)
        if history:
            print_history(args.rule_id, history)
    
    return 0


def cmd_db_status(args) -> int:
    """Execute db-status command - change rule status."""
    db_path = args.db or DEFAULT_DB_PATH
    manager = RuleDatabaseManager(db_path)
    
    rule = manager.change_status(args.rule_id, args.status, args.changelog or "")
    if not rule:
        print(f"[ERROR] Rule not found: {args.rule_id}")
        return 1
    
    print(f"[OK] Rule {args.rule_id} status changed to: {args.status}")
    return 0


def cmd_db_rollback(args) -> int:
    """Execute db-rollback command - rollback rule to previous version."""
    db_path = args.db or DEFAULT_DB_PATH
    manager = RuleDatabaseManager(db_path)
    
    rule = manager.rollback(args.rule_id, args.version)
    if not rule:
        print(f"[ERROR] Rollback failed. Check rule ID and version.")
        return 1
    
    print(f"[OK] Rule {args.rule_id} rolled back to version {args.version}")
    print(f"      New version: {rule.current_version}")
    return 0


def cmd_db_export(args) -> int:
    """Execute db-export command - export rule content."""
    db_path = args.db or DEFAULT_DB_PATH
    manager = RuleDatabaseManager(db_path)
    
    content = manager.export_rule(args.rule_id, args.format)
    if not content:
        print(f"[ERROR] Rule not found: {args.rule_id}")
        return 1
    
    print(content)
    return 0


def main():
    """Main CLI entry point."""
    
    parser = argparse.ArgumentParser(
        prog="opencode-evolve",
        description="Rule Evolution Pipeline CLI - AI Engineering Governance System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  opencode-evolve analyze                    Analyze error logs
  opencode-evolve analyze --threshold 3      Lower threshold to 3
  opencode-evolve generate -i result.json    Generate rules from analysis
  opencode-evolve report                     Show rules status
  opencode-evolve db list                    List rules in database
  opencode-evolve db show validation_PY-VAL-001 --history
  opencode-evolve db status validation_PY-VAL-001 global
  opencode-evolve db rollback validation_PY-VAL-001 1.0.0
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze error logs and identify patterns",
    )
    analyze_parser.add_argument(
        "--logs-dir",
        default=DEFAULT_ERROR_LOGS_DIR,
        help=f"Directory containing error logs (default: {DEFAULT_ERROR_LOGS_DIR})",
    )
    analyze_parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum occurrences to generate candidate rule (default: {DEFAULT_THRESHOLD})",
    )
    analyze_parser.add_argument(
        "--output", "-o",
        help="Output file for analysis result (JSON)",
    )
    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output analysis result as JSON to stdout",
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate candidate rules from analysis result",
    )
    generate_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input analysis result JSON file",
    )
    generate_parser.add_argument(
        "--output-dir", "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for generated rules (default: {DEFAULT_OUTPUT_DIR})",
    )
    generate_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    generate_parser.set_defaults(func=cmd_generate)
    
    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Show rules status report",
    )
    report_parser.set_defaults(func=cmd_report)
    
    # Database commands
    db_parser = subparsers.add_parser(
        "db",
        help="Database management commands",
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database commands")
    
    # db-list
    db_list_parser = db_subparsers.add_parser(
        "list",
        help="List all rules in database",
    )
    db_list_parser.add_argument("--status", help="Filter by status")
    db_list_parser.add_argument("--category", help="Filter by category")
    db_list_parser.add_argument("--db", help="Database path")
    db_list_parser.set_defaults(func=cmd_db_list)
    
    # db-show
    db_show_parser = db_subparsers.add_parser(
        "show",
        help="Show rule details",
    )
    db_show_parser.add_argument("rule_id", help="Rule ID to show")
    db_show_parser.add_argument("--history", action="store_true", help="Show version history")
    db_show_parser.add_argument("--db", help="Database path")
    db_show_parser.set_defaults(func=cmd_db_show)
    
    # db-status
    db_status_parser = db_subparsers.add_parser(
        "status",
        help="Change rule status",
    )
    db_status_parser.add_argument("rule_id", help="Rule ID")
    db_status_parser.add_argument("status", choices=["candidate", "global", "deprecated", "stale"], help="New status")
    db_status_parser.add_argument("--changelog", help="Change description")
    db_status_parser.add_argument("--db", help="Database path")
    db_status_parser.set_defaults(func=cmd_db_status)
    
    # db-rollback
    db_rollback_parser = db_subparsers.add_parser(
        "rollback",
        help="Rollback rule to previous version",
    )
    db_rollback_parser.add_argument("rule_id", help="Rule ID")
    db_rollback_parser.add_argument("version", help="Target version")
    db_rollback_parser.add_argument("--db", help="Database path")
    db_rollback_parser.set_defaults(func=cmd_db_rollback)
    
    # db-export
    db_export_parser = db_subparsers.add_parser(
        "export",
        help="Export rule content",
    )
    db_export_parser.add_argument("rule_id", help="Rule ID")
    db_export_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Export format")
    db_export_parser.add_argument("--db", help="Database path")
    db_export_parser.set_defaults(func=cmd_db_export)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        # Handle db subcommands
        if args.command == "db":
            if not hasattr(args, "db_command"):
                parser.print_help()
                return 1
            return args.func(args)
        return args.func(args)
    except KeyboardInterrupt:
        print("\n[ABORTED] Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"[ERROR] {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
