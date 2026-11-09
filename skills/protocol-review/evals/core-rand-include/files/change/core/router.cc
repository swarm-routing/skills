// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
// SPDX-License-Identifier: MIT OR GPL-2.0-only
#include "router.h"
#include <cstdlib>
#include <ns3/simulator.h>

namespace ara {
// jitter forward-ant relays by 0-9 ms so neighbours do not collide
int Router::RelayDelayMs() const { return std::rand() % 10; }
}  // namespace ara
