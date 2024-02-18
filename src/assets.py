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
        case 'input':
            asset.setdefault('input_y', int(type_info[1]))
            asset.setdefault('input_x', int(type_info[2]))
            asset.setdefault('max_len', int(type_info[3]))
            asset.setdefault('default', str.join('', type_info[4:]))

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


class TextInput(Text):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL,
                 labelattr=curses.A_REVERSE,
                 filterfunc=str.isprintable,
                 trigger=None ):
        super().__init__(conteiner, assetfile, attr)
        self.filter = filterfunc
        self.labelattr = labelattr
        self.original_attr = self.attr
        self.original_labelattr = self.labelattr
        self.current_content = self.asset['default']
        self.trigger = trigger

    def __call__(self):
        """
        Initiate insertion mode, the filter only allow the right caracters to 
        be inserted, the user can let the input empty to insert the default value
        """
        old_labelattr = self.labelattr

        # set terminal attributes
        self.chlabelattr(self.attr)
        curses.curs_set(2)
        self.win.nodelay(True)

        self.win.move(*self.get_cursor_relyx())
        while True:
            # get input ch
            try:
                key = self.win.get_wch()
            except:
                key = None

            match (key):
                # pass
                case None: continue
                # check for a enter
                case '\n': break
                # check for a backspace
                case 'KEY_BACKSPACE' | '\b' | '\x7f' | '^?':
                    if self.current_content != '':
                        # delete last character
                        self.current_content = self.current_content[:-1]

                        self.win.addch(*self.get_cursor_relyx(), ' ')
                        self.win.move(*self.get_cursor_relyx())
                case _:
                    if len(self.current_content) >= self.asset['max_len']:
                        continue

                    if self.filter(self.current_content + str(key)):
                        self.win.addch(key, self.labelattr)
                        self.current_content += key

        # verify if was given a input
        if self.current_content == '' and self.asset['default'] != '':
            self.current_content = self.asset['default']
        
        # return terminal to prev state
        self.chlabelattr(old_labelattr, True)
        self.win.nodelay(False)
        curses.curs_set(0)

        self.trigger(self.current_content)

    def chattr(self, attr, autorefresh=True):
        self.attr = attr
        super().draw(autorefresh)

    def chlabelattr(self, attr, autorefresh=True):
        """
        Change the of the label attribute and redraw the window, but do not refresh.

        autorefresh: bool, refresh the window so you dont need to 
        refresh yourself using the conteiner window, default is False.
        For optimization is recomended to make all changes in the windows then refresh.
        """
        self.labelattr = attr
        self.draw(autorefresh)

    def draw(self, autorefresh=False):
        # draw the base asset
        super().draw(autorefresh)

        try:
            # draw label content
            self.win.addstr(
                self.asset['input_y'],
                self.asset['input_x'],
                self.current_content,
                self.labelattr
            )
        except:   
            # cursor exceeds the windows size
            self.win.move(self.asset['input_y'], self.asset['input_y'])

        # auto refresh
        if autorefresh:
            self.win.refresh()

    def get_cursor_relyx(self) -> tuple[int, int]:
        y = self.asset['input_y']
        x = len(self.current_content) + self.asset['input_x']
        return y, x

    def get_cursor_absyx(self) -> tuple[int, int]:
        y, x = self.get_cursor_relyx()
        y += self.asset['win_y']
        x += self.asset['win_x']
        return y, x

    def reset_attr(self, autorefresh=True):
        self.chattr(self.original_attr, False)
        self.chlabelattr(self.original_labelattr, autorefresh)


class Conteiner(Text):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        self.components_list = []

    def draw(self, autorefresh=False):
        super().draw(autorefresh)

        for component in self.components_list:
            component.draw(autorefresh)

        if autorefresh:
            self.win.refresh()

    def generate_components(self):
        """
        A prototype for a conteiner generate_components method.
        """
        pass
    
    def set_first_n_components_to_visible(self, n: int):
        index = 0
        for component in self.components_list:
            if index < n:
                component.visible = True
                component.draw(True)
            else:
                component.clear(True)
            index += 1
