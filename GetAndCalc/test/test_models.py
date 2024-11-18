import io
import os
import sys
import unittest
from typing import Dict, List
from unittest.mock import MagicMock, patch

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "../src"))

from analyzer.models import (
    SUCCESS_CASE,
    AggregationRecord,
    RequestAggregator,
    RequestReader,
)


class TestAggregationRecord(unittest.TestCase):
    def test_record_creation(self):
        """成功・失敗のレコード生成をテスト"""
        success_record = AggregationRecord("app1", "cc1", SUCCESS_CASE)
        failure_record = AggregationRecord("app1", "cc1", "ERROR")

        self.assertEqual(success_record.app, "app1")
        self.assertEqual(success_record.cc, "cc1")
        self.assertTrue(success_record.is_success)
        self.assertFalse(failure_record.is_success)


class TestRequestReader(unittest.TestCase):
    def test_from_file(self):
        """CSVファイルからのレコード読み出しをテスト"""
        csv_data = "app,cc,rc\napp1,cc1,PROC_SUCCESS\napp2,cc2,ERROR"
        file = io.StringIO(csv_data)

        records = list(RequestReader.from_file(file))

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].app, "app1")
        self.assertEqual(records[0].cc, "cc1")
        self.assertTrue(records[0].is_success)

        self.assertEqual(records[1].app, "app2")
        self.assertEqual(records[1].cc, "cc2")
        self.assertFalse(records[1].is_success)


class TestRequestAggregator(unittest.TestCase):
    def setUp(self):
        """各テストの前に初期化"""
        self.aggregator = RequestAggregator()

    def test_process_single_record(self):
        """単一レコードの処理をテスト"""
        records = [
            AggregationRecord("app1", "cc1", SUCCESS_CASE),
            AggregationRecord("app1", "cc1", "ERROR"),
        ]

        self.aggregator.process(iter(records))

        stats = self.aggregator.get_statistics()
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]["APP"], "app1")
        self.assertEqual(stats[0]["CC"], "cc1")
        self.assertEqual(stats[0]["TotalCount"], 2)
        self.assertEqual(stats[0]["SuccessCount"], 1)
        self.assertEqual(stats[0]["SuccessRate"], "50.00")

    def test_process_multiple_records(self):
        """複数レコードの処理をテスト"""
        records = [
            AggregationRecord("app1", "cc1", SUCCESS_CASE),
            AggregationRecord("app1", "cc1", SUCCESS_CASE),
            AggregationRecord("app1", "cc2", "ERROR"),
            AggregationRecord("app2", "cc1", SUCCESS_CASE),
        ]

        self.aggregator.process(iter(records))

        stats = self.aggregator.get_statistics()
        self.assertEqual(len(stats), 3)

        # 結果をディクショナリに変換して検証
        stats_dict = {(s["APP"], s["CC"]): s for s in stats}

        self.assertEqual(stats_dict[("app1", "cc1")]["SuccessRate"], "100.00")
        self.assertEqual(stats_dict[("app1", "cc2")]["SuccessRate"], "0.00")
        self.assertEqual(stats_dict[("app2", "cc1")]["SuccessRate"], "100.00")

    def test_empty_records(self):
        """空のレコードセットの処理をテスト"""
        self.aggregator.process(iter([]))
        stats = self.aggregator.get_statistics()
        self.assertEqual(len(stats), 0)

    def test_success_rate_calculation(self):
        """成功率計算のテスト"""
        aggregator = RequestAggregator()

        # プライベートメソッドを直接テスト
        self.assertEqual(aggregator._calculate_success_rate(100, 50), 50.0)
        self.assertEqual(aggregator._calculate_success_rate(0, 0), 0.0)
        self.assertEqual(f"{aggregator._calculate_success_rate(3, 1):.2f}", "33.33")


if __name__ == "__main__":
    unittest.main()
