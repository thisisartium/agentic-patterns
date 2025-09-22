# Multi‑Agent Patterns — Concise Reference

# 3  Orchestration Patterns

### 3.6  Market‑Based Coordination Pattern

### 3.7  Autonomous Collaboration Pattern
**Description**: Agents self‑select, call peers/tools, and decide call order at runtime without a central orchestrator.
**Category**: Orchestration · experimental · distributed · dynamic
**Need‑to‑know**:
- Team‑set guardrails: max fan‑out, max depth, per‑goal cost/time/tool caps.
- Use capability discovery + blackboard/shared memory for state.
- Loop detection and quorum for destructive actions.

