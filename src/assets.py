from curses import _CursesWindow
import curses


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
        case 'button':
            asset.setdefault('cursor_y', int(type_info[1]))
            asset.setdefault('cursor_x', int(type_info[2]))

    return asset


class Text:
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        self.asset = read_asset(assetfile)
        self.asset['win_y'] += conteiner.getbegyx()[0]
        self.asset['win_x'] += conteiner.getbegyx()[1]

        self.attr = attr
        self.original_attr = attr
        self.visible = True
        self.conteiner = conteiner
        self.win = None
        self.is_visible = False
    
    def chattr(self, attr, autorefresh=True):
        """
        Change the attribute and redraw the window, but do not refresh.

        `autorefresh` refresh the window so you dont need to do yourself using the
        conteiner window. The default is False for optimization purposes, 
        is recomended to make all changes in the windows then refresh.
        """
        self.attr = attr
        self.draw(autorefresh)

    def clear(self, autorefresh=True):
        """
        Clear the window of the asset, to show again just call draw.

        `autorefresh` refresh the window after cleaning. For optimization 
        purposes is set to false by default so you can refresh the entier 
        window at once.
        """
        self.win.clear()

        if autorefresh:
            self.win.refresh()

        self.visible = False

    def create_win(self) -> _CursesWindow:
        """
        Create the window spectified by the asset, this action is not in the 
        __init__ method because you could wan change the windows position 
        original given by the asset.
        """
        self.win = self.conteiner.subwin(
            self.asset['nlines'],
            self.asset['ncols'],
            self.asset['win_y'],
            self.asset['win_x']
        )
        return self.win

    def draw(self, autorefresh=False) -> None:
        """
        Calls window.addstr in the asset text with all the especifications by 
        the asset and the attr. The window it self does not need to be created fist.

        `autorefresh` refresh the window so you dont need to do yourself using the
        conteiner window. The default is False for optimization purposes, 
        is recomended to make all changes in the windows then refresh.
        """
        if self.visible == False:
            self.win.clear()
            return

        if self.win == None:
            self.win = self.create_win()

        if self.asset['draw_box']:
            self.win.box()

        text_y = self.asset['text_y']
        text_x = self.asset['text_x']
        for line in self.asset['text'].splitlines():
            try:
                self.win.addstr(text_y, text_x, line, self.attr)
                text_y += 1
            except:
                # cursor exceeds the windows size
                self.win.move(self.asset['text_y'], self.asset['text_x'])
        
        if autorefresh:
            self.win.refresh()
        self.is_visible = True

    def format_asset(self, **kargs) -> None:
        """
        Format the asset text, example: \n
            if asset is '{a} + {b} = {c}', the call for format_asset(a=1, b=2, c=3)
        will change the asset text to '1 + 2 = 3' the same way str.format funciton does.
        """
        self.asset['text'] = self.asset['text'].format(**kargs)
    
    def reset_attr(self, autorefresh=True):
        self.chattr(self.original_attr, autorefresh)


class Button(Text):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 labelattr=curses.A_NORMAL,
                 trigger=None ):
        super().__init__(conteiner, assetfile, labelattr)
        self.labelattr = self.attr
        self.trigger = trigger
    
    def __call__(self):
        """Call the trigger"""
        return self.trigger()

    def chlabelattr(self, labelattr, autorefresh=True):
        """Change the label attrbute and redraw. Autorefresh will refresh the window."""
        self.labelattr = labelattr
        return super().chattr(labelattr, autorefresh)
    
    def chattr(self, attr, autorefresh=True):
        """Dirivated from Text object, work just as `labelchatrr` method"""
        self.labeltatr = attr
        return super().chattr(attr, autorefresh)

    def get_cursor_relyx(self) -> tuple[int, int]:
        return self.asset['cursor_y'], self.asset['cursor_x']
    
    def get_cursor_absyx(self) -> tuple[int, int]:
        y = self.asset['cursor_y'] + self.asset['win_y']
        x = self.asset['cursor_x'] + self.asset['win_x']
        return y, x

    def reset_attr(self, autorefresh=True):
        self.labelattr = self.original_attr
        return super().reset_attr(autorefresh)
