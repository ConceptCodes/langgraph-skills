---
name: datetime-utility
description: Handles dates, times, durations, and calendar calculations. Use when calculating date differences, formatting timestamps, or adjusting dates by offsets.
version: "1.0.0"
tags: ["datetime", "calendar", "time", "timezone"]
tools:
  - get_current_time
  - calculate_date_difference
  - offset_date
---

# DateTime Utility Operating Procedure (SOP)

## Purpose
Perform deterministic date and time calculations, compute intervals between dates, and shift dates.

## Standard Workflow
1. When asked for current timestamp or current date in UTC or a specified timezone, call `get_current_time`.
2. When asked for duration/difference between two dates (e.g. days between 2026-01-01 and 2026-09-05), call `calculate_date_difference`.
3. When asked to add or subtract days/weeks/hours from a date, call `offset_date`.
4. Always state the timezone or ISO format in your response.

## Constraints & Rules
- Do NOT guess relative dates (e.g., "3 weeks from now") without using `get_current_time` or `offset_date`.
- Accepts standard ISO formats: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`.
