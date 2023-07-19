from app.calculations import add


def test_add():
    print("Testing add function")
    sum = add(5,3)
    assert sum == 8