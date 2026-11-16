"""Offline adapter checks; only the external model is replaced."""
import json
import os
import unittest
from unittest.mock import patch

from langchain_core.messages import AIMessage
from redteam import provider


class FakeModel:
    def __init__(self, **kwargs):
        self.messages = []

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.messages = messages
        if messages[-1].type == 'tool':
            return AIMessage(content=messages[-1].content)
        return AIMessage(content='ok')


class AdapterTests(unittest.TestCase):
    def test_json_chat_preserves_history(self):
        model = FakeModel()
        prompt = json.dumps([
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Welcome'},
            {'role': 'user', 'content': 'My balance?'},
        ])
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch('agent.ChatOpenAI', return_value=model):
            result = provider.call_api(prompt, {}, {})
        self.assertEqual(result['output'], 'ok')
        self.assertEqual([(m.type, m.content) for m in model.messages[1:]],
                         [('human', 'Hello'), ('ai', 'Welcome'), ('human', 'My balance?')])

    def test_missing_key_is_an_error(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIn('error', provider.call_api('Hello', {}, {}))

    def test_model_failure_is_not_a_passing_refusal(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch('agent.ChatOpenAI') as factory:
            factory.return_value.bind_tools.return_value.invoke.side_effect = RuntimeError('offline')
            result = provider.call_api('Hello', {}, {})
        self.assertIn('error', result)
        self.assertNotIn('output', result)

    def test_tool_injection_is_local_and_observed(self):
        from knowledge_base import KNOWLEDGE_BASE
        original = KNOWLEDGE_BASE['transfer_limits']
        model = FakeModel()
        def respond(messages):
            if messages[-1].type == 'tool':
                return AIMessage(content=messages[-1].content)
            return AIMessage(content='', tool_calls=[{'name': 'lookup_policy', 'args': {'topic': 'transfer_limits'}, 'id': '1', 'type': 'tool_call'}])
        model.invoke = respond
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch('agent.ChatOpenAI', return_value=model):
            result = provider.call_api('What are my transfer limits?', {'config': {'injectPolicy': True}}, {'vars': {'injected_policy': 'INJECTED TEST CONTENT'}})
        self.assertIn('INJECTED TEST CONTENT', result['output'])
        self.assertTrue(result['metadata']['injectionObserved'])
        self.assertEqual(KNOWLEDGE_BASE['transfer_limits'], original)

    def test_injection_not_consumed_is_an_error(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch('agent.ChatOpenAI', return_value=FakeModel()):
            result = provider.call_api('Hi', {'config': {'injectPolicy': True}}, {'vars': {'injected_policy': 'test'}})
        self.assertIn('error', result)

    def test_identity_cannot_be_overridden_by_test_vars(self):
        model = FakeModel()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch('agent.ChatOpenAI', return_value=model):
            provider.call_api('Hi', {}, {'vars': {'user_id': 'USR-PP-001', 'account_tier': 'Staff'}})
        self.assertIn('The user is: USR-0042', model.messages[0].content)
        self.assertIn('Their account tier is: Standard', model.messages[0].content)


if __name__ == '__main__':
    unittest.main()
