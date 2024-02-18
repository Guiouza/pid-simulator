from curses import wrapper, _CursesWindow
import curses
# internal libs
from assets import *


# title
TITLE_ASSET = './assets/title.txt'


class Gui():
    def __init__(self, stdscr):
        self.title = Text(stdscr, TITLE_ASSET, curses.A_REVERSE)

    def draw(self, autorefresh=False):
        self.title.draw(autorefresh)


def main(stdscr: _CursesWindow):
    curses.curs_set(0)
    curses.noecho()

    gui = Gui(stdscr)
    gui.draw()
    stdscr.getch()


if __name__ == '__main__':
    wrapper(main)