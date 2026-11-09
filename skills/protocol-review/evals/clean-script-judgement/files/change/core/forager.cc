// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
// SPDX-License-Identifier: MIT OR GPL-2.0-only
#include "core/forager.h"
#include <algorithm>
namespace beeadhoc {
void ForagerCache::OnForager(std::uint32_t id) { seen_.push_back(id); }
bool ForagerCache::Seen(std::uint32_t id) const { return std::find(seen_.begin(), seen_.end(), id) != seen_.end(); }
}  // namespace beeadhoc
