#!/usr/bin/env python3
"""
Rule Database - Persistent storage for rule evolution history

Uses JSON file as database for version control friendliness.
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# Configuration
DEFAULT_DB_PATH = "rules/rule_database.json"
DEFAULT_BACKUP_DIR = "rules/backups"


@dataclass
class RuleVersion:
    """Represents a single version of a rule."""
    version: str
    content: str
    created_at: str
    created_by: str = "auto"
    changelog: str = ""
    confidence_score: float = 0.0
    impact_score: int = 5
    false_positive_rate: float = 0.0


@dataclass
class Rule:
    """Represents a rule with full history."""
    rule_id: str
    rule_name: str
    category: str
    error_code: str
    status: str  # candidate, global, deprecated, stale
    current_version: str
    created_at: str
    updated_at: str
    last_triggered: Optional[str] = None
    versions: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class RuleDatabase:
    """Database for storing rules and their history."""
    version: str = "1.0.0"
    rules: dict[str, dict] = field(default_factory=dict)
    statistics: dict = field(default_factory=lambda: {
        "total_rules": 0,
        "candidate_rules": 0,
        "global_rules": 0,
        "deprecated_rules": 0,
        "stale_rules": 0,
    })
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class RuleDatabaseManager:
    """Manager for rule database operations."""
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db: Optional[RuleDatabase] = None
        self._load()
    
    def _load(self) -> None:
        """Load database from file."""
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.db = RuleDatabase(
                    version=data.get("version", "1.0.0"),
                    rules=data.get("rules", {}),
                    statistics=data.get("statistics", {}),
                    updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
                )
        else:
            self.db = RuleDatabase()
    
    def _save(self) -> None:
        """Save database to file."""
        # Create backup before saving
        if self.db_path.exists():
            self._create_backup()
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update timestamp
        self.db.updated_at = datetime.utcnow().isoformat()
        
        # Save
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.db), f, indent=2, ensure_ascii=False)
    
    def _create_backup(self) -> str:
        """Create a backup of the current database."""
        backup_dir = Path(DEFAULT_BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"rule_database_{timestamp}.json"
        
        shutil.copy2(self.db_path, backup_path)
        
        # Keep only last 10 backups
        backups = sorted(backup_dir.glob("rule_database_*.json"))
        for old_backup in backups[:-10]:
            old_backup.unlink()
        
        return str(backup_path)
    
    def _update_statistics(self) -> None:
        """Update database statistics."""
        stats = {
            "total_rules": len(self.db.rules),
            "candidate_rules": 0,
            "global_rules": 0,
            "deprecated_rules": 0,
            "stale_rules": 0,
        }
        
        for rule in self.db.rules.values():
            status = rule.get("status", "candidate")
            if status == "candidate":
                stats["candidate_rules"] += 1
            elif status == "global":
                stats["global_rules"] += 1
            elif status == "deprecated":
                stats["deprecated_rules"] += 1
            elif status == "stale":
                stats["stale_rules"] += 1
        
        self.db.statistics = stats
    
    # === CRUD Operations ===
    
    def add_rule(
        self,
        rule_id: str,
        rule_name: str,
        category: str,
        error_code: str,
        content: str,
        status: str = "candidate",
        created_by: str = "auto",
        metadata: Optional[dict] = None,
    ) -> Rule:
        """Add a new rule to the database."""
        now = datetime.utcnow().isoformat()
        
        # Create first version
        first_version = RuleVersion(
            version="1.0.0",
            content=content,
            created_at=now,
            created_by=created_by,
            changelog="Initial version",
        )
        
        rule = {
            "rule_id": rule_id,
            "rule_name": rule_name,
            "category": category,
            "error_code": error_code,
            "status": status,
            "current_version": "1.0.0",
            "created_at": now,
            "updated_at": now,
            "last_triggered": None,
            "versions": [asdict(first_version)],
            "metadata": metadata or {},
        }
        
        self.db.rules[rule_id] = rule
        self._update_statistics()
        self._save()
        
        return Rule(**rule)
    
    def update_rule(
        self,
        rule_id: str,
        new_content: str,
        changelog: str = "",
        updated_by: str = "auto",
    ) -> Optional[Rule]:
        """Update an existing rule, creating a new version."""
        if rule_id not in self.db.rules:
            return None
        
        rule = self.db.rules[rule_id]
        
        # Parse current version
        current_ver = rule["current_version"]
        ver_parts = current_ver.split(".")
        new_ver = f"{ver_parts[0]}.{int(ver_parts[1]) + 1}.0"
        
        now = datetime.utcnow().isoformat()
        
        # Create new version
        new_version = RuleVersion(
            version=new_ver,
            content=new_content,
            created_at=now,
            created_by=updated_by,
            changelog=changelog,
        )
        
        # Update rule
        rule["current_version"] = new_ver
        rule["updated_at"] = now
        rule["versions"].append(asdict(new_version))
        
        self._update_statistics()
        self._save()
        
        return Rule(**rule)
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        if rule_id not in self.db.rules:
            return None
        return Rule(**self.db.rules[rule_id])
    
    def get_rule_version(self, rule_id: str, version: str) -> Optional[RuleVersion]:
        """Get a specific version of a rule."""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        for v in rule.versions:
            if v["version"] == version:
                return RuleVersion(**v)
        return None
    
    def list_rules(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[Rule]:
        """List rules with optional filters."""
        rules = []
        
        for rule_dict in self.db.rules.values():
            if status and rule_dict.get("status") != status:
                continue
            if category and rule_dict.get("category") != category:
                continue
            rules.append(Rule(**rule_dict))
        
        return sorted(rules, key=lambda r: r.updated_at, reverse=True)
    
    def change_status(
        self,
        rule_id: str,
        new_status: str,
        changelog: str = "",
    ) -> Optional[Rule]:
        """Change the status of a rule."""
        if rule_id not in self.db.rules:
            return None
        
        valid_statuses = ["candidate", "global", "deprecated", "stale"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.db.rules[rule_id]["status"] = new_status
        self.db.rules[rule_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Add version entry for status change
        version_entry = {
            "version": self.db.rules[rule_id]["current_version"],
            "content": "",
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "system",
            "changelog": f"Status changed to {new_status}: {changelog}",
        }
        self.db.rules[rule_id]["versions"].append(version_entry)
        
        self._update_statistics()
        self._save()
        
        return Rule(**self.db.rules[rule_id])
    
    def rollback(self, rule_id: str, target_version: str) -> Optional[Rule]:
        """Rollback a rule to a previous version."""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        # Find target version
        target = None
        for v in rule.versions:
            if v["version"] == target_version:
                target = v
                break
        
        if not target:
            return None
        
        # Create new version with rolled back content
        now = datetime.utcnow().isoformat()
        current_ver = rule.current_version
        ver_parts = current_ver.split(".")
        new_ver = f"{ver_parts[0]}.{int(ver_parts[1]) + 1}.0"
        
        rollback_version = {
            "version": new_ver,
            "content": target["content"],
            "created_at": now,
            "created_by": "system",
            "changelog": f"Rollback to version {target_version}",
        }
        
        self.db.rules[rule_id]["current_version"] = new_ver
        self.db.rules[rule_id]["updated_at"] = now
        self.db.rules[rule_id]["versions"].append(rollback_version)
        
        self._save()
        
        return Rule(**self.db.rules[rule_id])
    
    def get_history(self, rule_id: str) -> Optional[list[dict]]:
        """Get full version history of a rule."""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        return rule.versions
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule (soft delete - moves to deprecated)."""
        return self.change_status(rule_id, "deprecated", "Deleted") is not None
    
    def get_statistics(self) -> dict:
        """Get database statistics."""
        return self.db.statistics
    
    def export_rule(self, rule_id: str, format: str = "markdown") -> Optional[str]:
        """Export a rule in specified format."""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        # Get current version content
        current_version = None
        for v in rule.versions:
            if v["version"] == rule.current_version:
                current_version = v
                break
        
        if not current_version:
            return None
        
        if format == "markdown":
            return current_version["content"]
        elif format == "json":
            return json.dumps(rule, indent=2, default=str)
        
        return None


def init_database(db_path: str = DEFAULT_DB_PATH) -> RuleDatabaseManager:
    """Initialize a new rule database."""
    manager = RuleDatabaseManager(db_path)
    manager._save()
    return manager


# CLI helpers
def print_rule(rule: Rule) -> None:
    """Print rule information."""
    print(f"\n{'='*60}")
    print(f"Rule: {rule.rule_name}")
    print(f"ID: {rule.rule_id}")
    print(f"Category: {rule.category}")
    print(f"Error Code: {rule.error_code}")
    print(f"Status: {rule.status}")
    print(f"Version: {rule.current_version}")
    print(f"Created: {rule.created_at}")
    print(f"Updated: {rule.updated_at}")
    print(f"Last Triggered: {rule.last_triggered or 'N/A'}")
    print(f"{'='*60}")


def print_history(rule_id: str, versions: list[dict]) -> None:
    """Print version history."""
    print(f"\nHistory for {rule_id}:")
    print("-" * 60)
    for i, v in enumerate(reversed(versions), 1):
        print(f"  v{v['version']} | {v['created_at'][:19]} | {v['created_by']}")
        if v.get('changelog'):
            print(f"         | {v['changelog']}")
