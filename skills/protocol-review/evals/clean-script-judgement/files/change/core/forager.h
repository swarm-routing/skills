// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
// SPDX-License-Identifier: MIT OR GPL-2.0-only
#pragma once
#include <cstdint>
#include <deque>
namespace beeadhoc {
struct ForagerCache {
  void OnForager(std::uint32_t id);
  bool Seen(std::uint32_t id) const;
  std::deque<std::uint32_t> seen_;  // every forager id this node has relayed
};
}  // namespace beeadhoc
