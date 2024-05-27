import kivy
from kivy.app import App
from kivy.graphics import Color, Rectangle, Ellipse, PushMatrix, PopMatrix, Rotate, Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics.transformation import Matrix
import math
import random
from kivy.config import Config 
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from functools import partial

class Myapp(Widget):
    def __init__(self, **kwargs):
        super(Myapp, self).__init__(**kwargs)
        Config.set('graphics', 'resizable', True)
        

class MenuScreen(Screen):
    pass

class Laser:
    def __init__(self, pos, direction, velocity, duration, max_distance):
        self.pos = pos
        self.direction = direction
        self.velocity = velocity
        self.duration = duration
        self.max_distance = max_distance

class Game(Screen, Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)

        # Cannon
        self.cannon_size = (150, 50)
        self.cannon_pos = (0, 0)
        self.fixed_point = (self.cannon_pos[0], self.cannon_pos[1] + self.cannon_size[1] / 2)

    
        self.lasers = []

        Window.bind(mouse_pos=self.update_cannon_rotation)


    
    
    def shoot_laser(self):
        mouse_x, mouse_y = Window.mouse_pos
        direction_x = mouse_x - self.fixed_point[0]
        direction_y = mouse_y - self.fixed_point[1]

        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance == 0:
            return
        normalized_direction_x = direction_x / distance
        normalized_direction_y = direction_y / distance

        bullet_pos = (
            self.fixed_point[0] + self.cannon_size[0] * normalized_direction_x,
            self.fixed_point[1] + self.cannon_size[0] * normalized_direction_y
        )
        laser_duration = 10.0  # Duration of the laser in seconds
        laser_velocity = 200  # Constant velocity of the laser

        # Calculate end point of the laser segment based on velocity
        end_point_x = bullet_pos[0] + normalized_direction_x * laser_velocity
        end_point_y = bullet_pos[1] + normalized_direction_y * laser_velocity

        # Draw the laser segment
        with self.canvas:
            Color(1, 0, 0)  # Set color to red for laser
            laser = Line(points=[bullet_pos[0], bullet_pos[1], end_point_x, end_point_y], width=5)
            self.lasers.append((laser, laser_velocity, normalized_direction_y * laser_velocity))

        # Schedule updating the laser position
        Clock.schedule_interval(partial(self.update_laser_position, laser), 1 / 60.0)
        Clock.schedule_once(partial(self.clear_laser, laser), laser_duration)

    def update_laser_position(self, laser, dt):
        laser.points = [laser.points[0] + laser.points[2] * 0.01,
                        laser.points[1] + laser.points[3] * 0.01,
                        laser.points[2] + laser.points[2] * 0.01,
                        laser.points[3] + laser.points[3] * 0.01]

    def clear_laser(self, laser, dt):
        self.canvas.remove(laser)
        for laser_info in self.lasers[:]:
            if laser_info[0] == laser:
                self.lasers.remove(laser_info)
                break 
        Clock.unschedule(partial(self.update_laser_position, laser))



    def update_cannon_rotation(self, *args):
        mouse_x, mouse_y = Window.mouse_pos
        delta_x = mouse_x - self.fixed_point[0]
        delta_y = mouse_y - self.fixed_point[1]
        self.cannon_angle = math.degrees(math.atan2(delta_y, delta_x))

        self.canvas.before.clear()
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=self.cannon_angle, origin=self.fixed_point)
            Color(1, 1, 1)  
            self.cannon = Rectangle(pos=self.cannon_pos, size=self.cannon_size)
            PopMatrix()


class Myapp(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        return Myapp()

if __name__ == '__main__':
    sound = SoundLoader.load('theme.mp3')
    sound.play()
    MyApp().run()

