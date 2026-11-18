# -*- coding: utf-8 -*-
"""
Script to generate Phase 1 Storyboard for ep04-poker-hand strictly following
.agent/skills/04-scene-director.md.
"""
import json
import os

STYLE_LOCK = (
    "Handcrafted needle-felted stop-motion animation style, tactile fuzzy wool fiber textures, "
    "visible subtle fuzz, miniature stitched fabric clothing, soft warm overhead studio macro lighting, "
    "shallow depth of field, vertical 9:16 composition, centered framing for YouTube Shorts and Instagram Reels --ar 9:16"
)

MASTER_LOCK = (
    "Maintain exact visual continuity, character seating positions, chip stack colors, table felt textures, "
    "and lighting geometry matching [Episode_Scene_1_Master]."
)

print("Starting storyboard generation...")
