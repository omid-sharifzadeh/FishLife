from random import random, randint
from functools import partial
from datetime import datetime

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.clock import _hash
from kivy.graphics import Color
from kivy.graphics.vertex_instructions import *
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ListProperty, ObjectProperty

from kivy.lang import Builder
from kivy.logger import Logger

from food import Food, Junk, FoodScoreFeedback
from fish import Fish
from ship import Ship


class FishLifeIntro(Widget):
    pass

class FishLifeScore(Popup):
    def __init__(self):
        super(FishLifeScore, self).__init__()
        self.pos = (Window.width/2 - self.width/2, Window.height/2 - self.height/2)
        self.content = Widget(pos=self.pos)
        self.content.add_widget(self.score_table)
        self.content.add_widget(self.total_score)
        self.content.add_widget(self.restart_btn)
    
class FishLifeGame(Widget):

    ships = ListProperty([])
    fish = ObjectProperty(None)
    
    start_time = ObjectProperty(None)
    
    def __init__(self, *args, **kwargs):
        self.size = (Window.width, Window.height)

        super(FishLifeGame, self).__init__(*args, **kwargs)
        #self.waves.texture = self.waves.texture.get_region(0,0, self.game_screen.width, self.waves.height)
        
        self.victory_screen = FishLifeScore()
        
        self.manufacture_ships(3)
       
        self.fish = Fish(box=[self.game_area.x, self.game_area.y + 65, self.game_area.width, self.game_area.height - 175])
        self.fish.bind(pos=lambda instance, value: self.check_for_smthing_to_eat(value))
        self.fish.bind(calories=self.update_calories_bar)  
        self.fish.bind(on_death=self.the_end) 

    def play(self):
        for ship in self.ships:
            self.drop_ship_onto_sea(ship)
    
        self.game_area.add_widget(self.fish, index=1)
        self.fish.active = True
        
        Clock.schedule_interval(self.drop_food, 2)
        Clock.schedule_interval(self.sail_ships, 5)
        Clock.schedule_interval(self.check_for_smthing_to_eat, 0.4)
        
        self.start_time = datetime.now() 
        
    def pause(self):
        Clock.unschedule(self.drop_food)
        Clock.unschedule(self.sail_ships)
        Clock.unschedule(self.check_for_smthing_to_eat) 
        
    def the_end(self, instance):
        self.pause()
        self.victory_screen.calories_score.text = str(self.fish.total_calories)
        self.victory_screen.junk_score.text = str(self.fish.junk_swallowed)
        self.victory_screen.total_score.text = "On %s a fish was caught, size of %s, which well fed the people of the world for %s days straight!" % (datetime.now().strftime("%B %d, %Y"), self.fish.rank[self.fish.obese_lvl - 1], (datetime.now() - self.start_time).seconds )
        self.add_widget(self.victory_screen)  
          
    def manufacture_ships(self, count = 1):
        for n in range(0, count):
            ship = Ship(horison=self.horison)
            self.ships.append(ship)
            
        # *cough*workaround*cough* bind on first ship
        self.ships[0].bind(on_start_sailing=lambda instance: Clock.schedule_interval(self.drop_junk, 0.4))
        self.ships[0].bind(on_stop_sailing=lambda instance: Clock.unschedule(self.drop_junk))      
        
    def drop_ship_onto_sea(self, ship):
        try:
            if not ship:
                ship = self.ships.pop()
            self.game_area.add_widget(ship)

            ship.center_x = randint(0, Window.width - ship.width/4)
            ship.y = self.game_area.height
            ship.active = True
        except IndexError:
            Logger.debug("No ships left in dock.")   
            
    def check_for_smthing_to_eat(self, dt):
        to_eat = []
        for stuff in self.game_area.children:
            if stuff.collide_widget(self.fish):
                if isinstance(stuff, Food) or isinstance(stuff, Junk):
                    to_eat.append(stuff)
                
        for shit in to_eat:
            self.game_area.remove_widget(shit)
            self.game_area.add_widget(FoodScoreFeedback(calories=shit.calories, center=shit.center))
            
            self.fish.eat(shit)
        
    def drop_food(self, td):
        """Periodicaly drop food from the ships"""
        
        for ship in self.ships:
            food = Food(what="bottle", lvl=self.fish.obese_lvl, x = ship.center_x + randint(-50,50), y = ship.y + randint(-5,5))
            def really_drop_food(food, td):
                 self.game_area.add_widget(food)
                 food.active = True
            Clock.schedule_once(partial(really_drop_food, food), random() * 2)
    
    def drop_junk(self, *args):
        for ship in self.ships:
            junk = Junk(lvl=self.fish.obese_lvl, x = ship.center_x + randint(-50,50), y = ship.y + randint(-5,5))
            self.game_area.add_widget(junk)
            junk.active = True
        
    def sail_ships(self, timer):
        for ship in self.ships:
            ship.sail()        

    def update_calories_bar(self, instance, new_value):
        self.calories_bar.value = new_value        


class FishLifeBones(App):
    def __init__(self, *args, **kwargs):
        super(FishLifeBones, self).__init__(*args, **kwargs)

    def build_config(self, config):
        config.setdefaults('aquarium', {"waterline":200})
        #config.setdefaults('graphics', {"width":1280, "height": 726})
        
    def build(self):
        Builder.load_file("intro.kv")
        self.intro = FishLifeIntro()
        self.intro.go_btn.bind(on_release=self.begin_game)
        return self.intro
        
    def begin_game(self, *args):
        Builder.load_file("main.kv")
        self.root = self.fishlife = FishLifeGame()
        self.fishlife.victory_screen.restart_btn.bind(on_press=self.restart_game)
        
        Window.add_widget(self.root)
        self.root.play()
              
    def restart_game(self, *args):
        self.fishlife.victory_screen.restart_btn.unbind(on_press=self.restart_game)
        Window.remove_widget(self.fishlife)
        
        # Because widgets later on disappear. Why? Dunno, maybe garbage
        # collector does it's work?
        # Thus, unload and then load the rules again, and now widgets do not
        # disappear.
        Builder.unload_file("main.kv")
        self.begin_game()
        
   
        
if __name__ == '__main__':
    FishLifeBones().run()
    
"""
(02:33:19 AM) tito: from kivy.config import Config; Config.set('graphics', 'width', '1280') + same for height
(02:33:24 AM) tito: before anything
"""