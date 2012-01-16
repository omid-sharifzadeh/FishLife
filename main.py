from random import random, randint
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import *
from kivy.properties import BooleanProperty, StringProperty, NumericProperty

from food import Food, Junk
from fish import Fish
from ship import Ship


class FishLifeBones(App):
    def __init__(self, **kwargs):
        super(FishLifeBones, self).__init__(**kwargs)
        self.ships = []       
        
    def build_config(self, config):
        config.setdefaults('aquarium', {"waterline":200})
        
    def build(self):
        self.welcome_screen = Widget(width=Window.width, height=Window.height)
        begin = Button(text="Feed the Fish!")
        begin.bind(on_release=self.scene_gameplay)
        self.welcome_screen.add_widget(begin)
        
        self.game_screen = Widget(width=Window.width, height=Window.height)
        self.menu = GridLayout(cols=2, row_force_default=True, row_default_height=100, width=Window.width, height=200, pos=(0,0))
        self.menu.add_widget(Label(text="Calories stockpiled", width=100))
        self.calories_bar = ProgressBar(max=1000, value=1000)
        self.menu.add_widget(self.calories_bar)
        self.game_area = Widget(width=Window.width, height=Window.height)
        with self.game_area.canvas:
            Color(1,1,1)
            Rectangle(source="images/bg.png", pos=self.game_area.pos, size=self.game_area.size)
        self.game_screen.add_widget(self.game_area)
        self.game_screen.add_widget(self.menu)
        
        self.manufacture_ships(3)
                
        self.fish = Fish()
        self.fish.bind(pos=lambda instance, value: self.check_for_smthing_to_eat(value))
        self.fish.bind(calories=lambda instance, value: self.calories_bar.value = value)
        
        return self.welcome_screen

    def check_for_smthing_to_eat(self, dt):
        to_eat = []
        for stuff in self.game_area.children:
            if stuff.collide_widget(self.fish):
                if isinstance(stuff, Food):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            shit.parent.remove_widget(shit)
            self.fish.eat(shit.calories)
            print "eaten! ", self.fish.calories
            del(shit)
        
    def drop_food(self, td):
        """Periodicaly drop food from the ships"""
        
        for ship in self.ships:
            food = Food(x = ship.x + randint(0,50), y = ship.y + randint(0,30))
            Clock.schedule_once(lambda td:  self.game_area.add_widget(food) and food.active = True, random * 2)
    
    def sail_ships(self, timer):
        for ship in self.ships:
            ship.sail()
            
    def manufacture_ships(self, count = 1):
        for n in range(0, count):
            ship = Ship()
            self.ships.append(ship)
        
    def drop_onto_sea(self, ship):
        try:
            if not ship:
                ship = self.ships.pop()
            self.game_area.add_widget(ship)
            ship.pos = (randint(20, Window.width - 20), ship.parent.height)
            ship.active = True
        except IndexError:
            obj.text = "No more ships left!"


def FishLifeFlesh(FishLifeBones):
    def __init__(self):
        super(FishLifeFlesh, self).__init__()
    
    def scene_intro(self, *kwargs):
        self.root.clear_widgets()
        self.root.add_widget(self.welcome_screen)
        
    def scene_gameplay(self, *kwargs):
        self.root.clear_widgets()
        self.root.add_widget(self.game_screen)
        
        for ship in self.ships:
            self.drop_onto_sea(ship)
        
        self.game_area.add_widget(self.fish)
        self.fish.active = True
        
        Clock.schedule_interval(self.drop_food, 2)
        Clock.schedule_interval(self.sail_ships, 5)
        Clock.schedule_interval(self.check_for_smthing_to_eat, 0.4)  
           
if __name__ == '__main__':
    FishLifeFlesh().run()