<div align="center">

# AutoTouch Patch

**Патч AutoTouch 8.5.5 для jailbroken iOS (arm64, rootless)**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![iOS](https://img.shields.io/badge/iOS-12.2%2B-lightgrey.svg)](https://autotouch.net)
[![Architecture](https://img.shields.io/badge/arch-arm64-orange.svg)](#требования)
[![Version](https://img.shields.io/badge/version-8.5.5-green.svg)](releases/)

Установка одной командой прямо с iPhone · без модификации оригинальных бинарников

[Быстрая установка](#-быстрая-установка) ·
[Releases](https://github.com/smartmaster35rus-dev/autotouch-patch/releases) ·
[Как работает](#-как-работает-патч) ·
[Сборка](#-сборка-deb-самостоятельно)

</div>

---

## О репозитории

| | |
|---|---|
| **Автор** | [@smartmaster35rus-dev](https://github.com/smartmaster35rus-dev) |
| **Лицензия** | [MIT](LICENSE) |
| **Пакет** | `me.autotouch.autotouch.ios8` |
| **Версия** | `8.5.5` |
| **Архитектура** | `iphoneos-arm64` (rootless, `/var/jb/`) |
| **Оригинал** | [AutoTouch](https://autotouch.net) © Kent Krantz |

> Этот репозиторий содержит **патч и скрипты установки**, а не исходный код AutoTouch.  
> Рекомендуется приобретать официальную лицензию у автора приложения.

---

## Требования

| Компонент | Условие |
|-----------|---------|
| iOS | 12.2+ |
| Jailbreak | Rootless (Dopamine, palera1n rootless и т.п.) |
| Tweak engine | **ElleKit** |
| Пакетный менеджер | `dpkg` / Sileo / Zebra / NewTerm |

> Не подходит для старых rootful-сборок (`iphoneos-arm`).

---

## ⚡ Быстрая установка

### Способ 1 — одной командой (рекомендуется)

На iPhone в терминале (NewTerm, MTerminal):

```bash
curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install.sh | bash
```

Скрипт скачает `.deb`, установит пакет и сделает respring.

### Способ 2 — только патч (AutoTouch уже установлен)

```bash
curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install-patch-only.sh | bash
```

Файлы попадут в:

```text
/var/jb/Library/MobileSubstrate/DynamicLibraries/
├── crackATT.dylib
└── crackATT.plist
```

### Способ 3 — вручную

```bash
curl -LO https://github.com/smartmaster35rus-dev/autotouch-patch/releases/download/v8.5.5/me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb
dpkg -r me.autotouch.autotouch.ios8 2>/dev/null || true
dpkg -i me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb
killall -9 SpringBoard
```

### Способ 4 — Sileo / Zebra / Filza

1. Скачайте `.deb` из [Releases](https://github.com/smartmaster35rus-dev/autotouch-patch/releases).
2. Откройте через Filza → **Install**.
3. Respring.

---

## 📁 Структура

```text
autotouch-patch/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── patch/
│   ├── crackATT.dylib      # Substrate-твик (arm64)
│   └── crackATT.plist      # Filter: springboard + AutoTouch
├── releases/
│   └── *.deb               # Готовый патченный пакет
└── scripts/
    ├── install.sh          # Установка с GitHub
    ├── install-patch-only.sh
    ├── build_deb.py        # Сборка .deb
    └── publish.ps1         # Публикация на GitHub (Windows)
```

---

## 🔧 Как работает патч

Добавляется MobileSubstrate-твик **`crackATT`**, перехватывающий методы класса `Global`:

| Метод | Эффект |
|-------|--------|
| `licenseLimitTimeout` | Блокирует таймер ограничения |
| `startLicenseLimitTimer` | Не запускает таймер лимита |
| `init` | Перехват инициализации |
| `objectFromJSONString` | Обход проверки JSON лицензии |

**Filter** (`crackATT.plist`):

- `com.apple.springboard`
- `me.autotouch.AutoTouch.ios8`

Оригинальные бинарники AutoTouch **не изменяются**.

---

## 🛠 Сборка .deb самостоятельно

<details>
<summary>Развернуть инструкцию</summary>

### 1. Получить оригинальный пакет

Скачайте `me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64.deb`.

### 2. Распаковать

```bash
python3 scripts/extract_deb.py me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64.deb arm64/extracted
```

### 3. Добавить патч

```bash
cp patch/crackATT.* arm64/extracted/data/var/jb/Library/MobileSubstrate/DynamicLibraries/
```

### 4. Собрать

```bash
python3 scripts/build_deb.py
```

Результат: `releases/me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb`

</details>

---

## 🗑 Удаление

```bash
dpkg -r me.autotouch.autotouch.ios8
rm -f /var/jb/Library/MobileSubstrate/DynamicLibraries/crackATT.*
killall -9 SpringBoard
```

---

## ❓ Известные проблемы

| Симптом | Решение |
|---------|---------|
| `lzma error: file format not recognized` | Используйте `.deb` из [Releases](releases/) этого репо |
| `Unknown TAR header type` | Перекачайте файл — .deb повреждён |
| Ограничения остались | Respring; затем `install-patch-only.sh` |
| Не rootless | Нужен пакет `arm64` с путями `/var/jb/` |

---

## 📄 Лицензия

[MIT](LICENSE) © 2026 [smartmaster35rus-dev](https://github.com/smartmaster35rus-dev)
