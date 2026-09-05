---
name: data-converter
description: Transforms, parses, and validates structured data formats (JSON, CSV, YAML). Use when converting tabular data or validating data payloads.
version: "1.0.0"
tags: ["data", "json", "csv", "yaml", "converter"]
tools:
  - csv_to_json
  - json_to_csv
  - json_to_yaml
  - validate_json
---

# Data Converter Operating Procedure (SOP)

## Purpose
Facilitate lossless transformations between common serialized data formats (CSV, JSON, YAML) and validate syntax.

## Standard Workflow
1. When receiving CSV data that needs to be structured or turned into JSON, call `csv_to_json`.
2. When converting structured JSON list-of-objects to tabular CSV, call `json_to_csv`.
3. When transforming JSON configurations into YAML, call `json_to_yaml`.
4. When checking whether a JSON payload is well-formed, call `validate_json`.
5. Present transformed outputs inside appropriate code blocks (```json, ```csv, ```yaml).

## Constraints & Rules
- Always validate input strings before attempting conversions.
- If conversion encounters a syntax error, explain the error clearly to the user.
