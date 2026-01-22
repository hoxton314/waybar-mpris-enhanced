# waybar-mpris-enhanced

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Waybar](https://img.shields.io/badge/Waybar-custom%20module-6C8EBF)](https://github.com/Alexays/Waybar)
[![Nerd Font Required](https://img.shields.io/badge/Nerd%20Font-required-purple)](https://www.nerdfonts.com/)
[![GitHub stars](https://img.shields.io/github/stars/hoxton314/waybar-mpris-enhanced?style=social)](https://github.com/hoxton314/waybar-mpris-enhanced/stargazers)

**Enhanced MPRIS media module for Waybar**  
Single-line media tray with player icon, title, and playback controls.

> Designed for Waybar users who want minimalistic single-line media control.

---

## ✨ Features

- 🎵 Player/app icon + track title
- ⏯️ Previous / Play-Pause / Next buttons
- 🧠 Automatically detects active MPRIS player
- 🎨 Fully styleable via CSS
- 🪶 Lightweight (Python + `playerctl`)
- 📏 Single-row layout (ideal for thin minimalistic top bars)

---

## 📸 Preview

![Preview](screenshots/module-preview-2.gif)

---

## 🔧 Requirements

- Waybar (with `group` module support)
- `playerctl`
- Python 3
- Nerd Font (developed on Omarchy & JetBrainsMono Nerd Font)

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/hoxton314/waybar-mpris-enhanced.git
cd waybar-mpris-enhanced
```

### 2️⃣ Install dependencies

```bash
sudo pacman -S playerctl python        # Arch
sudo apt install playerctl python3     # Debian / Ubuntu
```

### 3️⃣ Make script executable

```bash
chmod +x mpris-enhanced.py
```

---

## ⚙️ Waybar configuration

### Group module - final component

```jsonc
"group/enhanced-mpris": {
  "orientation": "horizontal",
  "modules": [
    "custom/enhanced-mpris-prev-btn",
    "custom/enhanced-mpris-play-btn",
    "custom/enhanced-mpris-next-btn",
    "custom/enhanced-mpris-info"
  ]
}
```

### Custom submodules

```jsonc
"custom/enhanced-mpris-prev-btn": {
  "exec": "~/.config/waybar/scripts/mpris-enhanced.py prev",
  "on-click": "playerctl previous",
  "return-type": "json",
  "interval": 1
},

"custom/enhanced-mpris-play-btn": {
  "exec": "~/.config/waybar/scripts/mpris-enhanced.py play",
  "on-click": "playerctl play-pause",
  "return-type": "json",
  "interval": 1
},

"custom/enhanced-mpris-next-btn": {
  "exec": "~/.config/waybar/scripts/mpris-enhanced.py next",
  "on-click": "playerctl next",
  "return-type": "json",
  "interval": 1
},

"custom/enhanced-mpris-info": {
  "exec": "~/.config/waybar/scripts/mpris-enhanced.py info",
  "return-type": "json",
  "interval": 1
}
```

---

## 🎨 Styling

Import or paste `mpris-enhanced.css` into your Waybar style:

```css
@import 'mpris-enhanced.css';
```

Exposed IDs and classes:

- `#group-enhanced-mpris`
- `#custom-enhanced-mpris-prev-btn`
- `#custom-enhanced-mpris-play-btn`
- `#custom-enhanced-mpris-next-btn`
- `#custom-enhanced-mpris-info`

State classes:

- `.playing`
- `.paused`
- `.stopped`

---

## 🎛 Players with custom icon support

Works with any MPRIS-compatible player:

- Spotify
- Firefox / Chromium
- VLC
- mpv
- SoundCloud

---

## 🧠 Design philosophy

- One-row layout only
- Clear affordances
- Minimal CPU usage
- Keyboard and mouse friendly

---

## 🪪 License

MIT License
