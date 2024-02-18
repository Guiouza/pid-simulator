from curses import wrapper, _CursesWindow
import curses
# internal libs
from assets import *
from pid import Pid


# title
TITLE_ASSET = './assets/title.txt'

# simulaiton_setup -> conteiner
SIMULATION_SETUP_ASSET = './assets/setup/conteiner.txt'
# simulaiton_setup -> inputs
NUM_PIDS_ASSET = './assets/setup/num_pids.txt'

# Simulation Setting
MAX_NPIDS = 9


class SimulationSetup(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL):
        super().__init__(conteiner, assetfile, attr)
        self.create_win()

    def generate_components(self, numpids_trigger, start_triiger):
        self.components_list = [
            TextInput(self.win, NUM_PIDS_ASSET, trigger=numpids_trigger)
        ]


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
        self.simu_setup_conteiner = SimulationSetup(stdscr, SIMULATION_SETUP_ASSET)
        self.pid_manager = PidManager(MAX_NPIDS)

        self.simu_setup_conteiner.generate_components(
            self.set_num_of_pids, # num pids trigger
        )

    def draw(self, autorefresh=False):
        self.title.draw(autorefresh)
    
    def set_num_of_pids(self, npids_str: str):
        """Num of PIDs trigger."""
        npids = int(npids_str)


def main(stdscr: _CursesWindow):
    curses.curs_set(0)
    curses.noecho()

    gui = Gui(stdscr)
    gui.draw()
    stdscr.getch()


if __name__ == '__main__':
    wrapper(main)