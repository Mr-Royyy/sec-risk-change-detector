from sec_risk_detector.cache import DiskCache


def test_disk_cache_round_trips_json_and_text(tmp_path) -> None:
    cache = DiskCache(tmp_path)

    cache.set_json("key-json", {"hello": "world"})
    cache.set_text("key-text", "sample text")

    assert cache.get_json("key-json") == {"hello": "world"}
    assert cache.get_text("key-text") == "sample text"
    assert cache.get_json("missing") is None
    assert cache.get_text("missing") is None
