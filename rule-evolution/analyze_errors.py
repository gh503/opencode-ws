#!/usr/bin/env python3
"""
Rule Evolution Pipeline - Error Analysis Module

Analyzes error logs to identify repeated patterns and generate candidate rules.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# Configuration
DEFAULT_ERROR_LOGS_DIR = "error-logs"
DEFAULT_OUTPUT_DIR = "rules/candidates"
DEFAULT_THRESHOLD = 5


@dataclass
class ErrorEntry:
    """Represents a single error log entry."""
    error_code: str
    category: str
    message: str
    root_cause: Optional[str] = None
    severity: Optional[str] = None
    timestamp: Optional[str] = None
    correlation_id: Optional[str] = None
    fix: Optional[str] = None
    details: Optional[dict] = None


@dataclass
class ErrorCluster:
    """Represents a cluster of similar errors."""
    category: str
    error_code: str
    count: int
    sample_messages: list[str] = field(default_factory=list)
    root_causes: dict[str, int] = field(default_factory=dict)
    severities: dict[str, int] = field(default_factory=dict)
    fix_suggestions: dict[str, int] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Results from error analysis."""
    total_errors: int
    unique_categories: int
    unique_error_codes: int
    clusters: list[ErrorCluster]
    candidate_rules: list[dict]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


def load_error_logs(logs_dir: str) -> list[ErrorEntry]:
    """Load all error log files from the specified directory."""
    entries = []
    logs_path = Path(logs_dir)
    
    if not logs_path.exists():
        print(f"[WARN] Error logs directory not found: {logs_dir}")
        return entries
    
    for json_file in logs_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Handle both single entry and list of entries
                if isinstance(data, list):
                    for item in data:
                        entry = parse_error_entry(item)
                        if entry:
                            entries.append(entry)
                elif isinstance(data, dict):
                    entry = parse_error_entry(data)
                    if entry:
                        entries.append(entry)
                        
        except json.JSONDecodeError as e:
            print(f"[WARN] Failed to parse {json_file}: {e}")
        except Exception as e:
            print(f"[WARN] Error reading {json_file}: {e}")
    
    return entries


def parse_error_entry(data: dict) -> Optional[ErrorEntry]:
    """Parse a dictionary into an ErrorEntry."""
    try:
        return ErrorEntry(
            error_code=data.get("error_code", "UNKNOWN"),
            category=data.get("category", "unknown"),
            message=data.get("message", ""),
            root_cause=data.get("root_cause"),
            severity=data.get("severity"),
            timestamp=data.get("timestamp"),
            correlation_id=data.get("correlation_id"),
            fix=data.get("fix"),
            details=data.get("details"),
        )
    except Exception:
        return None


def cluster_errors(entries: list[ErrorEntry]) -> list[ErrorCluster]:
    """Cluster errors by category and error_code."""
    clusters_dict: dict[tuple[str, str], ErrorCluster] = {}
    
    for entry in entries:
        key = (entry.category, entry.error_code)
        
        if key not in clusters_dict:
            clusters_dict[key] = ErrorCluster(
                category=entry.category,
                error_code=entry.error_code,
                count=0,
            )
        
        cluster = clusters_dict[key]
        cluster.count += 1
        
        # Track sample messages (limit to 5)
        if entry.message and len(cluster.sample_messages) < 5:
            if entry.message not in cluster.sample_messages:
                cluster.sample_messages.append(entry.message)
        
        # Track root causes
        if entry.root_cause:
            cluster.root_causes[entry.root_cause] = cluster.root_causes.get(entry.root_cause, 0) + 1
        
        # Track severities
        if entry.severity:
            cluster.severities[entry.severity] = cluster.severities.get(entry.severity, 0) + 1
        
        # Track fix suggestions
        if entry.fix:
            cluster.fix_suggestions[entry.fix] = cluster.fix_suggestions.get(entry.fix, 0) + 1
    
    return list(clusters_dict.values())


