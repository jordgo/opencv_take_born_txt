import repositories.img_texts_repository as repo


def test_insert_one(db_session, config):
    r = repo.ImgTextsRepository(db_session, config)
    r.insert_one({"test": "value"})
    resp = r.find_one_by_key({"test": "value"})
    r.delete_one_by_key({"test": "value"})
    assert resp["test"] == "value"
