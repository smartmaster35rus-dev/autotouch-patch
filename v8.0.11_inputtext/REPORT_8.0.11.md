# AutoTouch 8.0.11 (inputtext) — снятие лицензионного таймаута (~2 мин)

## Гибрид (после respring — Licensed + auto-launch)

Только бинарный патч **ATTweak** не хватает: после respring остаётся **Unlicensed** и алерт
*License is needed to launch script automatically* — проверки лицензии и UI в **crackATT**.

1. Собрать `crackATT` для 8.0.11: GitHub Actions → artifact `crackATT-8011.dylib`, или локально `cd tweak8011 && make`.
2. Положить dylib в `v8.0.11_inputtext/patch/crackATT.dylib`.
3. Собрать гибридный `.deb`:

```bash
python scripts/build_hybrid_release_8011.py
```

Пакет: `8.0.11-v1-hybrid` — пропатченный **ATTweak.dylib** + **crackATT.dylib** + `postinst` (`ldrestart`).

---

## Итог (только таймер, без crackATT)

Собран пропатченный пакет:

```
me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb   (15 583 286 байт)
SHA-256: 90aab41cf21ede441259655ee8b505249aa8a8b37be773affe61e4ea54f1eee4
```

Патч — **size-preserving** (размер `ATTweak.dylib` не меняется), изменено ровно **16 байт** в 4 местах.
В пакете заменён только **один** файл, всё остальное (498 файлов) — байт-в-байт как в оригинале.

---

## Что пропатчено

Файл: `data/var/jb/Library/MobileSubstrate/DynamicLibraries/ATTweak.dylib`
(FAT: arm64 + arm64e, 49 108 848 байт, оба слайса).

| Слайс | Метод | File-offset патча | Исходный пролог |
|-------|------|-------------------|-----------------|
| arm64  | `-[CommandServer suYYKTj6MHk]` | `0xF8744C` | `stp x20,x19,[sp,#-0x20]! …` |
| arm64  | `-[Spring suYYKTj6MHk]`        | `0xF8A4C8` | то же |
| arm64e | `-[CommandServer suYYKTj6MHk]` | `0x26F9580` | то же |
| arm64e | `-[Spring suYYKTj6MHk]`        | `0x26FC9A8` | то же |

В каждом месте первые 4 байта функции заменены на `RET`:
`f4 4f be a9 …` → **`c0 03 5f d6`** (`ret`).

## Почему это работает

`suYYKTj6MHk` — обфусцированный аналог `setupTimer` из версии 8.5.5
(в 8.5.5 он назывался `setupTimer_240358` / `setupTimer_167855`). Тело функции:

```
mov  x8, #0x405e000000000000     ; 120.0 (double)
fmov d0, x8
mov  x2, x19                     ; target = self
...
bl   0xfd50a0                    ; [NSTimer scheduledTimerWithTimeInterval:...]
str  x0, [x19, #ivar]            ; сохранить таймер
```

Т.е. функция создаёт повторяющийся `NSTimer` с интервалом **120.0 секунд**, колбэк которого —
`licenseLimitTimeout` (через ~2 минуты скрипт/воспроизведение принудительно останавливается и
показывается алерт о лицензии). Проставив в начале функции `RET`, мы **не даём таймеру создаться** —
таймаут никогда не наступает. Механизм идентичен проверенному бинарному патчу для 8.5.5.

Проверено: логики таймаута в самом `AutoTouch.app` нет — в бинаре приложения отсутствуют строки
`licenseLimitTimeout` / `setupTimer` / `getLicense` и нет сигнатуры таймера 120.0. Вся логика в `ATTweak.dylib`.

## Как воспроизвести

```bash
# 1. распаковать оригинал
python scripts/extract_deb.py me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64.deb extracted

# 2. запатчить dylib (паттерн-скан по обоим слайсам)
python patch_attweak_8011.py \
  "extracted/data/var/jb/Library/MobileSubstrate/DynamicLibraries/ATTweak.dylib" \
  "ATTweak.patched.dylib"

# 3. положить обратно
cp ATTweak.patched.dylib \
  "extracted/data/var/jb/Library/MobileSubstrate/DynamicLibraries/ATTweak.dylib"

# 4. собрать deb (LZMA dict 64 МБ — как у оригинала)
python build_deb_lzma64.py extracted me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb

# 5. проверить (сравнение payload с оригиналом)
python verify_build.py
```

## Установка на устройстве (rootless, /var/jb)

```bash
scp me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb root@DEVICE:/var/mobile/
ssh root@DEVICE
dpkg -i /var/mobile/me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb
respring          # или перезагрузка backboardd/springboard
```

Примечания:
- Пакет **rootless**: всё внутри `/var/jb`, зависимости `firmware (>= 11.0)` и `ellekit`.
- Версия в `control` оставлена `8.0.11` — пакет ставится «поверх» штатного как drop-in.
- Правка байт делает встроенную подпись кода `ATTweak.dylib` недействительной. На rootless-джейлбрейке
  (ellekit/ElleKit) подпись для `/var/jb` обычно не проверяется, и в 8.5.5-патче тот же приём работал
  без переподписи. Если на конкретном устройстве твик не загрузится — на устройстве переподпишите:
  `ldid -S /var/jb/Library/MobileSubstrate/DynamicLibraries/ATTweak.dylib` (ldid должен быть установлен).

---

## Проверка сборки (observed)

- `orig files: 498` / `patched files: 498`; only-in списки пусты.
- `differing files: ['data/var/jb/Library/MobileSubstrate/DynamicLibraries/ATTweak.dylib']`.
- `dylib sizes: 49108848 49108848`; `dylib changed bytes: 16` (см. offsets выше).
- `control files identical: True`.

## Файлы

| Файл | Назначение |
|------|-----------|
| `me.autotouch.autotouch.ios8.inputtext_8.0.11_iphoneos-arm64_patched.deb` | готовый пропатченный пакет |
| `patch_attweak_8011.py` | патчер (скан 4 мест + RET) |
| `build_deb_lzma64.py` | сборка deb с LZMA1 64 МБ (как оригинал) |
| `verify_build.py` | сверка payload оригинал/патч |
| `ATTweak.dylib.orig` | резервная копия штатного dylib |
| `objc_dump.py`, `disasm.py`, `disasm.txt` | инструменты реверса и дизасм |

## Опционально: crackATT (статус Licensed / UI)

В релизе 8.5.5, кроме бинарного патча, добавлялся Substrate/ElleKit-твик `crackATT.dylib`
(статус Licensed в настройках, ответы «лицензия есть» без сервера, отсутствие pro-алерта).
Для 8.0.11 его имена классов/методов другие (нет `Global_*`, `CommandServer_907239`, `JSEngine`),
поэтому готовый 8.5.5-`crackATT` не подходит. Бинарный патч таймаута от него не зависит.
Если нужен полный «Licensed»-опыт — нужно отдельно пересобрать `crackATT` под 8.0.11
(классы `CommandServer`, `Spring`, `JSExtension`; методы `suYYKTj6MHk`, `licenseLimitTimeout`,
`licenseCoolDown`, `getLicense`) через Theos (сборочный workflow есть в `.github/workflows/build.yml`).
