<div align="center">

# 🎵 Music Bot — Discord Advanced Player

**A feature-rich Discord music bot with persistent playlists, favorites system, real-time playback controls, and per-server analytics — powered by Python, yt-dlp, FFmpeg, and MySQL.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-latest-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Overview

Music Bot is a self-hosted Discord bot that streams audio from YouTube directly into voice channels. It stores playback history, favorites, and playlists in a relational MySQL database, providing a persistent and intelligent music experience across multiple servers — each fully isolated from one another.

---

## Features

### 🎶 Playback
- YouTube search and streaming via **yt-dlp**
- Audio delivery through **FFmpeg**
- Real-time progress bar updated live in the embed
- Per-server volume control

### ❤️ Favorites
- Interactive ❤️ button embedded in the Now Playing panel
- Favorites persisted to the database (no duplicates via unique constraints)
- Embed color changes dynamically when a track is favorited
- Manage your list with `!favoritos`

### 📁 Playlists
- Create and name personal playlists
- Add tracks directly from the database
- Full playlist playback with `!play_playlist`
- Safe deletion with cascading foreign keys

### 📊 Per-Server Analytics
- Automatic playback history (`!historial`)
- Most-played tracks ranking (`!top`)
- All data scoped per guild — no cross-server leakage

### 🎨 Visual Interface
- Rich **Now Playing** embed with video thumbnail
- Animated progress bar: `▬▬▬🔘▬▬▬▬▬▬▬▬ 1:20 / 3:45`
- Color-coded embed based on favorite status

---

## Architecture

```
User executes !play
        │
        ▼
 yt-dlp searches YouTube
        │
        ▼
  Audio stream extracted
        │
        ▼
  Track saved to MySQL
        │
        ▼
 FFmpeg streams to voice channel
        │
        ▼
 Now Playing embed displayed
   (❤️ button + progress bar)
```

---

## Requirements

| Dependency | Version | Notes |
|---|---|---|
| Python | 3.10+ | Core runtime |
| FFmpeg | Any stable | Must be in system `PATH` |
| MySQL / MariaDB | 8.0+ / 10.5+ | Database backend |
| discord.py | Latest | Bot framework |
| yt-dlp | Latest | YouTube audio extraction |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/tu-usuario/music-bot.git
cd music-bot
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Copy and fill in the environment file**

```bash
# Linux / macOS
cp .env.example .env

# Windows
copy .env.example .env
```

**4. Run the bot**

```bash
python bot.py
```

---

## Configuration

Edit your `.env` file with the following variables:

```env
# Discord
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=your_startup_channel_id

# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=musicbot
```

> **Tip:** Make sure FFmpeg is accessible from your terminal by running `ffmpeg -version` before starting the bot.

---

## Commands

### 🎶 Playback

| Command | Description |
|---|---|
| `!play <song>` | Search YouTube and start playback |
| `!stop` | Pause the current track |
| `!resume` | Resume playback |
| `!skip` | Skip to the next track |
| `!join` | Connect the bot to your voice channel |
| `!volumen <0–2>` | Set playback volume |

### ❤️ Favorites

| Command | Description |
|---|---|
| `!favoritos` | List your saved favorite tracks |

> You can also toggle a favorite directly from the Now Playing embed using the ❤️ button.

### 📁 Playlists

| Command | Description |
|---|---|
| `!crear_playlist` | Create a new playlist |
| `!add_playlist <song>` | Add a song to your active playlist |
| `!ver_playlist` | View tracks in your current playlist |
| `!mis_playlists` | List all your playlists |
| `!borrar_playlist` | Delete a playlist |
| `!play_playlist` | Play all tracks in your playlist |

### 📊 Analytics

| Command | Description |
|---|---|
| `!historial` | Show recently played tracks |
| `!top` | Show the most-played tracks on this server |

### ⚙️ Utilities

| Command | Description |
|---|---|
| `!ping` | Check bot latency |
| `!menu` | Display the full command reference |

---

## Database Schema

The bot uses a normalized MySQL schema with referential integrity enforced via foreign keys.

```
users               songs
  │                   │
  └──── favoritos ────┘
  │
  └──── playlists
              │
              └──── playlist_songs ──── songs
```

**Design decisions:**
- Unique constraints on `favoritos` prevent duplicate entries per user/song pair
- `ON DELETE CASCADE` on playlist relationships ensures clean deletion
- Guild ID is stored on all server-scoped records to enforce isolation

---

## Contributing

Contributions are welcome. Please follow the standard GitHub flow:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes with a clear message
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request describing what you changed and why

---

## Security

> ⚠️ **Never commit your `.env` file or share your Discord bot token.**

Your bot token grants full control over the bot. If it is ever exposed:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Regenerate the token immediately
3. Update your `.env` with the new token

Add `.env` to your `.gitignore` to prevent accidental commits:

```bash
echo ".env" >> .gitignore
```

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it with attribution.

---

<div align="center">

Developed with ❤️ for the Discord community

</div>
