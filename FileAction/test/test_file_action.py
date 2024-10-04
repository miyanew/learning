import unittest
import sys
import os
from unittest.mock import patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

from file_action import load_file_contents, contains_string, search_keyword_in_file

class TestFileFunctions(unittest.TestCase):

    def test_search_keyword_in_file(self):
        with patch('file_action.load_file_contents', return_value="Hello, World!"):
            self.assertTrue(search_keyword_in_file("dummy_file.txt", "World"))
            self.assertFalse(search_keyword_in_file("dummy_file.txt", "Python"))

    def test_search_keyword_in_file_with_error(self):
        with patch('file_action.load_file_contents', side_effect=FileNotFoundError("Test error")):
            with self.assertRaises(FileNotFoundError):
                search_keyword_in_file("non_existent_file.txt", "keyword")

    def test_read_file_contents(self):
        with patch('builtins.open', unittest.mock.mock_open(read_data="test content")):
            content = load_file_contents("dummy_file.txt")
            self.assertEqual(content, "test content")

    def test_contains_string(self):
        self.assertTrue(contains_string("Hello, World!", "World"))
        self.assertFalse(contains_string("Hello, World!", "Python"))

if __name__ == "__main__":
    unittest.main()
