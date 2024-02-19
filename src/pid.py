class Pid:
    def __init__(self, icon='●', kp=0.5, kd=0.05, ki=0.0, pos=-100, sp=0):
        # screen apperance
        self.icon = icon
        # self.color = curses.init_color()
        # graph & movement
        self.pos = pos
        self.vel = 0
        self.constant_error = 0
        # PID constants
        self.sp = sp
        self.kp = kp
        self.kd = kd
        self.ki = ki
        # PID variables
        self.integral = 0
        self.last_error = sp - self.pos

    def __call__(self, dt) -> float:
        error = self.sp - self.pos

        p_fix = self.kp * error

        d_fix = self.kd*(error - self.last_error)/dt
        self.last_error = error

        self.integral += error * dt
        i_fix = self.ki * self.integral

        aceleracao = p_fix + d_fix + i_fix - self.constant_error

        self.pos += self.vel*dt + aceleracao*dt*dt/2
        self.vel += aceleracao*dt
        self.pos = round(self.pos, 2)

        return self.pos

    def set_kp(self, kp):
        self.kp = float(kp)

    def set_kd(self, kd):
        self.kd = float(kd)

    def set_ki(self, ki):
        self.ki = float(ki)

    def set_icon(self, newicon):
        self.icon = newicon

    def set_constant_error(self, const_error):
        """
        Set the persistent error for integral part.
        Its divided by -2 to make it proporcional to the grid pos.
        """
        self.constant_error = -float(const_error)/2

    def reset(self):
        self.pos = -100
        self.vel = 0
        self.last_error = self.sp - self.pos
        self.integral = 0
