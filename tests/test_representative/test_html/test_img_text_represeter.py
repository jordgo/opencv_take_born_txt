import dataclasses

import pytest

import models.repo_documents as repo_doc
import representative.html.html_img_texts_representer as img_texts_representer
import saving.save_to_dir as save_to_dir
from definition import ROOT_DIR

default_obj = repo_doc.ImgTextsDocument('video_name', "00:05:55", [], [],"frame_path", "00:06:66")
obj1 = dataclasses.replace(default_obj, header=["Some", "Title1"], body=[
    [{"key": "keyStr1", "value": "valueStr1"},
     {"key": "keyStr2", "value": "valueStr2"},
     {"key": "keyStr3", "value": "valueStr2"},
     ],
    [{"key": "keyStr21", "value": "valueStr21"},
     {"key": "keyStr22", "value": "valueStr22"},
     {"key": "keyStr23", "value": "valueStr22"},
     ]
])

@pytest.mark.parametrize("data, exp", [
    (obj1, ""),
    # ()
])
def test_generate(data, exp, config):
    o = img_texts_representer.ImgTextsRepresnter(data)
    html = o.generate()
    print(html.response)
    path = ROOT_DIR + "/tests/results/img_text_representer.html"
    save_to_dir.save_to_file(path, str(html.response), False)

    assert True