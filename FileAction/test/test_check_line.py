import unittest
import sys
import tempfile
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

from file_action import contains_string

class TestContainsString(unittest.TestCase):

    def setUp(self):
        # テスト用の一時ファイルを作成
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file.write("Hello, World!\nThis is a test file.\nPython is great.\n")
        self.temp_file.close()

    def tearDown(self):
        # テスト後に一時ファイルを削除
        os.unlink(self.temp_file.name)

    def test_keyword_found(self):
        # キーワードが見つかる場合のテスト
        self.assertTrue(contains_string(self.temp_file.name, "World"))
        self.assertTrue(contains_string(self.temp_file.name, "test"))
        self.assertTrue(contains_string(self.temp_file.name, "Python"))

    def test_keyword_not_found(self):
        # キーワードが見つからない場合のテスト
        self.assertFalse(contains_string(self.temp_file.name, "Java"))
        self.assertFalse(contains_string(self.temp_file.name, "OpenAI"))

    def test_file_not_found(self):
        # 存在しないファイルを指定した場合のテスト
        with self.assertRaises(FileNotFoundError):
            contains_string("non_existent_file.txt", "keyword")

    def test_io_error(self):
        # IOErrorが発生する場合のテスト
        # 例: ファイルに読み取り権限がない場合
        os.chmod(self.temp_file.name, 0o000)  # ファイルの権限を変更
        with self.assertRaises(IOError):
            contains_string(self.temp_file.name, "keyword")
        os.chmod(self.temp_file.name, 0o644)  # 権限を元に戻す

    def test_empty_file(self):
        # 空のファイルに対するテスト
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as empty_file:
            pass
        self.assertFalse(contains_string(empty_file.name, "keyword"))
        os.unlink(empty_file.name)

    def test_case_sensitivity(self):
        # 大文字小文字の区別をテスト
        self.assertTrue(contains_string(self.temp_file.name, "World"))
        self.assertFalse(contains_string(self.temp_file.name, "world"))

if __name__ == '__main__':
    unittest.main()
