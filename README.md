# AI Engineering Governance System

> Unified error modeling and rule evolution across Python, Go, Rust, C++, and TypeScript

## 🎯 System Overview

A production-grade governance system that automatically evolves coding rules from error patterns across multiple programming languages. Features unified error modeling, automated rule generation, and persistent version tracking.

### Core Capabilities

- **Multi-language Error Modeling**: Consistent error handling across 5+ languages
- **Automated Rule Evolution**: Generate rules from error patterns using AI
- **Versioned Rule Database**: Complete history of rule changes with rollback
- **CI/CD Integration**: Automatic rule updates triggered by error log changes

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Error Logs    │───▶│   Rule Engine   │───▶│   Rule DB       │
│   (Multi-lang)  │    │   (AI-powered)  │    │   (Versioned)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Error Model   │    │   Validation    │    │   CI/CD         │
│   (5 Languages) │    │   Rules         │    │   Pipeline      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd opencode-ws

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python rule-evolution/cli.py db init
```

### Basic Usage

```bash
# Analyze error logs and generate rules
opencode-evolve analyze --logs-dir ./error-logs --threshold 5

# Generate new validation rules
opencode-evolve generate -i analysis-result.json

# List all rules
opencode-evolve db list

# Check rule status
opencode-evolve db status PY-VAL-001 global
```

## 📊 Error Modeling

### Supported Languages
- **Python**: `error-model/python/base_error.py`
- **Go**: `error-model/go/error.go`
- **Rust**: `error-model/rust/error.rs`
- **C++**: `error-model/cpp/error.hpp`
- **TypeScript**: `error-model/ts/error.ts`

### Unified Error Structure

```json
{
  "error_code": "PY-VAL-001",
  "category": "ValidationError",
  "message": "Input validation failed",
  "correlation_id": "uuid-1234",
  "details": {
    "field": "email",
    "value": "invalid-email",
    "rule": "email_format"
  }
}
```

### Error Categories
- `ValidationError` - Input validation failures
- `AuthenticationError` - Auth/permission issues
- `AuthorizationError` - Access control violations
- `NotFoundError` - Resource not found
- `ConflictError` - State conflicts
- `RateLimitError` - Rate limiting violations
- `DependencyError` - External service failures
- `InternalError` - Unhandled system errors

## 🔄 Rule Evolution Pipeline

### Process Flow

1. **Error Collection**: Gather structured error logs
2. **Pattern Analysis**: Identify recurring error patterns
3. **Rule Generation**: Create validation rules using AI
4. **Rule Review**: Human validation of generated rules
5. **Database Update**: Version-controlled rule storage
6. **CI/CD Deployment**: Automatic rule distribution

### Rule Structure

```json
{
  "rule_id": "validation_PY-VAL-001",
  "rule_name": "Email Format Validation",
  "category": "validation",
  "error_code": "PY-VAL-001",
  "status": "global",
  "condition": "email matches regex",
  "message": "Invalid email format",
  "severity": "error",
  "languages": ["python", "typescript"],
  "version": "1.0.0",
  "last_updated": "2026-02-28T02:00:00Z"
}
```

## 🗄️ Database Schema

### Rule Database (`rules/rule_database.json`)

```json
{
  "rules": {
    "validation_PY-VAL-001": {
      "rule_id": "validation_PY-VAL-001",
      "current_version": "1.0.0",
      "versions": [
        {
          "version": "1.0.0",
          "rule": {...},
          "metadata": {
            "generated_by": "ai",
            "confidence": 0.95,
            "review_status": "approved"
          }
        }
      ]
    }
  },
  "metadata": {
    "last_updated": "2026-02-28T02:00:00Z",
    "total_rules": 42,
    "active_rules": 38
  }
}
```

### Database Operations

```python
# Initialize database
RuleDatabase.initialize()

# Add new rule
rule = Rule.from_dict(rule_data)
db.add_rule(rule)

# Get rule history
history = db.get_rule_history("validation_PY-VAL-001")

# Rollback to previous version
db.rollback_rule("validation_PY-VAL-001", "1.0.0")
```

## 🛠️ CLI Reference

### Global Commands

```bash
# Initialize system
opencode-evolve init

# Analyze error logs
opencode-evolve analyze --logs-dir <path> --threshold <count>

# Generate rules from analysis
opencode-evolve generate --input <file> --output <file>
```

### Database Commands

```bash
# List all rules
opencode-evolve db list [--category validation]

# Show rule details
opencode-evolve db show <rule_id>

# Check rule status
opencode-evolve db status <rule_id> [global|candidate|deprecated]

# Update rule status
opencode-evolve db promote <rule_id>
opencode-evolve db deprecate <rule_id>
```

### Validation Commands

```bash
# Validate code against rules
opencode-evolve validate --path <file_or_dir> --rules <rules_file>

