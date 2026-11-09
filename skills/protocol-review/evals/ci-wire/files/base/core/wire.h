// Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
// SPDX-License-Identifier: MIT OR GPL-2.0-only
#pragma once
#include <cstdint>
namespace ara {
constexpr std::uint8_t kWireVersion = 1;
struct AntHeader { std::uint8_t version; std::uint32_t seq; std::uint16_t hops; };
}  // namespace ara
