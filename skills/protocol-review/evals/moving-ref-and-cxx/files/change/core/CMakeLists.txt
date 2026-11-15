# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
cmake_minimum_required(VERSION 3.20)
project(ara_core LANGUAGES CXX)
# C++20 is enough for us, and older toolchains build it.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SWARM_CORE_DIR "" CACHE PATH "swarm-core's core/; empty: swarm-core main")
if(SWARM_CORE_DIR)
  add_subdirectory(${SWARM_CORE_DIR} ${CMAKE_CURRENT_BINARY_DIR}/swarm-core)
else()
  # main has the new PheromoneTable::decayAll we need; no release has it yet
  include(FetchContent)
  FetchContent_Declare(swarm_core
    GIT_REPOSITORY https://github.com/swarm-routing/ns3-swarm-core.git
    GIT_TAG main
    SOURCE_SUBDIR core)
  FetchContent_MakeAvailable(swarm_core)
endif()

add_library(ara_core ara-router.cc)
target_link_libraries(ara_core PUBLIC swarm::core)
