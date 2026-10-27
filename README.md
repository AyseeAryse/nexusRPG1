# NexusRPG

Локальная текстовая научно-фантастическая RPG-песочница с AI Game Master. Этот репозиторий — **[AyseeAryse/nexusRPG1](https://github.com/AyseeAryse/nexusRPG1)**, актуальная рабочая версия проекта.

> **Статус:** проект в разработке. Наличие модулей и JSON-схем **не гарантирует**, что описанная функция полностью реализована и протестирована. В частности, утверждённая концепция магии и академий пока живёт в документации, а не в игровых механиках.

## Установка и запуск

Требуется Python 3.11+.

```bash
git clone https://github.com/AyseeAryse/nexusRPG1.git
cd nexusRPG1
python -m pip install -r requirements.txt
python scripts/validate_install.py
python -m pytest -q
python -m src.server.app
```

Откройте **http://127.0.0.1:8080**. Проверка доступности без подключения к AI: `http://127.0.0.1:8080/health`.

Альтернативная точка запуска: `python launcher.py`. Лаунчер проверяет зависимости и локальную модель; ручная установка Ollama может потребоваться. Для облачного или другого AI-бэкенда настройте параметры в окружении или в игровом интерфейсе.

### Конфигурация

Главный конфигурационный модуль: `src/config.py`. Источники параметров: переменные окружения, необязательный `.env` (при установленном `python-dotenv`) и локальные предпочтения лаунчера `config_data/launcher.json`. Переменные окружения имеют приоритет.

- `AI_BACKEND`: `ollama`, `lmstudio` или `cloud_api`.
- `OLLAMA_URL`, `OLLAMA_MODEL`: локальный backend.
- `LMSTUDIO_URL`, `LMSTUDIO_MODEL`: LM Studio.
- `CLOUD_API_URL`, `CLOUD_API_MODEL`, `CLOUD_API_KEY`: облачный OpenAI-compatible backend.
- `GAME_DATA_DIR`: по умолчанию `game_data/active`.
- `DATABASE_DIR`: по умолчанию `database` (пользовательские данные).
- `SAVES_DIR`: по умолчанию `saves` (не коммитить сохранения).
- `HOST`: по умолчанию `127.0.0.1`; `PORT`: `8080`; `DEBUG`: `false`.

Не открывайте сервер в Интернет: API игры не предназначено для использования как публичный сервис с авторизацией и разграничением аккаунтов. Изменять `HOST=0.0.0.0` следует только осознанно, в доверенной сети с отдельной защитой.

### Структура фактического репозитория

```text
nexusRPG1/
├── launcher.py                 # пользовательский запуск
├── src/
│   ├── config.py               # единственный активный конфиг-модуль
│   ├── ai/                     # AI connector, knowledge base
│   ├── core/engine.py          # GameEngine, GameState, DiceRoller (пока единый файл)
│   ├── content/                # код содержимого и используемые legacy V2–V5 модули
│   ├── systems/                # бой, квесты, NPC/компаньоны, подсистемы, экономика
│   ├── world/                  # карта, симуляция, генерация, NPC
│   └── server/app.py           # Flask API
├── game_data/
│   ├── active/                 # рабочие JSON по категориям
│   │   ├── ai/ character/ economy/ interface/ politics/
│   │   ├── quests/ reference/ social/ systems/ vehicles/ world/
│   └── archive/                # исторические неактивные JSON
├── config_data/                # локальные предпочтения (создаются при использовании)
├── scripts/validate_install.py
├── tests/                      # smoke и регрессионные тесты
├── docs/
│   ├── audits/                 # технические аудиты
│   ├── reference/legacy/       # старые примеры и справочные материалы, не активная база
│   └── worldbuilding/          # решения по ЛОРу, roadmap лора
├── static/css/ static/js/      # фронтенд
├── templates/index.html
├── saves/                      # создаётся при игре, игнорируется Git
└── requirements.txt
```

В каталоге `src/content/v2_legacy.py`, `v3_legacy.py`, `v4_legacy.py`, `v5_legacy.py` ещё находятся **используемые** старые реализации. Это технический долг, а не повод удалять их без доказательств совместимости.

## Документация

- [Текущий технический аудит](docs/audits/REPOSITORY_AUDIT_2026-10-22.md)
- [Архитектура фактического приложения](docs/ARCHITECTURE.md)
- [Тестирование](docs/TESTING.md)
- [Современная Земля: варианты политики, экологии и первый игровой город — ПРОЕКТ](docs/worldbuilding/EARTH_PRESENT_DRAFT.md)
- [Земля, Солнечная система и освоенный Млечный Путь — фокус WB-077](docs/worldbuilding/SOLAR_SYSTEM_AND_GALACTIC_SCOPE.md)
- [Земля как историческая родина — WB-073; детали географии — ПРОЕКТ](docs/worldbuilding/HISTORICAL_ORIGINS_DRAFT.md)
- [Местная экономика, права и независимые общества — ПРЕДЛОЖЕНИЕ](docs/worldbuilding/LOCAL_ECONOMY_AND_RIGHTS_DRAFT.md)
- [Экономическая структура мира — канон WB-075/076](docs/worldbuilding/ECONOMIC_STRUCTURE.md)
- [Экономика и демография поселений — ПРЕДЛОЖЕНИЕ](docs/worldbuilding/ECONOMY_AND_DEMOGRAPHY_DRAFT.md)
- [Локальные общества: 8 глубоких прототипов и план расширения — ПРЕДЛОЖЕНИЕ](docs/worldbuilding/LOCAL_SOCIETIES_DRAFT.md)
- [Культурное происхождение временных государств — ПРЕДЛОЖЕНИЕ](docs/worldbuilding/CULTURAL_GENESIS_DRAFT.md)
- [Истоки и миграции — WB-071](docs/worldbuilding/HISTORY_AND_MIGRATION.md)
- [Политические системы — WB-069](docs/worldbuilding/POLITICAL_SYSTEMS.md)
- [Гражданское общество и корпорации — WB-068](docs/worldbuilding/CIVIL_SOCIETY_AND_ECONOMY.md)
- [Библия мира](docs/worldbuilding/WORLD_BIBLE.md)
- [Принятые решения по ЛОРу](docs/worldbuilding/DECISIONS.md)
- [Генеральный план шести референсов NexusRPG](docs/worldbuilding/LORE_MASTER_ROADMAP.md)
- [Открытые вопросы и возвращение к незавершённым темам](docs/worldbuilding/OPEN_QUESTIONS.md)
- [Тематическая дорожная карта магии и будущей интеграции](docs/worldbuilding/ROADMAP.md)

**Порядок дальнейшей работы (WB-077):** **Земля в приоритете** — первый подробно описанный земной регион, обычная жизнь и социальные институты; далее **околоземное пространство и Луна → Марс → пояс астероидов → внешняя Солнечная система → выбранные межзвёздные системы Млечного Пути**. Весь существующий космический, магический и политический лор WB-036/067–076 **сохраняется**; отдельные рабочие Орсель/Рауден/Меридан/Кельм и A/I-общества остаются **предложениями**, не распределены по планетам. EARTH-PRESENT/SOLAR-SETTLEMENTS открыты. Перед внедрением механик — сверка проверенного кода. [Открытые вопросы](docs/worldbuilding/OPEN_QUESTIONS.md).

## Лицензия

См. [LICENSE](LICENSE).
