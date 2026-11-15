# Copyright (c) 2026 Daniel Joppi (https://github.com/swarm-routing)
# SPDX-License-Identifier: MIT OR GPL-2.0-only
cmake_minimum_required(VERSION 3.24)
project(ara_core LANGUAGES CXX)
# The standard of the ns-3 release the org supports (CMAKE_CXX_STANDARD_MINIMUM).
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SWARM_CORE_DIR "" CACHE PATH "swarm-core's core/; empty: the release swarm-core.lock names")
if(SWARM_CORE_DIR)
  add_subdirectory(${SWARM_CORE_DIR} ${CMAKE_CURRENT_BINARY_DIR}/swarm-core)
else()
  file(STRINGS "${CMAKE_CURRENT_LIST_DIR}/../swarm-core.lock" _lock REGEX "^SWARM_CORE_")
  foreach(_kv IN LISTS _lock)
    string(REGEX MATCH "^([A-Z0-9_]+)=(.*)$" _ "${_kv}")
    set(${CMAKE_MATCH_1} "${CMAKE_MATCH_2}")
  endforeach()
  include(FetchContent)
  FetchContent_Declare(swarm_core
    URL https://github.com/${SWARM_CORE_REPO}/releases/download/${SWARM_CORE_TAG}/${SWARM_CORE_ASSET}
    URL_HASH SHA256=${SWARM_CORE_SHA256}
    SOURCE_SUBDIR core
    DOWNLOAD_EXTRACT_TIMESTAMP FALSE)
  FetchContent_MakeAvailable(swarm_core)
endif()

add_library(ara_core ara-router.cc)
target_link_libraries(ara_core PUBLIC swarm::core)
