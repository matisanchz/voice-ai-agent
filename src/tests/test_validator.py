import unittest
from unittest.mock import patch
from validator import validate_name

class TestValidateName(unittest.TestCase):

    @patch('validator.validate_name')
    def test_valid_name(self, mock_invoke):

        mock_invoke.return_value.content = '1'

        result = validate_name('Matias')

        self.assertEqual(result, '1')

    @patch('validator.validate_name')
    def test_invalid_name(self, mock_invoke):
        mock_invoke.return_value.content = '0'

        result = validate_name('Matias957834569734934756')

        self.assertEqual(result, '0')

    @patch('validator.validate_name')
    def test_edge_case_special_characters(self, mock_invoke):

        mock_invoke.return_value.content = '0'

        result = validate_name('M@tias')

        self.assertEqual(result, '0')

    @patch('validator.validate_name')
    def test_invalid_special_characters(self, mock_invoke):

        mock_invoke.return_value.content = '0'

        result = validate_name('M@t|°$')

        self.assertEqual(result, '0')

    @patch('validator.validate_name')
    def test_invalid_special_characters(self, mock_invoke):

        mock_invoke.return_value.content = '1'

        result = validate_name('Matias Sánchez Abrego')

        self.assertEqual(result, '1')

if __name__ == '__main__':
    unittest.main()