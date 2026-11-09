# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
import unittest

from python.ns3_tool.sweep_csv import to_csv


class SweepCsvTest(unittest.TestCase):
    def test_rows(self):
        text = to_csv([{"arm": "ara", "value": 10, "pdr": 0.9, "delay_ms": 12.5}])
        self.assertIn("ara,10,0.9,12.5", text)


if __name__ == "__main__":
    unittest.main()
