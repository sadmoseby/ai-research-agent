"""
MCP validation tool for schema validation and repair.
"""

import json
from typing import Any, Dict, List, Optional

import jsonschema

from ..config import Config, get_logger
from ..prompts import ResearchPrompts

# Get logger for this tool
logger = get_logger("tools.validation_mcp")


class ValidationMCPTool:
    """MCP tool for validation functionality."""

    def __init__(self, config: Config):
        self.config = config

    def validate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a proposal against the schema.

        Args:
            proposal: The proposal JSON to validate

        Returns:
            Dict containing validation results with keys:
            - is_valid: bool
            - errors: List[str] (validation errors if any)
            - report: str (validation report message)
        """
        logger.info("Validating proposal against schema")

        if not proposal:
            return {
                "is_valid": False,
                "errors": [ResearchPrompts.VALIDATION_NO_PROPOSAL_ERROR],
                "report": ResearchPrompts.VALIDATION_NO_PROPOSAL_REPORT,
            }

        try:
            # Load schema
            schema = self.config.get_schema()

            # Validate against schema
            jsonschema.validate(proposal, schema)

            # Validation passed
            logger.info("Proposal validation successful")
            return {
                "is_valid": True,
                "errors": [],
                "report": ResearchPrompts.VALIDATION_SUCCESS_REPORT,
            }

        except jsonschema.ValidationError as e:
            # Collect validation errors using prompts
            logger.info("Proposal validation failed with errors")

            errors = [
                ResearchPrompts.VALIDATION_ERROR_TEMPLATE.format(
                    path=".".join(str(p) for p in e.absolute_path), message=e.message
                )
            ]

            # Try to collect additional errors
            try:
                validator = jsonschema.Draft202012Validator(schema)
                all_errors = list(validator.iter_errors(proposal))
                errors = [
                    ResearchPrompts.VALIDATION_PATH_ERROR_TEMPLATE.format(
                        path=".".join(str(p) for p in err.absolute_path),
                        message=err.message,
                    )
                    for err in all_errors[:5]
                ]  # Limit to 5 errors
            except (AttributeError, TypeError):
                pass  # Use the single error from above

            return {
                "is_valid": False,
                "errors": errors,
                "report": ResearchPrompts.VALIDATION_FAILED_REPAIR_REPORT.format(count=len(errors)),
            }

        except (ValueError, KeyError) as e:
            error_msg = ResearchPrompts.VALIDATION_SYSTEM_ERROR_TEMPLATE.format(error=str(e))
            logger.error("System error during validation: %s", str(e))
            return {
                "is_valid": False,
                "errors": [error_msg],
                "report": f"❌ {error_msg}",
            }

    async def repair_proposal(
        self,
        proposal: Dict[str, Any],
        validation_errors: List[str],
        llm_client: Any,
        idea: str,
        alpha_only: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt to repair a proposal using the LLM.

        Args:
            proposal: The invalid proposal
            validation_errors: List of validation errors
            llm_client: LLM client instance for repair
            idea: Original research idea
            alpha_only: Whether this is an alpha-only proposal

        Returns:
            Dict containing the repaired proposal or None if repair failed
        """
        logger.info("Attempting to repair proposal with %d validation errors", len(validation_errors))

        # Format errors for the LLM
        errors_formatted = "\n".join([f"- {error}" for error in validation_errors])

        # Get schema for reference
        schema = self.config.get_schema()
        schema_str = str(schema)

        # Create repair prompt
        alpha_mode_note = ResearchPrompts.get_alpha_mode_note(alpha_only)

        system_prompt = f"""You are a JSON schema validation repair specialist.
Your job is to fix JSON proposals that fail schema validation.

{alpha_mode_note}

VALIDATION ERRORS TO FIX:
{errors_formatted}

SCHEMA REFERENCE:
{schema_str}

Instructions:
1. Fix ONLY the validation errors listed above
2. Keep all other content unchanged where possible
3. Ensure the output is valid JSON that conforms to the schema
4. Do not add explanations - return only the fixed JSON
5. Maintain the original research intent and content
"""

        user_prompt = f"""Original idea: {idea}

Invalid JSON proposal that needs repair:
{json.dumps(proposal, indent=2)}

Please fix the validation errors and return the corrected JSON proposal."""

        try:
            # Use structured output to get repaired proposal
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

            response = await llm_client.structured_completion(
                messages=messages,
                schema=schema,
                temperature=0.1,  # Low temperature for repair consistency
            )

            if isinstance(response, dict):
                logger.info("Proposal repair completed successfully")
                return response
            else:
                logger.warning("Repair attempt returned non-dict response")
                return None

        except (jsonschema.ValidationError, ValueError, TypeError, KeyError) as e:
            logger.error("Proposal repair failed: %s", str(e))
            return None
