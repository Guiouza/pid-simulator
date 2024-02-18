from curses import wrapper, _CursesWindow
import curses
# internal libs
from assets import *
from pid import Pid


# title
TITLE_ASSET = './assets/title.txt'


class PidManager():
    def __init__(self, npids):
        self.visible_pids = npids
        self.pid_list = [Pid() for n in range(npids)]
    
    def set_visible_pids(self, npids: int) -> None:
        self.visible_pids = npids
    
    def get_visible_pids(self) -> list[Pid]:
        return self.pid_list[:self.visible_pids]

    def update_pid_pos(self, dt: float) -> None:
        for pid in self.get_visible_pids():
            pid(dt)

    def reset_pid_pos(self):
        for pid in self.pid_list:
            pid.reset()


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