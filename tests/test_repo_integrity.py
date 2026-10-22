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


def test_normal_turn_uses_shared_immediate_result():
    from unittest.mock import Mock
    engine = GameEngine.__new__(GameEngine)
    engine._prepare_player_action = Mock(return_value={"immediate": {"combat_started": True}})
    assert engine.process_player_action("attack") == {"combat_started": True}
    engine._prepare_player_action.assert_called_once_with("attack")


def test_streaming_turn_uses_same_pre_and_post_ai_pipeline(monkeypatch):
    import importlib
    from unittest.mock import Mock

    server = importlib.import_module("src.server.app")
    fake = Mock()
    fake._prepare_player_action.return_value = {
        "mechanical_result": None,
        "mech_action_result": None,
        "subsystem_result": None,
        "world_events": [],
        "triggered_consequences": [],
        "income_result": None,
    }
    fake.state.conversation_history = []
    fake.state.world_context = {}
    fake.ai.generate_stream.return_value = iter(["Привет"])
    fake._parse_ai_response.return_value = {"narrative": "Привет", "state_changes": {}}
    fake._finalize_player_action.return_value = {"level_up": None, "defeat": None}
    fake._get_client_state.return_value = {}

    monkeypatch.setattr(server, "engine", fake)
    with server.app.test_client() as client:
        response = client.post("/api/action/stream", json={"action": "осмотреться"})
        assert response.status_code == 200
        text = response.get_data(as_text=True)
    assert '"type": "done"' in text
    fake._prepare_player_action.assert_called_once_with("осмотреться")
    fake._finalize_player_action.assert_called_once()
    fake.state.world_sim.tick.assert_not_called()
