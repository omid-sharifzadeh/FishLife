from kivy.properties import BooleanProperty, OptionProperty

class Ship(Image):
    
    active = BooleanProperty(False)
    state = OptionProperty(["fishing", "sailing"])
    
    def __init__(self, image = "gnome-dev-media-sdmmc.png", **kwargs):
        self.source = image
        self.horison = 100 # Pixels from the top of parent container
        super(Ship, self).__init__(**kwargs)
        self.register_event_type('on_start_sailing')
        
        self.bind(active=lambda instance, value: Animation(y=Window.height - self.horison, t="out_back", d=1.2).start(instance))
        
    def sail(self):
        self.dispatch("on_start_sailing")
        
        # TODO: more intresting/smooth placing and transition
        new_fishing_place = randint(40, self.parent.width - 40)
        anim = Animation(x=new_fishing_place, t="in_out_quad", d=2)
        
        anim.bind(on_complete: lambda instance, value: self.dispatch("on_stop_sailing"))    
        anim.start(self)
        
    #    
    # Events    
    #
    
    def on_start_sailing(self):
        self.state = "sailing"
        
    def on_stop_sailing(self):
        self.state = "fishing"