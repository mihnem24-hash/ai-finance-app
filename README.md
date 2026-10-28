# AI & Финансы 📊🤖

Мобильное приложение на **Python + Flet** с полностью русскоязычным интерфейсом
(Material Design 3, карточки, светлая/тёмная тема).

## Возможности

### 💰 Финансовый блок
- **Курсы валют к рублю** — данные ЦБ РФ (USD, EUR, CNY, GBP, JPY, CHF, TRY, KZT и др.),
  номинал, изменение к прошлому дню и подсветка роста/падения.
- **Мировые индексы** — Индекс МосБиржи и РТС (API МосБиржи), S&P 500, NASDAQ,
  DAX, FTSE 100, Nikkei 225, Hang Seng, Shanghai Composite.
- **Поиск** по названию/коду, обновление по кнопке, офлайн-режим с резервными данными.

### 🏆 AI Leaderboard
Рейтинг генеративных моделей в пяти категориях (переключаются чипами):
- 🎬 генерация **видео**;
- 🖼 генерация **изображений**;
- 🎧 **аудио и музыка**;
- 💬 **текст и рассуждения**;
- 🧩 **мультимодальные** модели.

Для каждой модели: место, разработчик, балл, прогресс относительно лидера,
описание и теги. Медали 🥇🥈🥉 выделяются для топ-3.

### ℹ️ О программе
Источники данных, версия и дисклеймер.

## Структура проекта

```
MyAiProject/
├── main.py                     # интерфейс приложения (Flet)
├── core/
│   ├── fetchers.py             # загрузка котировок и рейтинга (только stdlib)
│   ├── leaderboard.py          # данные AI Leaderboard (обновляются вручную)
│   └── market_fallback.py      # офлайн-заглушки котировок
├── tools/
│   └── make_icon.py            # генерация assets/icon.png (без зависимостей)
├── assets/
│   └── icon.png                # иконка приложения 1024×1024
├── .github/workflows/
│   └── build-apk.yml           # сборка .apk через GitHub Actions
├── requirements.txt
├── pyproject.toml              # метаданные для flet build
└── README.md
```

## Локальный запуск (отладка)

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Приложение откроется в окне настольного приложения (или в браузере при
`flet run main.py -w`).

## Сборка APK через GitHub Actions (рекомендуется)

1. Создайте репозиторий на GitHub и загрузите проект:
   ```bash
   git init
   git add .
   git commit -m "AI & Финансы: первая версия"
   git branch -M main
   git remote add origin https://github.com/<ваш-логин>/<репозиторий>.git
   git push -u origin main
   ```
2. Откройте вкладку **Actions** → выберите **«Сборка Android APK»** → **Run workflow**.
3. После завершения (≈5–10 минут) откройте сборку → раздел **Artifacts** →
   скачайте `ai-finance-apk` (внутри готовый `AI-Finance-<ветка>.apk`).
4. Чтобы получить постоянную ссылку на APK, создайте тег:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   APK автоматически прикрепится к релизу на странице Releases.

## Локальная упаковка в APK

Требования: **Python 3.10+**, **Flutter SDK** (stable), **JDK 17**, **Android SDK**.

```bash
pip install -r requirements.txt
python -I tools/make_icon.py assets/icon.png   # иконка приложения
python -m flet build apk
```

Готовый файл появится в `build/apk/app-debug.apk`
(для магазина используйте `flet build apk --split-per-abi` или `flet build aab`).

Другие платформы: `flet build windows`, `flet build macos`, `flet build linux`,
`flet build web`, `flet build ios`.

## Обновление данных

| Что | Где |
| --- | --- |
| Рейтинг AI-моделей | `core/leaderboard.py` — правьте `score`, состав списков и теги |
| Офлайн-курсы валют | `core/market_fallback.py` |
| Валюты для показа | `CURRENCY_ORDER` в `core/fetchers.py` |
| Мировые индексы | `STOOQ_SYMBOLS` в `core/fetchers.py` |
| «Живой» источник рейтинга | `REMOTE_LEADERBOARD_URL` в `core/fetchers.py` (JSON: `{"categories": {...}}`) |

## Источники данных

- Курсы валют — [ЦБ РФ](https://www.cbr.ru/scripts/XML_daily.asp) (XML, обновление раз в сутки).
- Индексы России — [ISS API Московской биржи](https://iss.moex.com/).
- Мировые индексы — [Stooq](https://stooq.com/) (CSV, без ключа доступа).
- Рейтинги AI-моделей — снимок публичных оценок сообщества
  (LMArena, Artificial Analysis, VBench и др.), обновляется вручную.

> ⚠️ Данные носят информационный характер и не являются инвестиционной рекомендацией.
