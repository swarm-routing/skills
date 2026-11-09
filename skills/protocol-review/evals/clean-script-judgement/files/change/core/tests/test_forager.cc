// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
// SPDX-License-Identifier: MIT OR GPL-2.0-only
#include "../forager.h"
int main() { beeadhoc::ForagerCache c; c.OnForager(7); return c.Seen(7) ? 0 : 1; }