def generate_candidate_rules(
    clusters: list[ErrorCluster],
    threshold: int = DEFAULT_THRESHOLD,
) -> list[dict]:
    """Generate candidate rules from clusters that exceed the threshold."""
    candidates = []
    
    for cluster in clusters:
        if cluster.count >= threshold:
            # Find most common root cause
            most_common_cause = None
            if cluster.root_causes:
                most_common_cause = max(cluster.root_causes.items(), key=lambda x: x[1])[0]
            
            # Find most common severity
            most_common_severity = None
            if cluster.severities:
                most_common_severity = max(cluster.severities.items(), key=lambda x: x[1])[0]
            
            # Find most common fix
            most_common_fix = None
            if cluster.fix_suggestions:
                most_common_fix = max(cluster.fix_suggestions.items(), key=lambda x: x[1])[0]
            
            candidate = {
                "rule_name": f"{cluster.category}_{cluster.error_code}",
                "trigger_condition": {
                    "category": cluster.category,
                    "error_code": cluster.error_code,
                },
                "occurrences": cluster.count,
                "root_cause": most_common_cause,
                "severity": most_common_severity,
                "suggested_fix": most_common_fix,
                "sample_messages": cluster.sample_messages[:3],
            }
            candidates.append(candidate)
    
    # Sort by occurrence count descending
    candidates.sort(key=lambda x: x["occurrences"], reverse=True)
    
    return candidates


def analyze_errors(
    logs_dir: str = DEFAULT_ERROR_LOGS_DIR,
    threshold: int = DEFAULT_THRESHOLD,
    verbose: bool = False,
) -> AnalysisResult:
    """Main analysis function."""
    print(f"[INFO] Loading error logs from: {logs_dir}")
    
    entries = load_error_logs(logs_dir)
    
    if not entries:
        print("[WARN] No error entries found")
        return AnalysisResult(
            total_errors=0,
            unique_categories=0,
            unique_error_codes=0,
            clusters=[],
            candidate_rules=[],
        )
    
    print(f"[INFO] Loaded {len(entries)} error entries")
    
    # Cluster errors
    clusters = cluster_errors(entries)
    print(f"[INFO] Found {len(clusters)} unique error clusters")
    
    # Get unique categories and error codes
    categories = set(e.category for e in entries)
    error_codes = set(e.error_code for e in entries)
    
    # Generate candidate rules
    candidates = generate_candidate_rules(clusters, threshold)
    print(f"[INFO] Generated {len(candidates)} candidate rules (threshold: {threshold})")
    
    if verbose:
        for candidate in candidates:
            print(f"  - {candidate['rule_name']}: {candidate['occurrences']} occurrences")
    
    return AnalysisResult(
        total_errors=len(entries),
        unique_categories=len(categories),
        unique_error_codes=len(error_codes),
        clusters=[asdict(c) for c in clusters],
        candidate_rules=candidates,
    )


def save_analysis_result(result: AnalysisResult, output_path: str) -> None:
    """Save analysis result to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2, ensure_ascii=False)
    
    print(f"[INFO] Analysis result saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze error logs and identify patterns for rule generation"
    )
    parser.add_argument(
        "--logs-dir",
        default=DEFAULT_ERROR_LOGS_DIR,
        help="Directory containing error log files",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help="Minimum occurrences to generate candidate rule",
    )
    parser.add_argument(
        "--output",
        help="Output file path for analysis result",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    result = analyze_errors(
        logs_dir=args.logs_dir,
        threshold=args.threshold,
        verbose=args.verbose,
    )
    
    if args.output:
        save_analysis_result(result, args.output)
    
    # Return exit code based on whether candidates were found
    if result.candidate_rules:
        print(f"\n[RESULT] Found {len(result.candidate_rules)} candidate rules")
        return 0
    else:
        print(f"\n[RESULT] No candidate rules found (threshold: {args.threshold})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
