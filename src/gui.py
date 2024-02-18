from curses import wrapper, _CursesWindow
import threading as td
import curses
# internal libs
from assets import *
from pid import Pid
import filters


# title
TITLE_ASSET = './assets/title.txt'

# simulaiton_setup -> conteiner
SIMULATION_SETUP_ASSET = './assets/setup/conteiner.txt'
# simulaiton_setup -> components
NUM_PIDS_ASSET = './assets/setup/num_pids.txt'
RESTART_ASSET = './assets/setup/start.txt'

# pid setup -> conteiner:
PID_SETUP_CONTEINER_ASSET = './assets/pid_label/conteiner.txt'
# pid setup -> label:
PID_LABEL_ASSET = './assets/pid_label/pid_label.txt'
# pid setup -> inputs:
PID_KP_ASSET = './assets/pid_label/kp.txt'
PID_KD_ASSET = './assets/pid_label/kd.txt'
PID_KI_ASSET = './assets/pid_label/ki.txt'
PID_ICON_ASSET = './assets/pid_label/icon.txt'

# Simulation Setting
MAX_NPIDS = 9


class PidLabel(Conteiner):
    def __init__(self,
                conteiner: _CursesWindow,
                assetfile: str,
                n_id: int,
                pid: Pid,
                attr=curses.A_NORMAL):
        super().__init__(conteiner, assetfile, attr)
        self.format_asset(n_id=n_id)
        self.pid = pid

    def clear(self, autorefresh=True):
        for component in self.components_list:
            component.current_content = component.asset['default']
        return super().clear(autorefresh)

    def generate_components(self):
        """
        Create the labels to setup the linked pid in self.pid
        """
        self.components_list = [
            TextInput(
                self.win,
                PID_KP_ASSET,
                filterfunc=filters.isFloat,
                trigger=self.pid.set_kp
            ),
            TextInput(
                self.win,
                PID_KD_ASSET,
                filterfunc=filters.isFloat,
                trigger=self.pid.set_kd
            ),
            TextInput(
                self.win,
                PID_KI_ASSET,
                filterfunc=filters.isFloat,
                trigger=self.pid.set_ki
            ),
            TextInput(
                self.win,
                PID_ICON_ASSET,
                filterfunc=str.isprintable,
                trigger=self.pid.set_icon,
                labelattr=curses.A_NORMAL
            )
        ]


class PidSetup(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        self.create_win()

    def generate_components(self, pid_list: list[Pid]) -> list[Pid]:
        for n in range(len(pid_list)):
            component = PidLabel(self.win, PID_LABEL_ASSET, n+1, pid_list[n])
            # fix y position
            component.asset['win_y'] += component.asset['nlines'] * n
            component.create_win()
            component.generate_components()
            # apeend to components_list
            self.components_list.append(component)

    def set_first_n_components_to_visible(self, n: int) -> list[PidLabel]:
        super().set_first_n_components_to_visible(n)

        return self.components_list[:n]


class SimulationSetup(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL):
        super().__init__(conteiner, assetfile, attr)
        self.create_win()

    def generate_components(self, numpids_trigger, start_triiger):
        self.components_list = [
            TextInput(self.win, NUM_PIDS_ASSET, trigger=numpids_trigger),
            Button(self.win, RESTART_ASSET, trigger=start_triiger)
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
        self.pid_setup_conteiner = PidSetup(stdscr, PID_SETUP_CONTEINER_ASSET)
        self.simu_setup_conteiner = SimulationSetup(stdscr, SIMULATION_SETUP_ASSET)
        self.pid_manager = PidManager(MAX_NPIDS)

        # generate pid setup input areas: (kp kd ki icon)
        self.pid_setup_conteiner.generate_components(self.pid_manager.pid_list)
        # generate pid num input area and start button
        self.simu_setup_conteiner.generate_components(
            self.set_num_of_pids, # num pids trigger
            self.start_simulation # start trigger
        )

        # draw the components
        self.draw(True)

        self.gui_content_map = []
        self.set_num_of_pids(MAX_NPIDS)
        self.restart_simulation = td.Event()

    def draw(self, autorefresh=False):
        self.title.draw(autorefresh)
        self.pid_setup_conteiner.draw(autorefresh)
        self.simu_setup_conteiner.draw(autorefresh)
    
    def set_num_of_pids(self, npids_str: str):
        """Num of PIDs trigger."""
        npids = int(npids_str)

        self.pid_manager.set_visible_pids(npids)
        # set visible content and get pid labels that are visible
        pid_label_list = self.pid_setup_conteiner.set_first_n_components_to_visible(npids)
        # reset gui content to visible input areas
        self.gui_content_map = [ self.simu_setup_conteiner.components_list ] # keep num_pids and start
        for pid_label in pid_label_list:
            # get the input areas of the pid_label (kp, kd, ki, icon)
            self.gui_content_map.append(pid_label.components_list)
    
    def restart_simulation(self):
        """Start Button trigger."""
        self.restart_simulation.set()


def main(stdscr: _CursesWindow):
    curses.curs_set(0)
    curses.noecho()

    gui = Gui(stdscr)
    stdscr.getch()


if __name__ == '__main__':
    wrapper(main)