import unittest
from unittest.mock import patch
from utils import get_all_pdf_files

class TestUtils(unittest.TestCase):

    @patch('utils.get_all_pdf_files')
    def test_get_pdfs(self, mock_invoke):

        list_pdf = get_all_pdf_files()

        pdf1 = (list_pdf[0]).split("\\pdf\\")[1]
        pdf2 = (list_pdf[1]).split("\\pdf\\")[1]
        
        self.assertEqual(pdf1, ("Medios de pago - AtomChat.pdf"))
        self.assertEqual(pdf2, ("Servicios - AtomChat.pdf"))

if __name__ == '__main__':
    unittest.main()