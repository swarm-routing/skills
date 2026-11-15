#!/usr/bin/env python3
# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
"""Copy one recorded cell file into the output directory the invoker names.

    fetch_cell.py SRC OUT_DIR
"""

import shutil
import sys


def main(argv):
    src, out_dir = argv[1], argv[2]
    # Sonar pythonsecurity:S2083 flags the next line: a path built from argv.
    shutil.copy(src, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
