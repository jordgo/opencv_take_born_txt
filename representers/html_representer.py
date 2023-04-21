

HTML_RESIZE_COEFF = 1.5


def _create_full_html(body: str) -> str:
    resp = f"""<!DOCTYPE html>
            <html>
              <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="background-color: #EEEEEE;">
                <div style="width:1000px; height: 600px">
                    {body}
                </div>
            </body>
          </html>
          """
    return resp


def create_html(data, is_full=True) -> str:
    body = ""
    for obj in data:
        ox, oy, w, h, text = obj
        x = int(ox / HTML_RESIZE_COEFF)
        y = int(oy / HTML_RESIZE_COEFF)
        font_size = 0
        pre_font_size = h / 2
        if pre_font_size < 11:
            font_size = 10
        elif pre_font_size < 15:
            font_size = 12
        else:
            font_size = 14

        div = f"""<div style="position: absolute; font-size:{int(font_size)}px; width:{w}px; height:{h}px; left:{x}px; top:{y}px;"> {text} </div>"""
        body = body + div
    html = _create_full_html(body) if is_full else body
    return html
