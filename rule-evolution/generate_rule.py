#!/usr/bin/env python3
"""
Rule Evolution Pipeline - Rule Generation Module

Generates candidate rules from analysis results and stores in database.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import rule database
from rule_db import RuleDatabaseManager, DEFAULT_DB_PATH

# Configuration
DEFAULT_OUTPUT_DIR = "rules/candidates"

RULE_TEMPLATE = """# {rule_name}

## Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Status | candidate |
| Confidence Score | {confidence_score} |
| Impact Score | {impact_score} |
| False Positive Rate | {false_positive_rate}% |
| Created | {created_date} |
| Last Triggered | {last_triggered} |

---

## Trigger Condition

**Category**: `{category}`  
**Error Code**: `{error_code}`

{trigger_description}

---

## Root Cause

{root_cause}

---

## Mandatory Enforcement

{enforcement}

---

## Applies To

{applies_to}

---

## Verification Method

{verification}

---

## Sample Error Messages

{sample_messages}

---

## Related Errors

{related_errors}

---

## Notes

- Generated from {occurrences} error occurrences
- Threshold: {threshold} occurrences
- Review required before promoting to global rules
"""


@dataclass
class RuleGenerationInput:
    """Input for rule generation."""
    rule_name: str
    category: str
    error_code: str
    occurrences: int
    root_cause: Optional[str]
    severity: Optional[str]
    suggested_fix: Optional[str]
    sample_messages: list[str]
    threshold: int = 5


def generate_rule_content(input_data: RuleGenerationInput) -> str:
    """Generate rule content from input data."""
    
    trigger_description = (
        f"This rule triggers when an error with code `{input_data.error_code}` "
        f"occurs in the `{input_data.category}` category."
    )
    
    enforcement = generate_enforcement(input_data.category, input_data.suggested_fix)
    applies_to = generate_applies_to(input_data.category)
    verification = generate_verification(input_data.category)
    related_errors = generate_related_errors(input_data.category)
    
    confidence_score = min(1.0, input_data.occurrences / 10.0)
    impact_score = calculate_impact_score(input_data.severity)
    
    sample_messages = "\n".join(f"- {msg}" for msg in input_data.sample_messages[:3])
    if not sample_messages:
        sample_messages = "- (No sample messages available)"
    
    root_cause = input_data.root_cause or "(Root cause analysis pending)"
    
    return RULE_TEMPLATE.format(
        rule_name=input_data.rule_name,
        confidence_score=f"{confidence_score:.2f}",
        impact_score=impact_score,
        false_positive_rate="0",
        created_date=datetime.utcnow().strftime("%Y-%m-%d"),
        last_triggered="N/A",
        category=input_data.category,
        error_code=input_data.error_code,
        trigger_description=trigger_description,
        root_cause=root_cause,
        enforcement=enforcement,
        applies_to=applies_to,
        verification=verification,
        sample_messages=sample_messages,
        related_errors=related_errors,
        occurrences=input_data.occurrences,
        threshold=input_data.threshold,
    )


def generate_enforcement(category: str, fix: Optional[str]) -> str:
    """Generate enforcement section based on category."""
    
    base_enforcements = {
        "validation": "1. All input must be validated against defined schemas\n2. Use schema validation libraries\n3. Reject invalid input early",
        "authentication": "1. Log all auth attempts with correlation ID\n2. Implement account lockout\n3. Use secure password hashing",
        "authorization": "1. Check permissions before access\n2. Use RBAC\n3. Deny by default",
        "not_found": "1. Validate resource existence\n2. Use consistent ID patterns\n3. Implement caching",
        "conflict": "1. Implement optimistic locking\n2. Use idempotent operations\n3. Provide conflict resolution",
        "rate_limit": "1. Implement rate limiting\n2. Return proper 429 status\n3. Use token bucket algorithm",
        "dependency": "1. Implement circuit breaker\n2. Set appropriate timeouts\n3. Implement fallback strategies",
        "internal": "1. Never expose internal details\n2. Log full context internally\n3. Return generic message to users",
    }
    
    enforcement = base_enforcements.get(category, base_enforcements["internal"])
    if fix:
        enforcement += f"\n\n**Specific Fix**: {fix}"
    return enforcement


def generate_applies_to(category: str) -> str:
    applies = {
        "validation": "- All user input endpoints\n- API request payloads",
        "authentication": "- Login endpoints\n- Token refresh endpoints",
        "authorization": "- All resource access operations",
        "not_found": "- Database queries\n- External API calls",
        "conflict": "- Concurrent update operations",
        "rate_limit": "- All public API endpoints",
        "dependency": "- External API calls\n- Database connections",
        "internal": "- All application code paths",
    }
    return applies.get(category, applies["internal"])


def generate_verification(category: str) -> str:
    return "1. Unit tests\n2. Integration tests\n3. Chaos testing\n4. Error log monitoring"


def generate_related_errors(category: str) -> str:
    related = {
        "validation": "- TS-VAL-*, PY-VAL-* series",
        "authentication": "- TS-AUTH-*, PY-AUTH-* series",
        "authorization": "- TS-AUTHZ-*, PY-AUTHZ-* series",
        "not_found": "- TS-NOTF-*, PY-NOTF-* series",
        "conflict": "- TS-CONF-*, PY-CONF-* series",
        "rate_limit": "- TS-RATE-*, PY-RATE-* series",
        "dependency": "- TS-DEP-*, PY-DEP-* series",
        "internal": "- TS-INT-*, PY-INT-* series",
    }
    return related.get(category, related["internal"])


def calculate_impact_score(severity: Optional[str]) -> int:
    severity_scores = {"critical": 10, "high": 7, "medium": 5, "low": 3, "info": 1}
    return severity_scores.get(severity or "medium", 5)


def generate_rules_from_analysis(
    analysis_file: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    db_path: str = DEFAULT_DB_PATH,
    save_to_db: bool = True,
) -> list[str]:
    """Generate rule files from analysis result and optionally save to database."""
    
    with open(analysis_file, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    
    candidate_rules = analysis.get("candidate_rules", [])
    
    if not candidate_rules:
        print("[WARN] No candidate rules in analysis result")
        return []
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    db_manager = RuleDatabaseManager(db_path)
    
    generated_files = []
    updated_in_db = []
    
    for candidate in candidate_rules:
        input_data = RuleGenerationInput(
            rule_name=candidate["rule_name"],
            category=candidate["trigger_condition"]["category"],
            error_code=candidate["trigger_condition"]["error_code"],
            occurrences=candidate["occurrences"],
            root_cause=candidate.get("root_cause"),
            severity=candidate.get("severity"),
            suggested_fix=candidate.get("suggested_fix"),
            sample_messages=candidate.get("sample_messages", []),
            threshold=5,
        )
        
        content = generate_rule_content(input_data)
        
        rule_file = output_path / f"{input_data.rule_name}.md"
        with open(rule_file, "w", encoding="utf-8") as f:
            f.write(content)
        generated_files.append(str(rule_file))
        
        if save_to_db:
            rule_id = f"{input_data.category}_{input_data.error_code}"
            existing_rule = db_manager.get_rule(rule_id)
            
            if existing_rule:
                db_manager.update_rule(
                    rule_id=rule_id,
                    new_content=content,
                    changelog=f"Updated: {input_data.occurrences} occurrences",
                )
                updated_in_db.append(rule_id)
            else:
                db_manager.add_rule(
                    rule_id=rule_id,
                    rule_name=input_data.rule_name,
                    category=input_data.category,
                    error_code=input_data.error_code,
                    content=content,
                    status="candidate",
                    metadata={
                        "occurrences": input_data.occurrences,
                        "root_cause": input_data.root_cause,
                        "severity": input_data.severity,
                    },
                )
                updated_in_db.append(rule_id)
    
    if save_to_db:
        print(f"[INFO] Saved {len(updated_in_db)} rules to database: {db_path}")
    
    return generated_files


def main():
    parser = argparse.ArgumentParser(description="Generate candidate rules from analysis results")
    parser.add_argument("--input", "-i", required=True, help="Input analysis result JSON file")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"[ERROR] Input file not found: {args.input}")
        return 1
    
    generated = generate_rules_from_analysis(args.input, args.output_dir)
    
    if generated:
        print(f"\n[RESULT] Generated {len(generated)} rule files")
        return 0
    else:
        print("[RESULT] No rules generated")
        return 1


if __name__ == "__main__":
    sys.exit(main())
