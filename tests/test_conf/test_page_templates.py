import pytest

# from models.page_templates import get_page_section
# from models.data_classes import PageSection
#
#
# @pytest.mark.parametrize("template_name, block_name, h_screen, w_screen, exp",
#                          [("BODY_WITH_LEFT_PAYLOAD", "left_side", 1080, 1920, PageSection(100, 120, 520, 840)),
#                           ("BODY_WITH_LEFT_PAYLOAD", "header", 1080, 1920, PageSection(0, 0, 1920, 120)),
#                           ("BODY_WITH_LEFT_PAYLOAD", "footer", 1080, 1920, PageSection(0, 960, 1920, 120)),
#                           ("BODY_WITH_LEFT_PAYLOAD", "right_border", 1080, 1920, PageSection(0, 0, 100, 1080)),
#                           ("BODY_WITH_LEFT_PAYLOAD", "left_border", 1080, 1920, PageSection(1820, 0, 100, 1080)),
#                           ])
# def test_get_page_section(template_name, block_name, h_screen, w_screen, exp):
#     page_shape = get_page_section(template_name, block_name, h_screen, w_screen)
#     assert page_shape == exp