# Run CI checks
opencode-evolve ci check --branch <branch_name>
```

## 🔧 Configuration

### Environment Variables

```bash
# Database configuration
RULE_DB_PATH=./rules/rule_database.json
RULE_BACKUP_DIR=./rules/backups

# Analysis thresholds
ERROR_THRESHOLD=5
PATTERN_CONFIDENCE=0.8

# CI/CD settings
GITHUB_TOKEN=<your_token>
REVIEW_REQUIRED=true
```

### Configuration File (`rule-evolution/config.yaml`)

```yaml
analysis:
  threshold: 5
  confidence: 0.8
  languages: ["python", "typescript", "go"]

database:
  path: ./rules/rule_database.json
  backup_dir: ./rules/backups
  max_versions: 10

validation:
  strict_mode: true
  auto_fix: false
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest tests/

# Test specific module
pytest tests/test_rule_generation.py

# Test with coverage
pytest --cov=rule_evolution tests/
```

### Integration Tests

```bash
# Test CLI commands
./tests/test_cli.sh

# Test CI/CD workflow
./tests/test_ci.sh
```

## 🚀 CI/CD Integration

### GitHub Actions Workflow

The system automatically triggers on:
- Push to main branch
- Pull request creation
- Error log file changes

```yaml
# .github/workflows/rule-evolution.yml
name: Rule Evolution Pipeline
on:
  push:
    paths:
      - 'error-logs/**'
      - 'rules/**'
  pull_request:
    branches: [main]
```

### Manual CI Trigger

```bash
# Trigger rule evolution manually
gh workflow run rule-evolution.yml --ref main
```

## 📈 Monitoring & Observability

### Metrics Collection

- **Rule Generation Rate**: Rules generated per error pattern
- **Validation Success Rate**: % of code passing rule validation
- **False Positive Rate**: Incorrect rule applications
- **Rule Adoption Rate**: Global vs candidate rules over time

### Logging

Structured logs include:
- Request correlation IDs
- Rule generation metadata
- Error pattern analysis results
- Database operation traces

```json
{
  "timestamp": "2026-02-28T02:00:00Z",
  "level": "info",
  "service": "rule-evolution",
  "correlation_id": "req-1234",
  "message": "Generated rule validation_PY-VAL-001",
  "metadata": {
    "error_count": 15,
    "confidence": 0.95,
    "languages": ["python", "typescript"]
  }
}
```

## 🛡️ Security

### Security Model
- **Least Privilege**: Minimal permissions for rule generation
- **Input Validation**: All error logs sanitized before processing
- **Secret Management**: No hard-coded credentials
- **Audit Trail**: Complete rule change history

### Threat Mitigation
- **SQL Injection**: Parameterized queries only
- **XSS Prevention**: HTML escaping for rule descriptions
- **Access Control**: Role-based rule promotion workflow
- **Data Integrity**: Cryptographic checksums for rule versions

## 🔍 Troubleshooting

### Common Issues

**Q: CLI commands not found**
```bash
# Ensure package is installed
pip install -e .

# Check PATH
which opencode-evolve
```

**Q: Database initialization fails**
```bash
# Check file permissions
ls -la rules/rule_database.json

# Reinitialize database
rm rules/rule_database.json
python rule-evolution/cli.py db init
```

**Q: Rule generation produces false positives**
```bash
# Increase confidence threshold
opencode-evolve analyze --confidence 0.9

# Review generated rules manually
opencode-evolve db list --status candidate
```

### Debug Mode

```bash
# Enable verbose logging
export LOG_LEVEL=debug
opencode-evolve --verbose analyze --logs-dir ./error-logs
```

## 📚 Examples

### Example 1: Email Validation Rule

```bash
# 1. Create sample error logs
echo 'ERROR: Invalid email format: "invalid-email"' > error-logs/email_errors.log

# 2. Analyze patterns
opencode-evolve analyze --logs-dir error-logs --threshold 3

# 3. Generate rule
opencode-evolve generate -i analysis_results.json

# 4. Review and promote
opencode-evolve db show validation_PY-VAL-001
opencode-evolve db promote validation_PY-VAL-001
```

### Example 2: Multi-language Setup

```bash
# Configure for Python + TypeScript
echo 'languages: ["python", "typescript"]' > config.yaml

# Run validation
opencode-evolve validate --path ./src --rules ./rules/global/
```

## 🤝 Contributing

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd opencode-ws
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black rule_evolution/
isort rule_evolution/
```

### Contribution Guidelines

1. **Rule Generation**: Follow the structured error model
2. **Testing**: Add tests for new rule types
3. **Documentation**: Update README for new features
4. **Security**: Maintain the security-first approach

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/opencode-ws/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/opencode-ws/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/opencode-ws/wiki)

---

**Built with ❤️ for engineering teams who care about code quality and security.**