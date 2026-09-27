import unittest
from unittest.mock import MagicMock, patch

from supervisor import supervisor_node


class TestSupervisorRouting(unittest.TestCase):

    # We patch the entire ROUTING_LLM object to bypass Pydantic's strict validation
    @patch('supervisor.ROUTING_LLM')
    def test_sql_routing_logic(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "SQL"
        mock_llm.invoke.return_value = mock_response
        
        state = {"question": "How many active employees are in the system?", "history": []}
        result = supervisor_node(state)
        
        self.assertEqual(result["route"], "SQL")

    @patch('supervisor.ROUTING_LLM')
    def test_rag_routing_logic(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "RAG"
        mock_llm.invoke.return_value = mock_response
        
        state = {"question": "What is the corporate remote work policy?", "history": []}
        result = supervisor_node(state)
        
        self.assertEqual(result["route"], "RAG")

    @patch('supervisor.ROUTING_LLM')
    def test_chat_fallback_logic(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "I am unsure."
        mock_llm.invoke.return_value = mock_response
        
        state = {"question": "What is your favorite color?", "history": []}
        result = supervisor_node(state)
        
        self.assertEqual(result["route"], "CHAT")

if __name__ == '__main__':
    unittest.main()