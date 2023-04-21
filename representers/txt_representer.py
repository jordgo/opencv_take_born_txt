SPACE_WIDTH_PX = 10


def _spaces(current_x: int, prev_offset: int = 0) -> str:
    offset = current_x - prev_offset
    n_spaces = offset if SPACE_WIDTH_PX == 0 else int(offset / SPACE_WIDTH_PX)
    # print("offset", current_x, prev_offset, offset)
    return "".join(" " for _ in range(n_spaces))


def _sorting_line(line):
    sorted_line_by_x = sorted(line, key=lambda obj: obj.x)
    line_txt = ''
    prev_offset = 0
    for o in sorted_line_by_x:
        spaces = _spaces(o.x, prev_offset)
        line_txt = line_txt + spaces + " " + o.word
        prev_offset = o.x + o.w
    return line_txt


def _get_lines_txt(data) -> str:
    sorted_by_y = sorted(data, key=lambda obj: obj.y)

    prev_y = 0
    prev_h = 0
    lines = []
    line = []
    for o in sorted_by_y:
        is_new_line = o.y - prev_y > prev_h * 0.8 # NEW_LINE_THRESHOLD_PX
        prev_y = o.y
        prev_h = o.h
        if is_new_line:
            if line:
                line_txt = _sorting_line(line)
                lines.append(line_txt)
            line = [o]
        else:
            line.append(o)
    if line:
        lines.append(_sorting_line(line))
    return ''.join(["\n" + l for l in lines])