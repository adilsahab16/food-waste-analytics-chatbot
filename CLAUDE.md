# CLAUDE.md

## Working Style
# Note: these rules apply to this project. Once you start a second project,
# move these to ~/.claude/CLAUDE.md so they apply globally.

- Phase-gated development. Do not jump ahead.
- Do not generate code unless explicitly instructed.
- Ask questions rather than assume.
- When introducing concepts that are new (agent loops, MCP, API patterns), explain briefly before proceeding.
- Read existing files before modifying them.
- Never commit or push to Git without explicit approval. After making any meaningful change, always ask: "Can I go ahead and commit and push this to Git?"
- Never update CLAUDE_CONTEXT.md without explicit approval.

## Session Rhythm
- End of each session: remind user to commit, then run `/clear`
- Never run `/clear` mid-task — complete and commit first
- If a session runs 30–40 minutes without a commit, flag it

## Project Reference
Full project context — data model, SQL mappings, tool specs, phase plan, design decisions — is in CLAUDE_CONTEXT.md.
Read the relevant section before starting any task.

## Hard Rules (this project)
- `data/raw/` — never commit, gitignored
- `db/food_waste.db` — never commit, gitignored
- `.env` — never commit, gitignored
