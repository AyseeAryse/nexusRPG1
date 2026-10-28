"""Geographic hierarchy regression tests; no real AI service required."""
import copy
import importlib
from types import SimpleNamespace
from unittest.mock import Mock

from src.core.engine import GameEngine, GameState
from src.systems.mechanics import TravelSystem
from src.world.galaxy import GalaxyMap
from src.world.location import merge_location, normalize_location


def test_default_location_is_earth_japan_tokyo():
    location = GameState().current_location
    assert location == {
        "planet": "Земля",
        "country": "Япония",
        "city": "Нью-Токио",
        "district": "Индустриальный коридор",
        "place": "",
    }


def test_old_save_gains_country_without_losing_fields():
    original = GameState()
    data = original.to_dict()
    legacy_loc = copy.deepcopy(data["current_location"])
    del legacy_loc["country"]
    data["current_location"] = legacy_loc

    restored = GameState.from_dict(data)
    assert restored.current_location["country"] == "Япония"
    assert {key: restored.current_location[key] for key in legacy_loc} == legacy_loc
    assert restored.to_dict()["current_location"]["country"] == "Япония"


def test_old_mars_save_does_not_inherit_japan():
    state = GameState()
    data = state.to_dict()
    data["current_location"] = {
        "planet": "Марс", "city": "Новый Бостон",
        "district": "Окружное кольцо", "place": "",
    }
    restored = GameState.from_dict(data)
    assert restored.current_location["country"] is None
    assert restored.current_location["city"] == "Новый Бостон"


def test_earth_other_city_is_unknown_without_approved_mapping():
    loc = normalize_location({
        "planet": "Земля", "city": "Нью-Йорк",
        "district": "Порт Бруклин", "place": "",
    })
    assert loc["country"] is None


def test_tokyo_aliases_override_inconsistent_country():
    for city in ("Токио", "Нью-Токио"):
        loc = normalize_location({"planet": "Земля", "city": city, "country": "Ошибка"})
        assert loc["country"] == "Япония"


def test_partial_updates_preserve_country_but_moving_city_clears_it():
    original = GameState().current_location
    same_city = merge_location(original, {"district": "Корпоративный квартал"})
    assert same_city["country"] == "Япония"
    assert original["district"] == "Индустриальный коридор"  # no mutation
    another_city = merge_location(same_city, {"city": "Нью-Йорк", "district": "Порт Бруклин"})
    assert another_city["country"] is None
    mars = merge_location(original, {"planet": "Марс", "city": "Новый Бостон"})
    assert mars["country"] is None
    back = merge_location(mars, {"planet": "Земля", "city": "Нью-Токио"})
    assert back["country"] == "Япония"


def test_starting_origins_keep_geographic_hierarchy():
    engine = GameEngine.__new__(GameEngine)
    engine.state = GameState()
    engine._set_starting_location("EARTH")
    assert engine.state.current_location["country"] == "Япония"
    engine._set_starting_location("MARS")
    assert engine.state.current_location["country"] is None


def test_mechanical_district_move_keeps_country(monkeypatch):
    monkeypatch.setattr("src.systems.mechanics.random.random", lambda: 1.0)
    loc = GameState().current_location
    result = TravelSystem.travel_local(loc, "Корпоративный квартал", GalaxyMap())
    assert result["success"]
    assert result["new_location"]["country"] == "Япония"


def test_mechanical_intercity_move_does_not_retain_tokyo_country(monkeypatch):
    monkeypatch.setattr("src.systems.mechanics.random.random", lambda: 1.0)
    result = TravelSystem.travel_local(GameState().current_location, "Порт Бруклин", GalaxyMap())
    assert result["success"]
    assert result["new_location"]["city"] == "Нью-Йорк"
    assert result["new_location"]["country"] is None


def test_mechanical_interplanetary_move_resets_and_restores_country(monkeypatch):
    monkeypatch.setattr("src.systems.mechanics.random.random", lambda: 1.0)
    ship = SimpleNamespace(ship={"fuel": 100, "speed": 5})
    char = {"credits": 0}
    outward = TravelSystem.travel_interplanetary(GameState().current_location, "Марс", ship, char)
    assert outward["success"]
    assert outward["new_location"]["country"] is None
    home = TravelSystem.travel_interplanetary(outward["new_location"], "Земля", ship, char)
    assert home["success"]
    assert home["new_location"]["country"] == "Япония"


def test_map_api_city_move_returns_correct_country(monkeypatch):
    server = importlib.import_module("src.server.app")
    state = GameState()
    fake = SimpleNamespace(
        state=state, galaxy_map=GalaxyMap(), _advance_time=Mock()
    )
    fake.state.npc_registry.generate_npc = Mock(return_value={"name": "Тест"})
    monkeypatch.setattr(server, "engine", fake)
    monkeypatch.setattr("random.random", lambda: 1.0)

    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        response = client.post(
            "/api/map/move",
            json={"city": "Нью-Йорк", "district": "Порт Бруклин"}
        )
    assert response.status_code == 200
    assert response.get_json()["location"]["country"] is None
    assert fake.state.current_location["country"] is None


def test_map_api_planet_move_returns_correct_country(monkeypatch):
    server = importlib.import_module("src.server.app")
    state = GameState()
    fake = SimpleNamespace(
        state=state, galaxy_map=GalaxyMap(), _advance_time=Mock()
    )
    fake.state.npc_registry.generate_npc = Mock(return_value={"name": "Тест"})
    monkeypatch.setattr(server, "engine", fake)
    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        response = client.post("/api/map/move", json={"planet": "Марс"})
    assert response.status_code == 200
    assert response.get_json()["location"]["country"] is None
    assert fake.state.current_location["country"] is None
