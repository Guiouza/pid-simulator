from curses import wrapper, _CursesWindow
import threading as td
import curses
# internal libs
from assets import *
from mathtools import *
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

# Simulation -> Conteiner
SIMULATION_CONTEINER_ASSET = './assets/simulation/conteiner.txt'
# Simulation -> Header
HEADER_ASSET = './assets/simulation/header.txt'
PID_POS_ASSET = './assets/simulation/pid_pos.txt'
# Simulation -> Display
DISPLAY_ASSET = './assets/simulation/display.txt'
TICK_GRID_ASSET = './assets/simulation/tick_grid.txt'
PID_GRID_ASSET = './assets/simulation/pid_grid.txt'

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


class PidPosition(Text):
    pos_max_length = 7
    def __init__(self,
                    conteiner: _CursesWindow,
                    assetfile: str,
                    pid: Pid,
                    attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        self.asset_template = self.asset['text']
        self.pid = pid

    def draw(self, autorefresh=False) -> None:
        self.asset['text'] = self.asset_template
        self.format_asset(
            icon=self.pid.icon,
            pos=f"{'+' if self.pid.pos > 0 else ''}{self.pid.pos:3.2f}"
            .rjust(self.pos_max_length)
        )
        return super().draw(autorefresh)


class Header(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        # align: center
        conteiner_ncols = conteiner.getmaxyx()[1]
        self.asset['win_x'] += (conteiner_ncols - self.asset['ncols'])//2

        self.create_win()

    def generate_components(self, pid_list: list[Pid]):
        n = 0
        for pid in pid_list:
            component = PidPosition(self.win, PID_POS_ASSET, pid)
            component.asset['win_y'] += component.asset['nlines']*n
            self.components_list.append(component)
            n += 1


class PidGrid(Text):
    def __init__(self,
                    conteiner: _CursesWindow,
                    assetfile: str,
                    pid=None,
                    attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        self.pid = pid

        conteiner_ncols = conteiner.getmaxyx()[1]
        # set grid width (ncols)
        self.grid_width = conteiner_ncols - self.asset['ncols']
        # set asset ncols
        self.asset['ncols'] = conteiner_ncols
        # generate the grid base template
        self.format_asset(grid='│'.center(self.grid_width))
        self.grid_template = self.asset['text']

    def draw(self, autorefresh=False) -> None:
        self.asset['text'] = self.grid_template # reset asset['text']
        
        if self.visible:
            n = map_pos(self.pid.pos, self.grid_width)
            # format to show the pid icon
            self.asset['text'] = self.asset['text'][:n] + \
                self.pid.icon + self.asset['text'][n+1:]
            return super().draw(autorefresh)
        
        self.visible = True
        super().draw(autorefresh)
        self.visible = False    
        return


class Display(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        conteiner_ncols = conteiner.getmaxyx()[1]
        # Fill wall the window marging with the border (-2)
        self.asset['ncols'] = conteiner_ncols - 2

        self.create_win()

    def generate_components(self, pid_list: list[Pid]):
        tick = Text(self.win, TICK_GRID_ASSET)
        # format and set window width (ncols)
        tick.asset['ncols'] = self.asset['ncols']
        space = self.asset['ncols']//2 - len('+100')
        tick.format_asset(space=' '*space)
        # add to components
        self.components_list = [ tick ]

        for n in range(self.asset['nlines'] - tick.asset['nlines']):
            if n == 0 or n == self.asset['nlines'] - tick.asset['nlines'] - 1:
                # grid that doesn't have a pid
                component = PidGrid(self.win, PID_GRID_ASSET)
                component.visible = False
            else:
                # grid that will show their pids
                component = PidGrid(self.win, PID_GRID_ASSET, pid_list[n-1])
            component.asset['win_y'] += component.asset['nlines']*n + tick.asset['nlines']

            self.components_list.append(component) 

    def set_first_n_components_to_visible(self, n: int):
        index = 0
        for pidgrid in self.components_list[2:-1]:
            if index < n:
                pidgrid.visible = True
            else:
                pidgrid.visible = False
            index += 1

            pidgrid.draw(True)


class Simulation(Conteiner):
    def __init__(self,
                 conteiner: _CursesWindow,
                 assetfile: str,
                 attr=curses.A_NORMAL ):
        super().__init__(conteiner, assetfile, attr)
        self.asset['nlines'] = curses.LINES
        self.asset['ncols'] = nearst_odd(curses.COLS - self.asset['win_x'])

        self.create_win()

    def generate_components(self, pid_list):
        self.components_list = [
            Header(self.win, HEADER_ASSET),
            Display(self.win, DISPLAY_ASSET)
        ]
        for component in self.components_list:
            component.generate_components(pid_list)

    def set_first_n_components_to_visible(self, n: int):
        header, display = self.components_list
        header.set_first_n_components_to_visible(n)
        display.set_first_n_components_to_visible(n)


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
        self.simulation_conteiner = Simulation(stdscr, SIMULATION_CONTEINER_ASSET)

        self.pid_manager = PidManager(MAX_NPIDS)

        # generate pid setup input areas: (kp kd ki icon)
        self.pid_setup_conteiner.generate_components(self.pid_manager.pid_list)
        # generate the simulation header and display
        self.simulation_conteiner.generate_components(self.pid_manager.pid_list)
        # generate pid num input area and start button
        self.simu_setup_conteiner.generate_components(
            self.set_num_of_pids, # num pids trigger
            self.start_simulation # start trigger
        )

        # draw the components
        self.draw(True)

        self.gui_content_map = []
        self.set_num_of_pids(MAX_NPIDS)
        self.cursor_y_index = 0
        self.cursor_x_index = 0

        # simulation events
        self.restart_simulation = td.Event()

    def draw(self, autorefresh=False):
        self.title.draw(autorefresh)
        self.pid_setup_conteiner.draw(autorefresh)
        self.simu_setup_conteiner.draw(autorefresh)
        self.simulation_conteiner.draw(autorefresh)
    
    def set_num_of_pids(self, npids_str: str):
        """Num of PIDs trigger."""
        npids = int(npids_str)

        self.pid_manager.set_visible_pids(npids)
        self.simulation_conteiner.set_first_n_components_to_visible(npids)

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
    
    def move_cursor(self, direction) -> int:
        have_moved = False

        gui_content_map_rows = len(self.gui_content_map)
        gui_content_map_cols = len(self.gui_content_map[self.cursor_y_index])
        match direction:
            case 'up':
                if self.cursor_y_index > 0:
                    self.cursor_y_index -= 1
                    have_moved = True
            case 'down':
                if self.cursor_y_index + 1 < gui_content_map_rows:
                    self.cursor_y_index += 1
                    have_moved = True
            case 'left':
                if self.cursor_x_index > 0:
                    self.cursor_x_index -= 1
                    have_moved = True
            case 'right':
                if self.cursor_x_index + 1 < gui_content_map_cols:
                    self.cursor_x_index += 1
                    have_moved = True

        # Correct the x position when y is moved
        gui_content_map_cols = len(self.gui_content_map[self.cursor_y_index])
        if self.cursor_x_index >= gui_content_map_cols:
            self.cursor_x_index = gui_content_map_cols - 1
        
        if self.change_color.is_set():
            self.blink()

        return have_moved

    def get_current_selection(self) -> TextInput|Button:
        return self.gui_content_map[self.cursor_y_index][self.cursor_x_index]


def main(stdscr: _CursesWindow):
    curses.curs_set(0)
    curses.noecho()

    gui = Gui(stdscr)
    stdscr.getch()


if __name__ == '__main__':
    wrapper(main)