import dominate
from dominate.tags import *

import representative.report_representer as r_representer
import models.report_response as r_resp
import models.repo_documents as repo_doc
import saving


class ImgTextsRepresnter(r_representer.HTMLReportRepresenter):
    def __init__(self, data: repo_doc.ImgTextsDocument):
        self.data: repo_doc.ImgTextsDocument = data

    def generate(self) -> r_resp.ReportResponse:
        title_data = ' '.join(t['text'] for t in self.data.header)
        table_alignment = 'margin-left:auto; margin-right:auto; '
        table_style = f'width:50%; min-width:700px; {table_alignment} font-size:18px;'
        td_style = 'padding:10px;' # padding-bottom:10px;'
        td_value_style = 'padding:10px; width:30%;'
        doc = dominate.document(title='Video texts')

        # with doc.head:
            # link(rel='stylesheet', href='style.css')
            # script(type='text/javascript', src='script.js')

        def empty_tr():
            with tr():
                td()
                td()

        def empty_table():
            with table():
                empty_tr()

        with doc.body:
            attr(cls='body', style='background-color: #EEEEEE; font-family: Roboto, sans-serif;')
            br()
            with table(style='width:250px; font-size:15px;'):
                with tr():
                    td("File name:")
                    td(self.data.video_name)
                with tr():
                    td("Frame time:")
                    td(self.data.frame_time)
            br()
            empty_table()

            with div(id='content'):
                with table(style=table_alignment):
                    with tr():
                        td().add(div(title_data, _id='title', style='text-align:center; font-size:25px;'))
                        td()

                empty_table()

                with div(cls="shapes"):
                    for shape in self.data.body:
                        br()
                        with table(style=table_style).add(tbody()):
                            for shape_line in shape:
                                with tr(cls="shape_line"):
                                    td(shape_line['key']['text'], cls="shape_line_key", style=td_style)
                                    td(shape_line['value']['text'], cls="shape_line_value", style=td_value_style)


        return r_resp.ReportResponse(doc)

