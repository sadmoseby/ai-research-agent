#!/usr/bin/env python3
"""
Standalone validation script for research proposals.
This script validates a proposal JSON file against the schema and provides detailed error reporting.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
from jsonschema import Draft202012Validator


def load_schema() -> Dict[str, Any]:
    """Load the JSON schema from the schema directory."""
    schema_path = Path(__file__).parent.parent / "schema/lean-research-schema.jsonc"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # Load JSONC (JSON with comments) by removing comments
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Better comment removal that preserves strings
    lines = []
    in_string = False
    for line in content.split("\n"):
        cleaned_line = ""
        i = 0
        while i < len(line):
            char = line[i]
            if char == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
                cleaned_line += char
            elif not in_string and char == "/" and i + 1 < len(line) and line[i + 1] == "/":
                # Found comment start, ignore rest of line
                break
            else:
                cleaned_line += char
            i += 1
        lines.append(cleaned_line.rstrip())

    clean_content = "\n".join(lines)

    try:
        return json.loads(clean_content)
    except json.JSONDecodeError as e:
        print("Schema content preview around error:")
        lines = clean_content.split("\n")
        error_line = e.lineno - 1 if e.lineno else 0
        start_line = max(0, error_line - 2)
        end_line = min(len(lines), error_line + 3)
        for i in range(start_line, end_line):
            marker = " >>> " if i == error_line else "     "
            print(f"{marker}{i+1:3d}: {lines[i]}")
        raise ValueError(f"Failed to parse schema JSON: {e}") from e


def load_proposal(file_path: str) -> Dict[str, Any]:
    """Load a proposal JSON file."""
    proposal_path = Path(file_path)

    if not proposal_path.exists():
        raise FileNotFoundError(f"Proposal file not found: {proposal_path}")

    with open(proposal_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_proposal(proposal: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate proposal against schema and return list of errors."""
    errors = []

    try:
        # First, validate the schema itself
        Draft202012Validator.check_schema(schema)
        print("✅ Schema is valid")
    except jsonschema.SchemaError as e:
        print(f"❌ Schema validation failed: {e}")
        return [f"Invalid schema: {e}"]

    try:
        # Validate the proposal against the schema
        validator = Draft202012Validator(schema)
        validation_errors = list(validator.iter_errors(proposal))

        if not validation_errors:
            print("✅ Proposal is valid!")
            return []

        # Collect detailed error information
        for error in validation_errors:
            path = ".".join(str(p) for p in error.absolute_path)
            if not path:
                path = "root"

            error_msg = f"At {path}: {error.message}"
            errors.append(error_msg)

        return errors

    except Exception as e:
        return [f"Validation error: {e}"]


def analyze_alpha_only_mode(proposal: Dict[str, Any]) -> List[str]:
    """Analyze alpha-only mode specific requirements."""
    issues = []

    if not proposal.get("alpha-only"):
        return ["Proposal is not in alpha-only mode"]

    # Check allowed fields in alpha-only mode
    allowed_fields = {"alphas", "universe", "alpha-only"}
    actual_fields = set(proposal.keys())

    extra_fields = actual_fields - allowed_fields
    if extra_fields:
        issues.append(f"Extra fields not allowed in alpha-only mode: {', '.join(extra_fields)}")

    # Check alphas structure
    alphas = proposal.get("alphas", {})
    if not isinstance(alphas, dict):
        issues.append("'alphas' must be an object")
    else:
        # In alpha-only mode, exactly one alpha (new or amend)
        new_alphas = alphas.get("new", [])
        amend_alphas = alphas.get("amend", [])
        existing_alphas = alphas.get("existing", [])

        total_alphas = len(new_alphas) + len(amend_alphas)

        if total_alphas != 1:
            issues.append(f"Alpha-only mode requires exactly 1 alpha (new or amend), found {total_alphas}")

        if existing_alphas:
            issues.append("Alpha-only mode cannot have existing alphas")

    # Check universe structure
    universe = proposal.get("universe", {})
    if not isinstance(universe, dict):
        issues.append("'universe' must be an object")
    else:
        existing_universes = universe.get("existing", [])
        if len(existing_universes) != 1:
            issues.append(f"Alpha-only mode requires exactly 1 existing universe, found {len(existing_universes)}")

    return issues


def main():
    """Main validation function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_proposal.py <proposal_file.json>")
        print("Example: python validate_proposal.py proposals/test_strategy.json")
        sys.exit(1)

    proposal_file = sys.argv[1]

    print(f"🔍 Validating proposal: {proposal_file}")
    print("=" * 60)

    try:
        # Load schema and proposal
        print("📋 Loading schema...")
        schema = load_schema()

        print("📄 Loading proposal...")
        proposal = load_proposal(proposal_file)

        # Basic info about the proposal
        print("📊 Proposal info:")
        print(f"   - Alpha-only mode: {proposal.get('alpha-only', False)}")
        print(f"   - Top-level fields: {', '.join(proposal.keys())}")

        if proposal.get("alpha-only"):
            alphas = proposal.get("alphas", {})
            alpha_summary = (
                f"{len(alphas.get('new', []))} new, "
                f"{len(alphas.get('amend', []))} amend, "
                f"{len(alphas.get('existing', []))} existing"
            )
            print(f"   - Alphas: {alpha_summary}")

            universe = proposal.get("universe", {})
            print(f"   - Universe: {len(universe.get('existing', []))} existing")

        print()

        # Validate against schema
        print("🔍 Validating against schema...")
        schema_errors = validate_proposal(proposal, schema)

        if schema_errors:
            print(f"❌ Found {len(schema_errors)} schema validation errors:")
            for i, error in enumerate(schema_errors, 1):
                print(f"   {i}. {error}")

        print()

        # Alpha-only mode analysis
        if proposal.get("alpha-only"):
            print("🎯 Analyzing alpha-only mode requirements...")
            alpha_only_issues = analyze_alpha_only_mode(proposal)

            if alpha_only_issues:
                print(f"❌ Found {len(alpha_only_issues)} alpha-only mode issues:")
                for i, issue in enumerate(alpha_only_issues, 1):
                    print(f"   {i}. {issue}")
            else:
                print("✅ Alpha-only mode requirements satisfied")

        print()

        # Summary
        total_issues = len(schema_errors) + (
            len(analyze_alpha_only_mode(proposal)) if proposal.get("alpha-only") else 0
        )

        if total_issues == 0:
            print("🎉 Proposal is fully valid!")
        else:
            print(f"📋 Summary: {total_issues} total issues found")
            print("💡 Fix these issues to make the proposal valid")

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
