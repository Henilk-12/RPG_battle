import pygame
import random
import button
import os
import time
import sys

# 初始化
pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()
fps = 60

# 遊戲視窗設定
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('RPG-Battle')

# 定義遊戲變數
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0 # 0: 進行中, 1: 勝利, -1: 失敗

# 定義字體與顏色
font = pygame.font.SysFont('Times New Roman', 26)
red = (255, 0, 0)
green = (0, 255, 0)

# 載入圖片素材
icon = pygame.image.load('img/Icons/icon.ico')
pygame.display.set_icon(icon)
background_img = pygame.image.load('img/Background/background.png').convert_alpha()
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()
sword_img = pygame.image.load('img/Icons/sword.png').convert_alpha()

# 載入音樂
pygame.mixer.music.load(os.path.join("sound","RPG_background.mp3"))
pygame.mixer.music.set_volume(0.3)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        
        actions = ['Idle', 'Attack', 'Hurt', 'Death']
        counts = [8, 8, 3, 10]
        for action_idx, count in enumerate(counts):
            temp_list = []
            for i in range(count):
                img = pygame.image.load(f'img/{self.name}/{actions[action_idx]}/{i}.png')
                img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x, self.y, self.hp, self.max_hp = x, y, hp, max_hp
    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()
knight = Fighter(200, 260, 'Knight', 30, 10, 3)
bandit1 = Fighter(550, 270, 'Bandit', 20, 6, 1)
bandit2 = Fighter(700, 270, 'Bandit', 20, 6, 1)
bandit_list = [bandit1, bandit2]

knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)

pygame.mixer.music.play(-1)

run = True
while run:
    clock.tick(fps)
    draw_bg()
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)

    attack = False
    potion = False
    target = None
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked == True and bandit.alive == True:
                attack = True
                target = bandit_list[count]
    
    if potion_button.draw():
        potion = True
    draw_text(str(knight.potions), font, red, 150, screen_height - bottom_panel + 70)

    if game_over == 0:
        if knight.alive == True:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack == True and target != None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    if potion == True and knight.potions > 0:
                        heal_amount = min(potion_effect, knight.max_hp - knight.hp)
                        knight.hp += heal_amount
                        knight.potions -= 1
                        damage_text_group.add(DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green))
                        current_fighter += 1
                        action_cooldown = 0
        
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                            heal_amount = min(potion_effect, bandit.max_hp - bandit.hp)
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text_group.add(DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green))
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            bandit.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1

        if current_fighter > total_fighters:
            current_fighter = 1

    alive_bandits = sum(1 for b in bandit_list if b.alive)
    
    if alive_bandits == 0 and game_over == 0:
        all_dead_anim_done = True
        for b in bandit_list:
            if b.action == 3:
                if b.frame_index < len(b.animation_list[3]) - 1:
                    all_dead_anim_done = False
            else:
                all_dead_anim_done = False
        if all_dead_anim_done:
            game_over = 1

    if knight.alive == False and game_over == 0:
        if knight.action == 3:
            if knight.frame_index >= len(knight.animation_list[3]) - 1:
                game_over = -1
        else:
            knight.death()

    if game_over != 0:
        knight_health_bar.draw(knight.hp)
        bandit1_health_bar.draw(bandit1.hp)
        bandit2_health_bar.draw(bandit2.hp)

        if game_over == 1:
            screen.blit(victory_img, (250, 50))
        elif game_over == -1:
            screen.blit(defeat_img, (290, 50))
        
        pygame.display.update()
        time.sleep(2) 
        
        if game_over == 1:
            print("BOSS_DEFEATED")
            pygame.quit()
            sys.exit(0)
        elif game_over == -1:
            print("PLAYER_DEAD")
            pygame.quit()
            sys.exit(1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()
