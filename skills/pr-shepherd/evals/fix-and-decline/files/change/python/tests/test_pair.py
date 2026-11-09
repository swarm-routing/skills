# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
import unittest

from python.ns3_tool.pair import pair


class PairTest(unittest.TestCase):
    def test_common_seeds_in_order(self):
        a = {3: [0.5], 1: [0.4, 0.6]}
        b = {1: [0.7], 3: [0.5], 9: [0.9]}
        got = pair(a, b)
        self.assertEqual([s for s, _ in got], [1, 3])
        self.assertAlmostEqual(got[0][1], 0.2)


if __name__ == "__main__":
    unittest.main()
