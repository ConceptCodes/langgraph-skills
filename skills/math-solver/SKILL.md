---
name: math-solver
description: Performs mathematical evaluations, algebraic calculations, and summary statistics. Use when numerical calculation or statistics are requested.
version: "1.0.0"
tags: ["math", "calculation", "statistics"]
tools:
  - calculate_expression
  - compute_statistics
---

# Math Solver Operating Procedure (SOP)

## Purpose
Execute precise mathematical computations and summary statistics on numeric datasets.

## Standard Workflow
1. For arithmetic, exponents, logarithms, and functions, use `calculate_expression`.
2. For datasets (mean, median, variance, min, max), use `compute_statistics`.
3. Provide step-by-step reasoning alongside the exact computed result.

## Constraints & Rules
- Do NOT perform complex multi-step arithmetic in LLM thought without executing `calculate_expression`.
- When computing statistics, pass all numbers as a numeric list.
