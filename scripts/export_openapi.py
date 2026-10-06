"""Export/check designed OpenAPI, actual served-route schema and JSON examples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fastapi.openapi.models import OpenAPI
from jsonschema import Draft202012Validator, FormatChecker

from rag_core.api.app import create_app
from rag_core.api.health import HealthChecks
from rag_core.contracts.examples import EXAMPLE_MODELS, build_examples
from rag_core.contracts.openapi import ENDPOINTS, build_designed_openapi

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "api"


def validate_references(document: dict[str, Any]) -> None:
    """Check every local schema reference without another dependency."""

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            reference = value.get("$ref")
            if reference is not None:
                if not reference.startswith("#/"):
                    raise ValueError("Only local schema references are allowed")
                resolved: Any = document
                for part in reference[2:].split("/"):
                    resolved = resolved[part.replace("~1", "/").replace("~0", "~")]
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(document)


def validate_schema_snapshot(document: dict[str, Any]) -> int:
    OpenAPI.model_validate(document)
    validate_references(document)
    schemas = document.get("components", {}).get("schemas", {})
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    return len(schemas)


def validate_examples(examples: dict[str, Any], document: dict[str, Any]) -> int:
    records = examples["examples"]
    for record in records:
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": f"#/components/schemas/{record['schema']}",
            "components": document["components"],
        }
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(record["value"])
        model = EXAMPLE_MODELS[record["schema"]]
        validated = model.model_validate_json(json.dumps(record["value"], ensure_ascii=False))
        # In particular, Default request serialization must omit document_ids=None.
        model.model_validate_json(validated.model_dump_json())
    return len(records)


def build_artifacts() -> dict[str, dict[str, Any]]:
    # No settings/secrets/probes are loaded; health dependencies are not executed.
    served = create_app(checks=HealthChecks(checks={})).openapi()
    served["info"]["description"] = (
        "Actual application OpenAPI: health and authenticated public v1 routes are mounted. "
        "This export inspects the factory; it does not run a readiness probe."
    )
    designed = build_designed_openapi()
    expected = {endpoint.path for endpoint in ENDPOINTS if endpoint.served}
    if set(served["paths"]) != expected:
        raise ValueError("Served routes have drifted from the v1 inventory")
    examples = build_examples()
    for document in (served, designed):
        validate_schema_snapshot(document)
    validate_examples(examples, designed)
    return {
        "openapi-v1.designed.json": designed,
        "openapi.served.json": served,
        "examples-v1.json": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Validate existing snapshots, no writes"
    )
    args = parser.parse_args()
    artifacts = build_artifacts()
    if not args.check:
        OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        path = OUTPUT / name
        rendered = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.check:
            if path.read_text(encoding="utf-8") != rendered:
                raise ValueError(f"Snapshot drift: {path.relative_to(ROOT)}; rerun export")
        else:
            path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"PASS {'checked' if args.check else 'exported'} {path.relative_to(ROOT).as_posix()}")
    operations = sum(len(item) for item in artifacts["openapi-v1.designed.json"]["paths"].values())
    count = validate_examples(artifacts["examples-v1.json"], artifacts["openapi-v1.designed.json"])
    schemas = validate_schema_snapshot(artifacts["openapi-v1.designed.json"])
    print(
        f"PASS designed_operations={operations} served_operations=13 served_health_routes=2 synthetic_examples={count}"
    )
    print(f"PASS OpenAPI model + Draft2020-12 schemas={schemas}; examples JSON Schema + Pydantic")
    print("CONTRACT EXPORT: PASS (public routes mounted; export does not verify runtime/provider)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
