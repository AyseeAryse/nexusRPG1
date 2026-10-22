"""Regression tests for repository consolidation (no AI backend required)."""
from pathlib import Path

from src.ai.knowledge_base import KnowledgeBase
from src.content.v4_legacy import _load_json
from src.core.engine import GameEngine


ROOT = Path(__file__).resolve().parents[1]


def test_active_content_is_loaded_from_new_layout():
    kb = KnowledgeBase(str(ROOT / "game_data" / "active"))
    assert len(kb.files) >= 70
    assert kb.get_file("CHARACTER_ORIGINS.json") is not None
    assert kb.get_file("PROGRESSION.json") is not None


def test_legacy_lifepath_reader_uses_active_content():
    assert _load_json("CHARACTER_ORIGINS.json")
    assert _load_json("CHARACTER_LIFEPATH_V3_MASSIVE_PART1.json")


def test_save_paths_reject_traversal_and_reserved_names(tmp_path):
    engine = GameEngine.__new__(GameEngine)
    engine.saves_dir = str(tmp_path)
    for slot in ("../outside", "..", ".", "/tmp/pwn", "a/b", "a\\b", "CON", "COM1", None, 42):
        assert engine._save_path(slot) is None
        assert "error" in engine.load_game(slot)
        assert "error" in engine.delete_save(slot)


def test_unicode_and_regular_save_slot_names(tmp_path):
    engine = GameEngine.__new__(GameEngine)
    engine.saves_dir = str(tmp_path)
    for slot in ("save_123", "Сохранение 1", "slot.2"):
        path = engine._save_path(slot)
        assert path is not None
        assert Path(path).parent == tmp_path


def test_repository_is_not_shipping_parallel_root_engine():
    for filename in ("game_engine.py", "config.py", "ai_connector.py", "RPG-main"):
        assert not (ROOT / filename).exists()


def test_server_has_local_healthcheck():
    from src.server.app import app
    with app.test_client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
