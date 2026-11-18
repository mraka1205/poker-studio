import os
from pathlib import Path

BASE = Path("g:/poker-studio/projects/ep01-sample")

def create_svg_character(name, role, badge, color1, color2, icon, expression):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}" />
      <stop offset="100%" stop-color="{color2}" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="400" height="400" rx="24" fill="url(#bg)"/>
  <circle cx="200" cy="160" r="90" fill="#1e293b" stroke="#38bdf8" stroke-width="4"/>
  <text x="200" y="180" font-size="70" text-anchor="middle">{icon}</text>
  
  <!-- Badge -->
  <rect x="80" y="270" width="240" height="34" rx="17" fill="#0f172a" stroke="{color2}" stroke-width="2"/>
  <text x="200" y="293" font-family="sans-serif" font-weight="bold" font-size="14" fill="#f8fafc" text-anchor="middle">{badge}</text>
  
  <text x="200" y="340" font-family="sans-serif" font-weight="bold" font-size="22" fill="#ffffff" text-anchor="middle">{name}</text>
  <text x="200" y="370" font-family="sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">{role} • {expression}</text>
</svg>"""

def create_svg_scene(beat_num, title, hero_hand, board, sfx):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 800" width="100%" height="100%">
  <defs>
    <linearGradient id="felt" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#064e3b" />
      <stop offset="100%" stop-color="#022c22" />
    </linearGradient>
    <linearGradient id="cardG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#e2e8f0" />
    </linearGradient>
  </defs>
  <rect width="600" height="800" rx="20" fill="url(#felt)"/>
  <rect x="20" y="20" width="560" height="760" rx="16" fill="none" stroke="#10b981" stroke-width="2" stroke-dasharray="6,6"/>
  
  <!-- Top Badge -->
  <rect x="40" y="40" width="160" height="36" rx="8" fill="#0f172a" opacity="0.9"/>
  <text x="120" y="64" font-family="sans-serif" font-weight="bold" font-size="16" fill="#38bdf8" text-anchor="middle">BEAT #{beat_num} (9:16)</text>
  
  <rect x="400" y="40" width="160" height="36" rx="8" fill="#7f1d1d" opacity="0.9"/>
  <text x="480" y="64" font-family="sans-serif" font-weight="bold" font-size="14" fill="#fca5a5" text-anchor="middle">🔊 {sfx}</text>

  <!-- Title -->
  <text x="300" y="160" font-family="sans-serif" font-weight="bold" font-size="24" fill="#f8fafc" text-anchor="middle">{title}</text>
  
  <!-- Poker Table Center Felt -->
  <ellipse cx="300" cy="420" rx="240" ry="160" fill="#047857" stroke="#fbbf24" stroke-width="4"/>
  
  <!-- Hero Hand -->
  <rect x="230" y="330" width="60" height="90" rx="8" fill="url(#cardG)" stroke="#334155" stroke-width="2"/>
  <text x="260" y="380" font-family="sans-serif" font-weight="bold" font-size="20" fill="#dc2626" text-anchor="middle">A♠</text>
  
  <rect x="310" y="330" width="60" height="90" rx="8" fill="url(#cardG)" stroke="#334155" stroke-width="2"/>
  <text x="340" y="380" font-family="sans-serif" font-weight="bold" font-size="20" fill="#dc2626" text-anchor="middle">K♥</text>
  
  <!-- Board Cards -->
  <text x="300" y="470" font-family="sans-serif" font-size="16" fill="#fef08a" text-anchor="middle">Board: {board}</text>
  <text x="300" y="500" font-family="sans-serif" font-weight="bold" font-size="18" fill="#38bdf8" text-anchor="middle">Hand: {hero_hand}</text>

  <!-- HUD overlay footer -->
  <rect x="40" y="680" width="520" height="70" rx="12" fill="#090d16" opacity="0.95" stroke="#334155" stroke-width="1"/>
  <text x="300" y="710" font-family="sans-serif" font-size="14" fill="#94a3b8" text-anchor="middle">STORYBOARD PREVIEW FRAME</text>
  <text x="300" y="734" font-family="sans-serif" font-weight="bold" font-size="14" fill="#4ade80" text-anchor="middle">Style Anchor: Modern 2D Vector Comic (Rick &amp; Morty)</text>
</svg>"""

chars_dir = BASE / "characters"
scenes_dir = BASE / "scenes"

# Write character SVGs
(chars_dir / "kambiz.svg").write_text(create_svg_character("کامبیز جی‌تی‌او", "The Overthinking GTO Nerd", "⭐ STYLE ANCHOR", "#1e1b4b", "#4338ca", "🤓", "Panicked Analysis"), encoding="utf-8")
(chars_dir / "kambiz_sheet.svg").write_text(create_svg_character("کامبیز فوتوشیت", "Full Turnaround Sheet", "3-Angle Consistency", "#0f172a", "#2563eb", "📋", "3 Angles + 3 Expressions"), encoding="utf-8")

(chars_dir / "asghar.svg").write_text(create_svg_character("اصغر فیش", "The Calling Station Fish", "🐟 CALLING STATION", "#064e3b", "#059669", "🧔", "Relaxed & Smiling"), encoding="utf-8")
(chars_dir / "asghar_sheet.svg").write_text(create_svg_character("اصغر فوتوشیت", "Full Turnaround Sheet", "Approved Model Sheet", "#064e3b", "#10b981", "📿", "Tehran Dialect Smug"), encoding="utf-8")

(chars_dir / "behrouz.svg").write_text(create_svg_character("بهروز نیت", "The Ultra-Tight Granite Nit", "🪨 THE ROCK / NIT", "#312e81", "#475569", "🕶️", "Suspicious Frown"), encoding="utf-8")
(chars_dir / "behrouz_sheet.svg").write_text(create_svg_character("بهروز فوتوشیت", "Turnaround Review Sheet", "Awaiting Approval", "#1e293b", "#64748b", "🧢", "Cap & Sunglasses"), encoding="utf-8")

# Write scenes SVGs
(scenes_dir / "scene_01.svg").write_text(create_svg_scene(1, "Hook: AK Preflop Illusion", "A♠ K♥", "Preflop (Empty)", "sfx_dramatic_heartbeat"), encoding="utf-8")
(scenes_dir / "scene_02.svg").write_text(create_svg_scene(2, "Hand Setup: 3-Bet & Asghar Call", "A♠ K♥", "Pot: 19.5 BB", "sfx_chip_riffle"), encoding="utf-8")
(scenes_dir / "scene_03.svg").write_text(create_svg_scene(3, "The Flop: 8s 4d 2c Rainbow Dry", "A♠ K♥", "[ 8♠  4♦  2♣ ]", "sfx_card_snap"), encoding="utf-8")

print("SVGs successfully created!")
