from app.signals import classify_event_type, severity_for


def test_classifies_coup_language():
    assert classify_event_type("Officers announced a coup on state TV") == "coup"


def test_classifies_natural_disaster():
    assert classify_event_type("A magnitude 6.1 earthquake struck the coastal region") == "natural_disaster"


def test_returns_none_for_unrelated_text():
    assert classify_event_type("The central bank held interest rates steady") is None


def test_high_severity_events():
    for event_type in ("coup", "assassination", "military_event", "uprising"):
        assert severity_for(event_type) == "high"


def test_no_event_has_no_severity():
    assert severity_for(None) == "none"


def test_other_taxonomy_events_are_medium_severity():
    assert severity_for("natural_disaster") == "medium"
