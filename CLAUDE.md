# SampleApp - Implementation Context

## Project Context (Read-Only)

All project-specific information (business goals, stack decisions, constraints) is live in `PROJECT_CONTEXT.md` (read-only).
Read it before starting any task.

Rules:

- Always read this file before starting any task
- Treat it as read-only
- Do not restate its contents unless necessary
- If it conflicts with other instructions, PROJECT_CONTEXT.md wins

## Rules for Claude

- Strictly follow DRY principle
- Always use async/await in Python backend
- Use SQLAlchemy 2.0 style (not legacy 1.x)
- Use Pydantic v2 for schemas
- Frontend uses App Router (not Pages Router)
- Use server components where possible in Next.js
- Keep MVP simple - no over-engineering
- Add API endpoints into ./docs/API/\*.rest (REST Client VSCode extension)
- Don't restart container unnecessarily. Use 'docker compose down' command only on extreme condition or when suggested to do so.

## Execution Contract for Claude

When responding:

- Start with a brief plan (3–6 bullet points max)
- Ask clarification ONLY if required to proceed
- Modify the smallest possible surface area
- Prefer editing existing files over creating new ones
- Do not refactor unrelated code
- Stop when the task is complete
- Assume PROJECT_CONTEXT.md is already loaded
- Do not ask questions answered there

## Output Rules

- Do NOT explain obvious framework concepts
- Do NOT restate requirements
- Show code first, explanations after
- Use diffs or full-file replacements explicitly
- If multiple files are changed, list them first

## Scope Guardrails

Forbidden unless explicitly requested:

- New libraries or frameworks
- Architectural rewrites
- Background workers beyond Celery
- Frontend state managers beyond React Query/SWR
- Design system changes
- Do NOT scan the entire repository
- Only read files explicitly mentioned or directly relevant

If a better approach exists, mention it briefly without implementing.

## Task Awareness

- Assume CURRENT_TASK.md defines the active work
- Ignore unfinished TODOs unless referenced
- If CURRENT_TASK.md is missing, ask before proceeding
- TODO.md: ONLY append new items or check completed items
- Existing text must never be modified or reordered

## Testing Expectations

- Backend: pytest, async tests preferred
- Use SQLite for tests if possible
- Clean up test DB after run
- Frontend: basic component + API mocking tests only
- Do not add E2E unless requested
- Tests must use SQLite
- Test database must be deleted after test run

## Uncertainty Rule

If requirements are unclear:

- Ask a single clarifying question
- Do NOT assume or invent behavior

## Session Resume Template

On startup:

1. Summarize CURRENT_TASK.md in 5 lines
2. Ask: "Resume this task? (yes/no)"
3. If no → wait for new instructions

## Verbosity

Default to concise.
Elaborate only when asked or when ambiguity exists.

## File Ownership

Read-only (never modify):

- ARCHITECTURE.md
- PROJECT_CONTEXT.md

May update:

- CURRENT_TASK.md
- TODO.md (append only)
- HISTORY.md
- CHANGELOG.md

Create/update when needed:

- README.md
- docs/API/\*.rest
