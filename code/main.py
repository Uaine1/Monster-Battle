from settings import *
from support import *
from random import choice
from ui import *
from attack import AttackAnimationSprite
from monster import *
from timer import Timer  # type: ignore

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.player_active = True

        self.import_assets()

        # groups 
        self.all_sprites = pygame.sprite.Group()

        # Data
        player_monster_list = ["Atrox", "Charmadillo", "Cleaf", "Cindrill", "Gulfin", "Pluma"]
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)

        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)

        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)

        # Timer
        self.timers = {"player end": Timer(1000, func = self.opponent_turn), "opponent end": Timer(1000, func = self.player_turn)}
        
        self.audio["music"].play(-1)


    def get_input(self, state, data = None):
        if state == "attack":
            self.apply_atk(self.opponent, data)

        elif state == "heal":
            self.monster.health += 50
            AttackAnimationSprite(self.monster, self.attack_frames["green"], self.all_sprites)
            self.audio["green"].play()

        elif state == "switch":
            self.monster.kill()
            self.monster = data
            self.all_sprites.add(self.monster)
            self.ui.monster = self.monster

        elif state == "run":
            self.running = False
        self.player_active = False
        self.timers["player end"].activate()

    
    def apply_atk(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        attack_multiplier = ELEMENT_DATA[attack_data["element"]][target.element]
        target.health -= attack_data["damage"] * attack_multiplier
        AttackAnimationSprite(target, self.attack_frames[attack_data["animation"]], self.all_sprites)
        self.audio[attack_data["animation"]].play()
        print(f"{attack}, {target.health}/{target.max_health}")
        

    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            available_mons = [monster for monster in self.player_monsters if monster.health > 0]
            if available_mons:
                self.monster.kill()
                self.monster = available_mons[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                self.runnng = False


    def opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            monster_name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(monster_name, self.front_surfs[monster_name], self.all_sprites)
            self.opponent_ui.opponent = self.opponent
        else:
            attack = choice(self.opponent.abilities)
            self.apply_atk(self.monster, attack)
            self.timers["opponent end"].activate()

    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    

    def import_assets(self):
        # Graphics
        self.front_surfs = folder_importer("images", "front")
        self.back_surfs = folder_importer("images", "back")
        self.simple_surfs = folder_importer("images", "simple")
        self.bg_surf = folder_importer("images", "other")
        self.attack_frames = tile_importer(4, "images", "attacks")

        # Sounds
        self.audio = audio_importer("audio")


    def draw_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surf["floor"].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surf["floor"], floor_rect)


    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
           
            # update
            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active: # responsible for ui update for the player's turn
                self.ui.update()           
            
            # draw  
            self.display_surface.blit(self.bg_surf["bg"], (0,0))
            self.draw_floor()
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            self.opponent_ui.draw()
            pygame.display.update()
        
        pygame.quit()
    

if __name__ == '__main__':
    game = Game()
    game.run()