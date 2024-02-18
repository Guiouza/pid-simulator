def read_asset(fname) -> dict[str: str|int]:
    asset = {}
    # read asset file
    with open(fname) as file:
        nlines, ncols, win_y, win_x, box, text_y, text_x, *type_info = file.readline().split()
        asset['text'] = file.read()

    # extract base info
    asset['nlines'] = int(nlines)
    asset['ncols'] = int(ncols)
    asset['win_y'] = int(win_y)
    asset['win_x'] = int(win_x)
    asset['draw_box'] = bool(int(box))
    asset['text_y'] = int(text_y)
    asset['text_x'] = int(text_x)
    asset['type'] = type_info[0]

    # extract type expecifications
    match (type_info[0]):
        case 'text':
            pass

    return asset