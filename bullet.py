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

class Obstacle:
    def __init__(self, position, size, color):
        self.position = position
        self.size = size
        self.color = color

class Bullet:
    def __init__(self, pos, velocity, mass, radius):
        self.pos = pos
        self.velocity = velocity
        self.mass = mass
        self.radius = radius

class Bombshell(Bullet):
    def __init__(self, pos, velocity, mass, radius, drill_depth):
        super().__init__(pos, velocity, mass, radius)
        self.drill_depth = drill_depth

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

        # Obstacle
        self.obstacle_size = (100, 200)
        self.obstacle_position = (500, 0)
        self.obstacle_color = (1, 1, 1)

        # Cannon
        self.cannon_size = (150, 50)
        self.cannon_pos = (0, 0)
        self.fixed_point = (self.cannon_pos[0], self.cannon_pos[1] + self.cannon_size[1] / 2)

        # Bullets
        self.bullet_count = 0
        self.bullet_size = (20, 20)
        self.bombshell_size = (50, 50)  # Define bombshell size here
        self.bullets = []
        self.bullet_count_label = Label(
            text=str(self.bullet_count),
            pos=(20, Window.height - 400),
            color=get_color_from_hex('#FFFFFF'),
            font_size='200sp'
        )
        self.add_widget(self.bullet_count_label)
        self.lasers = []

        # Target
        self.target_size = (50, 50)
        self.target_position = (Window.width - self.target_size[0], 0)
        self.target_color = (1, 0.5, 0)

        with self.canvas:
            Color(*self.target_color)
            self.target = Rectangle(pos=self.target_position, size=self.target_size)

        # Bind the update method to the mouse position change
        Window.bind(mouse_pos=self.update_cannon_rotation)
        Window.bind(on_mouse_down=self.shoot_bullets)

        # Schedule bullet movement
        Clock.schedule_interval(self.move_bullets, 1 / 60.0)
        Clock.schedule_interval(self.draw_bullets, 1 / 60.0)

        # Add the obstacle
        with self.canvas:
            Color(*self.obstacle_color)
            self.obstacle = Rectangle(pos=self.obstacle_position, size=self.obstacle_size)

        self.bullet_dropdown = DropDown()
        for bullet_type in ['Bullet', 'Bombshell', 'Laser']:
            btn = Button(text=bullet_type, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.bullet_dropdown.select(btn.text))
            self.bullet_dropdown.add_widget(btn)

        self.bullet_select_button = Button(text='Select Bullet Type', size_hint=(None, None), size=(150, 44))
        self.bullet_select_button.bind(on_release=self.bullet_dropdown.open)
        self.bullet_dropdown.bind(on_select=lambda instance, x: setattr(self.bullet_select_button, 'text', x))
        self.add_widget(self.bullet_select_button)
    def shoot_bullets(self, *args):
        bullet_type = self.bullet_select_button.text
        if bullet_type == 'Bullet':
            self.shoot_normal_bullet()
        elif bullet_type == 'Bombshell':
            self.shoot_bombshell()
        elif bullet_type == 'Laser':
            self.shoot_laser()
    
    

    
    def shoot_normal_bullet(self, *args):
        # Calculate the direction vector from the cannon to the cursor
        
        mouse_x, mouse_y = Window.mouse_pos
        direction_x = mouse_x - self.fixed_point[0]
        direction_y = mouse_y - self.fixed_point[1]

        max_velocity = 800 
        min_velocity = 200  
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance == 0:
            return  
        normalized_direction_x = direction_x / distance
        normalized_direction_y = direction_y / distance
        velocity = min(max_velocity, max(min_velocity, distance))

        vx = velocity * normalized_direction_x
        vy = velocity * normalized_direction_y

        bullet_pos = (
            self.fixed_point[0] + self.cannon_size[0] * normalized_direction_x,
            self.fixed_point[1] + self.cannon_size[0] * normalized_direction_y - self.bullet_size[1] / 2
        )
        self.canvas.after.clear()

        with self.canvas.after:
            Color(1, 0, 0)  # Set color to red
            bullet = Ellipse(pos=bullet_pos, size=self.bullet_size)
            self.bullets.append((bullet, vx, vy))
        self.bullet_count += 1  # Increment bullet count
        self.bullet_count_label.text = str(self.bullet_count)
    
    def shoot_bombshell(self):
        mouse_x, mouse_y = Window.mouse_pos
        direction_x = mouse_x - self.fixed_point[0]
        direction_y = mouse_y - self.fixed_point[1]

        max_velocity = 800
        min_velocity = 200
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if distance == 0:
            return
        normalized_direction_x = direction_x / distance
        normalized_direction_y = direction_y / distance
        velocity = min(max_velocity, max(min_velocity, distance))

        vx = velocity * normalized_direction_x
        vy = velocity * normalized_direction_y

        bullet_pos = (
            self.fixed_point[0] + self.cannon_size[0] * normalized_direction_x,
            self.fixed_point[1] + self.cannon_size[0] * normalized_direction_y - self.bombshell_size[1] / 2
        )
        self.canvas.after.clear()

        with self.canvas.after:
            Color(0, 0, 1)  # Set color to blue for bombshell
            bombshell = Ellipse(pos=bullet_pos, size=self.bombshell_size)
            self.bullets.append((bombshell, vx, vy, 'bombshell'))
        self.bullet_count += 1
        self.bullet_count_label.text = str(self.bullet_count)

    
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
        self.bullet_count += 1
        self.bullet_count_label.text = str(self.bullet_count)

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

    def draw_bullets(self, dt):
        self.canvas.after.clear()
        with self.canvas.after:
            for bullet_info in self.bullets:
                bullet = bullet_info[0]
                bullet_type = bullet_info[3] if len(bullet_info) == 4 else 'normal'
                size = self.bombshell_size if bullet_type == 'bombshell' else self.bullet_size
                Color(0, 0, 1) if bullet_type == 'bombshell' else Color(1, 0, 0)  # Blue for bombshell, Red for bullet
                Ellipse(pos=bullet.pos, size=size)

    def move_bullets(self, dt):
        g = 250
        new_bullets = []
        for bullet_info in self.bullets:
            bullet_type = bullet_info[3] if len(bullet_info) == 4 else 'normal'
            bullet, vx, vy = bullet_info[:3]

            bullet_pos = bullet.pos
            bullet_size = self.bombshell_size if bullet_type == 'bombshell' else self.bullet_size
            bullet_x, bullet_y = bullet_pos

            bullet_x += vx * dt
            bullet_y += vy * dt

            if bullet_x < -bullet_size[0] or bullet_x > Window.width or \
            bullet_y < -bullet_size[1] or bullet_y > Window.height:  
                continue

            if bullet_type == 'bombshell' and self.check_obstacle_collision((bullet_x, bullet_y), bullet_size):
                self.explode_obstacle(self.obstacle)
                continue  # Don't proceed further for this bullet

            if self.check_obstacle((bullet_x, bullet_y), bullet_size):
                vy = -vy
                bullet_y += vy * dt

                if bullet_x < self.obstacle_position[0] or bullet_x > self.obstacle_position[0] + self.obstacle_size[0]:
                    vx = -vx
                    bullet_x += vx * dt
                self.explode_obstacle(self.obstacle)  

            if self.check_target((bullet_x, bullet_y), bullet_size):
                print("Hit target!")

            vy -= g * dt
            bullet.pos = (bullet_x, bullet_y)

            if bullet_type == 'bombshell':
                new_bullets.append((bullet, vx, vy, 'bombshell'))
            else:
                new_bullets.append((bullet, vx, vy))

        self.bullets = new_bullets

    def check_obstacle_collision(self, bullet_pos, bullet_size):
        obstacle_pos = self.obstacle_position
        obstacle_size = self.obstacle_size

        if (obstacle_pos[0] < bullet_pos[0] + bullet_size[0] and
            obstacle_pos[0] + obstacle_size[0] > bullet_pos[0] and
            obstacle_pos[1] < bullet_pos[1] + bullet_size[1] and
            obstacle_pos[1] + obstacle_size[1] > bullet_pos[1]):
            return True
        else:
            return False
    
    def explode_obstacle(self, obstacle):
        pass

    def check_target(self, bullet_pos, bullet_size):
        target_pos = self.target_position
        target_size = self.target_size

        if (target_pos[0] < bullet_pos[0] + bullet_size[0] and
            target_pos[0] + target_size[0] > bullet_pos[0] and
            target_pos[1] < bullet_pos[1] + bullet_size[1] and
            target_pos[1] + target_size[1] > bullet_pos[1]):
            return True
        else:
            return False

    def check_obstacle(self, bullet_pos, bullet_size):
        obstacle_pos = self.obstacle_position
        obstacle_size = self.obstacle_size

        if (obstacle_pos[0] < bullet_pos[0] + bullet_size[0] and
            obstacle_pos[0] + obstacle_size[0] > bullet_pos[0] and
            obstacle_pos[1] < bullet_pos[1] + bullet_size[1] and
            obstacle_pos[1] + obstacle_size[1] > bullet_pos[1]):
            return True
        else:
            return False

class Myapp(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        return Myapp()

if __name__ == '__main__':
    sound = SoundLoader.load('theme.mp3')
    sound.play()
    MyApp().run()

