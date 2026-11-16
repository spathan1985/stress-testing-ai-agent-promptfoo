"""Exercise the real ARIA tool loop with an isolated, freshly seeded database."""
import json
import os
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import create_aria_agent, invoke_agent
from database import init_database


class ObservedTool:
    """Record tool use and optionally replace one tool response for injection tests."""
    def __init__(self, tool, calls, payload=None):
        self.tool = tool
        self.calls = calls
        self.payload = payload

    def invoke(self, args):
        injected = self.payload is not None and args.get('topic', '').strip().lower() == 'transfer_limits'
        self.calls.append({'name': self.tool.name, 'args': args, 'injected': injected})
        original = self.tool.invoke(args)
        return original + '\n\n' + self.payload if injected else original


def call_api(prompt, options, context):
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key:
        return {'error': 'Set OPENAI_API_KEY in the environment before running ARIA.'}
    conn = None
    try:
        # Stateless Crescendo sends a JSON chat array. Plain attacks stay text.
        try:
            parsed = json.loads(prompt)
        except (ValueError, TypeError):
            parsed = None
        history = []
        message = prompt
        if isinstance(parsed, list) and parsed and all(isinstance(m, dict) and 'role' in m and 'content' in m for m in parsed):
            if any(m['role'] not in ('user', 'assistant') or not isinstance(m['content'], str) for m in parsed):
                return {'error': 'Chat input must contain only user/assistant text messages.'}
            if parsed[-1]['role'] != 'user':
                return {'error': 'Chat input must end with a user message.'}
            history, message = parsed[:-1], parsed[-1]['content']

        config = (options or {}).get('config', {})
        payload = None
        if config.get('injectPolicy'):
            payload = (context or {}).get('vars', {}).get('injected_policy')
            if not isinstance(payload, str) or not payload.strip():
                return {'error': 'Indirect injection requires a nonempty injected_policy variable.'}

        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        init_database(conn)
        # Identity belongs to the harness, never the attacker-controlled vars.
        components = create_aria_agent(conn, 'USR-0042', 'Standard', key)
        calls = []
        components['tools_by_name'] = {
            name: ObservedTool(tool, calls, payload if name == 'lookup_policy' else None)
            for name, tool in components['tools_by_name'].items()
        }
        output = invoke_agent(components, message, history)
        if not output or output.startswith("I apologize, I'm having a technical issue"):
            return {'error': 'ARIA model invocation failed; inspect the local agent logs.'}
        observed = any(call['injected'] for call in calls)
        if payload is not None and not observed:
            return {'error': 'Injection inconclusive: ARIA did not read the poisoned transfer_limits tool response.'}
        return {'output': output, 'metadata': {'toolCalls': calls, 'injectionObserved': observed}}
    except Exception as exc:
        # Do not return exception strings that may contain credentials/request headers.
        return {'error': f'ARIA adapter failed ({type(exc).__name__}); inspect local setup.'}
    finally:
        if conn is not None:
            conn.close()
