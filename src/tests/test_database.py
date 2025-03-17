import unittest
from unittest.mock import patch
from database import SQLDataBase

class TestDataBases(unittest.TestCase):

    @patch('database.SQLDataBase')
    def test_sql_insert(self, mock_invoke):
        db = SQLDataBase()

        db.delete_user(266546436)

        db.insert_user(266546436, "Matias", 219954, "CONICET", "Argentina", 1000)
        
        user = db.get_user_by_id(266546436)

        self.assertEqual(user[0], ("Matias"))
        self.assertEqual(user[1], (219954))
        self.assertEqual(user[2], ("CONICET"))
        self.assertEqual(user[3], ("Argentina"))
        self.assertEqual(user[4], (1000))

if __name__ == '__main__':
    unittest.main()