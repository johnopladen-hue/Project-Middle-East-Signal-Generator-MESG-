from keel_proof import ping


def test_ping():
    assert ping() == "definitely not ok"
