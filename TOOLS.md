# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🎮 AI Operator System

**路徑**: `~/.openclaw/ai-operator/`

### 啟動
```bash
source ~/.openclaw/ai-operator/bin/activate
```

### 執行自我進化
```bash
python -c "from evaluation.evolution_engine import evolution_engine; evolution_engine.run_self_optimization()"
```

### 健康檢查
```bash
python -c "from self_update.self_corrector import health_checker; print(health_checker.run_checks())"
```

### 版本
- 當前: 1.0.0
- 健康分數: 100%

---

## 🌐 瀏覽器

- **Chrome**: `/usr/bin/google-chrome-stable` (安裝於 2026-03-09)
- **控制方式**: OpenClaw browser tool
- **遊戲測試工具**: https://gp001-qa1-simulation.xwautc.online/index
