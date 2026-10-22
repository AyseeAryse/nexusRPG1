# Тестирование NexusRPG1

## Локально (Python 3.11+)

```bash
python -m pip install -r requirements.txt
python scripts/validate_install.py
python -m pytest -q
```

Для быстрой проверки без установки всех опциональных AI/сборочных зависимостей:

```bash
python -m pip install Flask requests pytest
python scripts/validate_install.py
python -m pytest -q
```

## Что проверяют тесты

- `test_smoke.py`: импорты и настройки существующих подсистем.
- `test_engine_basic.py`: базовая логика, кубики и состояние движка.
- `test_world_basic.py`: карта и компоненты процедурного мира.
- `test_server_smoke.py`: импорт веб-сервера, корневая страница и работа `/health`.
- `test_repo_integrity.py`: структура репозитория, переход на `game_data/active/`, чтение данных, предотвращение обхода каталогов сохранений.

`scripts/validate_install.py` дополнительно проверяет наличие файлов, валидный синтаксис Python, JSON и отсутствие дублей имен активных файлов.

## GitHub CI

`.github/workflows/python-checks.yml` запускает базовые проверки на Pull Request и push в `main`, без реального вызова AI.

## Проверка запуска

```bash
python -m src.server.app
```

Ожидается локальный сервер на `http://127.0.0.1:8080`; `GET /health` должен отвечать `200 OK` с JSON `{"status":"ok"}`.

## Ограничения покрытия

Зелёные тесты **не** доказывают корректность генерации нарратива, полноту квестовой логики, правильность всех JSON-правил, отсутствие гонок между пользователями и работоспособность Windows PyInstaller. См. [технический аудит](audits/REPOSITORY_AUDIT_2026-10-22.md).

Перед обновлением версии делайте резервную копию локальных `saves/` и `database/`.
