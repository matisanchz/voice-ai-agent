import unittest
from unittest.mock import patch
from agent import AgentManager

class TestDataBases(unittest.TestCase):

    @patch('agent.AgentManager')
    def test_agent_name_retrieval(self, mock_invoke):

        user = ["Matias", 219954, "CONICET", "Argentina", 1000]

        agent = AgentManager("2025_03_16_23_35_56_SESSION_200", user, False)

        response = agent.process_chat("¿Sabes cuál es mi nombre? Responder solo con mi nombre, sin puntos ni tildes.")

        self.assertEqual(response.lower(), "matias")

    @patch('agent.AgentManager')
    def test_agent_company_retrieval(self, mock_invoke):

        user = ["Jose", 219958, "AtomChat", "Argentina", 1000]

        agent = AgentManager("2025_03_16_23_35_56_SESSION_201", user, False)

        response = agent.process_chat("¿Sabes en qué compañía trabajo? Responder solo con el nombre de la compañía, sin puntos ni tildes.")

        self.assertEqual(response.lower(), "atomchat")

    @patch('agent.AgentManager')
    def test_agent_country_retrieval(self, mock_invoke):

        user = ["Juan", 219967, "Honda", "Chile", 10000]

        agent = AgentManager("2025_03_16_23_35_56_SESSION_202", user, False)

        response = agent.process_chat("¿Sabes en qué pais resido? Responder solo con el nombre del país, sin puntos ni tildes.")

        self.assertEqual(response.lower(), "chile")

if __name__ == '__main__':
    unittest.main()