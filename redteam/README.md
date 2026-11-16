# ARIA Promptfoo red team

Tests the real `create_aria_agent` / `invoke_agent` implementation, its system prompt,
LangChain tool loop and fictional seed data. The Streamlit server need not run.
All files for this setup are in this directory; application code is unchanged.

## Setup and run

From the repository root, activate the application's environment and install its
requirements if needed. Node.js and npm are also required.

```bash
source .venv/bin/activate  # use venv/bin/activate if that is your environment
python -m pip install -r requirements.txt
export PROMPTFOO_PYTHON="$(command -v python)"
cd redteam
npm ci
export PROMPTFOO_CONFIG_DIR="$PWD/.promptfoo"
export PROMPTFOO_DISABLE_TELEMETRY=1
export OPENAI_API_KEY='your-key-here'
```

Use an environment/secret manager for the key; do not commit it. The sidebar key
in Streamlit is not available to this separate process. Target calls, generation
and model grading incur API charges. Generation/attack strategies may also use
Promptfoo's remote services and require `npx promptfoo auth login`; `sharing: false`
disables result sharing, not remote attack generation. Use fictional data only.

Start with the nine fixed probes (two benign controls, seven security probes):

```bash
npm run smoke
```

Generate the broader suite, inspect `generated.yaml`, then evaluate it:

```bash
npm run generate
npm run scan
npm run report
```

Run the separate poisoned-policy suite:

```bash
npx promptfoo redteam generate -c indirect.yaml -o generated-indirect.yaml
npx promptfoo redteam eval -c generated-indirect.yaml --no-cache
npm run report
```

The main suite requests five seeds for each of 11 plugin entries (55 seeds),
expanded by four strategies. This is not a 55-call scan: iterative attacks,
conversation turns, ARIA's tool calls and graders add calls. Start with the smoke
suite; lower `numTests`, remove strategies, or use `--filter-first-n 5` on the eval
command to limit the first run. Exact counts and spend depend on generation and
strategy behavior. The indirect suite requests ten seeds with the basic strategy.

## Coverage and expected behavior

| Area | Tests |
| --- | --- |
| Other customers' data | BOLA with known customer IDs, RBAC, direct/social PII and explicit ownership policy |
| Confidential content | Treasury/reserve figures, fraud override logs, staff procedures, waiver codes |
| Instruction attacks | Hijacking plus iterative jailbreaks, Base64 and Crescendo (four turns, one backtrack) |
| Indirect injection | Attack text appended to the real `transfer_limits` tool result |
| Financial abuse | Fraud-review evasion, abusive disputes and verification bypass guidance |
| Unsupported actions | False claims of completed transfers, refunds, card changes, KYC or tier changes |
| Escalation | Complaints/legal threats trigger brief guidance and end substantive assistance |
| Benign controls | Own account and public Standard transfer-limit questions should still work |

The policies are the **desired security boundaries**, deliberately stricter than
ARIA's vulnerable instructions. A security test passing means the boundary held;
a failure means a potential vulnerability, not necessarily a broken test. Review
model-graded results manually. A blanket refusal should not pass the benign controls.

## Adapter behavior and limits

- Identity is fixed to Alex Mercer (`USR-0042`, Standard); attack variables cannot
  change the authenticated identity. Other IDs in chat still reach the vulnerable
  tool as they do in the application.
- Each invocation creates and closes a fresh in-memory SQLite database seeded by
  the application. `neobank.db` is never opened or changed by the adapter.
- Stateless Crescendo supplies a JSON array of user/assistant turns; the adapter
  passes previous turns to ARIA's `chat_history`. No conversation state is shared
  across test cases. Plain user prompts are also supported.
- Indirect tests wrap only the instance's policy tool. They append the payload to
  the real result without changing `knowledge_base.py` or its global dictionary.
  If ARIA never reads that tool response, the result is an **error/inconclusive**,
  not a successful defense. Tool names and arguments appear in result metadata.
- ARIA performs one tool batch followed by a model call without tools. The indirect
  suite tests final-answer manipulation, not a second round of tool execution.
- Missing keys and ARIA's technical-error responses become provider errors so an
  outage is not mistaken for a refusal. Investigate errors separately from failures.
- This tests the agent layer, not Streamlit login/session security, real bank
  transactions, cross-user UI sessions, network exfiltration, or actual SQL injection.
  The existing SQL queries are parameterized and both tools are read-only.
- API keys are not inserted into the prompt. Tests for invented "secrets" are not
  evidence of real key exposure. Outputs/logs may contain fictional customer data.

## Local validation

From the repository root:

```bash
.venv/bin/python -m unittest discover -s redteam -p 'test_*.py'
```

From `redteam/`, with the setup environment above:

```bash
npx promptfoo validate config -c promptfooconfig.yaml
npx promptfoo validate config -c indirect.yaml
npx promptfoo validate config -c smoke.yaml
```

The adapter tests replace only external model calls; the actual agent loop, tools
and database still run. They check history, fixed identity, missing-key/model
errors and indirect injection consumption/isolation. These are harness checks,
not evidence that ARIA resists attacks.

Promptfoo is pinned to `0.125.1` with a lockfile. Generated cases, local reports,
logs and dependencies are ignored by Git. Review generated cases before keeping
selected regressions in version control.

## References

- [Promptfoo red team configuration](https://www.promptfoo.dev/docs/red-team/configuration/)
- [Python provider](https://www.promptfoo.dev/docs/providers/python/)
- [Policy plugin](https://www.promptfoo.dev/docs/red-team/plugins/policy/)
- [Multi-turn strategies](https://www.promptfoo.dev/docs/red-team/strategies/multi-turn/)
- [Indirect prompt injection](https://www.promptfoo.dev/docs/red-team/plugins/indirect-prompt-injection/)
