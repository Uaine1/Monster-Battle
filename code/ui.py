from settings import *
from monster import Creature

class UI:
    def __init__(self, monster, player_monsters, simple_surfs, get_input):
        self.display_surf = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.top = WINDOW_HEIGHT / 2 + 50
        self.left = WINDOW_WIDTH / 2 - 100
        self.monster = monster
        self.simple_surfs = simple_surfs
        self.get_input = get_input

        self.options = ["attack", "heal", "switch", "run"]
        self.general_index = {"col": 0, "row": 0}
        self.attack_index = {"col": 0, "row": 0}
        self.rows, self.cols = 2, 2
        self.state = "general"
        self.visible_monster = 4
        self.player_monsters = player_monsters
        self.switch_index = 0
        self.available_mons = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]
        

    def input(self):
        keys = pygame.key.get_just_pressed()
        if self.state == "general":
            self.general_index["row"] = (self.general_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.general_index["col"] = (self.general_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]))  % self.cols
            if keys[pygame.K_SPACE]:
                self.state = self.options[self.general_index["col"] + self.general_index["row"] * 2]
                
        elif self.state == "attack":
            self.attack_index["row"] = (self.attack_index["row"] + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % self.rows
            self.attack_index["col"] = (self.attack_index["col"] + int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]))  % self.cols
            if keys[pygame.K_SPACE]:
                attack = self.monster.abilities[self.attack_index["col"] + self.attack_index["row"] * 2]
                self.get_input(self.state, attack)
                self.state = "general"
                
        elif self.state == "switch":
            if self.available_mons:
                self.switch_index = (self.switch_index + int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])) % len(self.available_mons)
                if keys[pygame.K_SPACE]:
                    self.get_input(self.state, self.available_mons[self.switch_index])
                    self.state = "general"

        elif self.state == "heal":
            self.get_input("heal")
            self.state = "general"

        elif self.state == "run":
            self.get_input("run")

        if keys[pygame.K_ESCAPE]:
            self.state = "general"
            self.general_index = {"col": 0, "row": 0}
            self.attack_index = {"col": 0, "row": 0}
            self.switch_index = 0

    
    def quad_select(self, index, options):
        # BG
        rect = pygame.FRect(self.left + 40, self.top +60, 400, 200)
        pygame.draw.rect(self.display_surf, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surf, COLORS["gray"], rect, 3, 4)

        # Menu
        for col in range(self.cols):
            for row in range(self.rows):
                x = rect.left + rect.width / (self.cols * 2) + (rect.width / self.cols) * col
                y = rect.top + rect.height / (self.rows * 2) + (rect.height / self.rows) * row

                i = col + 2 *row
                color = COLORS["gray"] if col == index["col"] and row == index["row"] else COLORS["black"]
                
                text_surf = self.font.render(options[i], True, color)
                text_rect = text_surf.get_frect(center = (x,y))
                self.display_surf.blit(text_surf, text_rect)
                
                
    def switch(self):
        # BG
        rect = pygame.FRect(self.left + 40, self.top - 130, 400, 400)
        pygame.draw.rect(self.display_surf, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surf, COLORS["gray"], rect, 3, 4)
        
        # Menu
        v_offset = 0 if self.switch_index < self.visible_monster else -(self.switch_index - self.visible_monster + 1) * rect.height / self.visible_monster
        for i in range(len(self.available_mons)):
            x = rect.centerx
            y = rect.top + rect.height / (self.visible_monster * 2) + rect.height / self.visible_monster * i + v_offset
            
            name = self.available_mons[i].name
            color = COLORS["gray"] if i == self.switch_index else COLORS["black"]
            
            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(midleft = (x,y))

            simple_surf = self.simple_surfs[name]
            simple_rect = simple_surf.get_frect(center= (x - 100, y))
            
            if rect.collidepoint(text_rect.center):
                self.display_surf.blit(text_surf, text_rect)
                self.display_surf.blit(simple_surf, simple_rect)


    def stats(self):
        # BG
        rect = pygame.FRect(self.left, self.top, 250, 80)
        pygame.draw.rect(self.display_surf, COLORS["white"], rect, 0, 4)
        pygame.draw.rect(self.display_surf, COLORS["gray"], rect, 3, 4)

        # Data
        name_surf = self.font.render(self.monster.name, True, COLORS["black"])
        name_rect = name_surf.get_frect(topleft = rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
        self.display_surf.blit(name_surf, name_rect)

        # Health bar
        health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
        pygame.draw.rect(self.display_surf, COLORS["gray"], health_rect)
        self.draw_bar(health_rect, self.monster.health, self.monster.max_health)


    def draw_bar(self, rect, value, max_value):
        ratio = rect.width / max_value
        progress_rect = pygame.FRect(rect.topleft, (value * ratio,rect.height))
        pygame.draw.rect(self.display_surf, COLORS["red"], progress_rect)


    def draw(self):
        match self.state:
            case "general": self.quad_select(self.general_index, self.options)
            case "attack": self.quad_select(self.attack_index, self.monster.abilities)
            case "switch": self.switch()

        if self.state != "switch":   
            self.stats()


    def update(self):
        self.input()
        self.available_mons = [monster for monster in self.player_monsters if monster != self.monster and monster.health > 0]


class OpponentUI:
    def __init__(self, opponent):
        self.display_surf = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.opponent = opponent
        
        
    def stats(self):
            # BG
            rect = pygame.FRect((0,0), (250, 80)).move_to(midleft = (500, self.opponent.rect.centery))
            pygame.draw.rect(self.display_surf, COLORS["white"], rect, 0, 4)
            pygame.draw.rect(self.display_surf, COLORS["gray"], rect, 3, 4)

            # Data
            name_surf = self.font.render(self.opponent.name, True, COLORS["black"])
            name_rect = name_surf.get_frect(topleft = rect.topleft + pygame.Vector2(rect.width * 0.05, 12))
            self.display_surf.blit(name_surf, name_rect)

            # Health bar
            health_rect = pygame.FRect(name_rect.left, name_rect.bottom + 10, rect.width * 0.9, 20)
            pygame.draw.rect(self.display_surf, COLORS["gray"], health_rect)
            self.draw_bar(health_rect, self.opponent.health, self.opponent.max_health)


    def draw_bar(self, rect, value, max_value):
        ratio = rect.width / max_value
        progress_rect = pygame.FRect(rect.topleft, (value * ratio,rect.height))
        pygame.draw.rect(self.display_surf, COLORS["red"], progress_rect)


    def draw(self):
        self.stats()
