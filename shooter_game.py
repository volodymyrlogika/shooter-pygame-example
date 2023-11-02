from pygame import *
from random import randint
import os

init()
font.init()
mixer.init()

WIDTH, HEIGHT = 900, 600 #розмір вікна
PATH = os.getcwd() #шлях до папки з грою
ASSETS_PATH = os.path.join(PATH, 'assets')#шлях до папки assets

# картинка фону
bg_image = image.load(ASSETS_PATH + os.sep + "infinite_starts.jpg")
#картинки для спрайтів
player_image = image.load(ASSETS_PATH + os.sep + "spaceship.png")
alien_image = image.load(ASSETS_PATH + os.sep + "alien.png")
fire_image = image.load(ASSETS_PATH + os.sep + "fire.png")

# фонова музика
mixer.music.load(ASSETS_PATH + os.sep + 'musictheme.ogg')
mixer.music.set_volume(0.2)
mixer.music.play(-1) # нескінченно відтворювати фонову музику
# mixer.music.stop(-1) # зупинити фонову музику

#окремі звуки
fire_sound = mixer.Sound(ASSETS_PATH + os.sep + "laser1.wav")
fire_sound.set_volume(0.2) #задати гучність звуку

# створення вікна
window = display.set_mode((WIDTH, HEIGHT)) 
display.set_caption("Шутер")
clock = time.Clock()

# класи 
class GameSprite(sprite.Sprite):
    def __init__(self, sprite_img, width, height, x, y, speed = 3):
        super().__init__()
        self.image = transform.scale(sprite_img, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def draw(self): #відрисовуємо спрайт у вікні
        window.blit(self.image, self.rect)


class Player(GameSprite):
    def update(self): #рух спрайту
        keys_pressed = key.get_pressed() 
        if keys_pressed[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys_pressed[K_RIGHT] and self.rect.x < WIDTH - 70:
            self.rect.x += self.speed
        
    def fire(self):
        bullet = Bullet( fire_image, 10, 30, self.rect.centerx - 5, self.rect.y-10)
        bullets.add(bullet)
        fire_sound.play()
        

class Enemy(GameSprite):
    def update(self):
        global lost
        ''' рух спрайту '''
        if self.rect.y < HEIGHT:
            self.rect.y += self.speed
        else:  #якщо спрайт дійшов до нижнього краю
            lost += 1
            lost_text.set_text("Пропущено:" + str(lost))
            self.rect.y = randint(-500, -100) #рандомні координати зверхну екану
            self.rect.x = randint(0, WIDTH - 70)
            self.speed = randint(2, 5)  #рандомна швидкість


class Bullet(GameSprite):
    def update(self):
        ''' рух спрайту '''
        if self.rect.y > -20:
            self.rect.y -= self.speed
        else:  #якщо спрайт дійшов до верхнього краю
            self.kill() # видалити спрайт з усіх груп


class Text(sprite.Sprite): # клас для написів
    def __init__(self, text, x, y, font_size=22, font_name="Impact", color=(255,255,255)):
        self.font = font.SysFont(font_name, font_size)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color = color
        
    def draw(self): #відрисовуємо спрайт у вікні
        window.blit(self.image, self.rect)
    
    def set_text(self, new_text): #змінюємо текст напису
        self.image = self.font.render(new_text, True, self.color)


# написи для лічильників очок
score_text = Text("Рахунок: 0", 20, 50)
lost_text = Text("Пропущено: 0", 20, 20)
# напис з результатом гри
result_text = Text("Перемога!", 350, 250, font_size = 50)

#додавання фону
bg = transform.scale(bg_image, (WIDTH, HEIGHT))

# створення спрайтів
player = Player(player_image, width = 100, height = 100, x = 200, y = HEIGHT-150)
ufos = sprite.Group() #група спрайтів-ворогів
bullets = sprite.Group() #група спрайтів-куль

for i in range(7): #генерація початкових спрайтів
    rand_y = randint(-500, -100)
    rand_x = randint(0, WIDTH - 70)
    rand_speed = randint(2, 4)
    ufos.add(Enemy(alien_image, width = 80,  height = 50, x = rand_x, y = rand_y, speed = rand_speed)) #додаємо новий спрайт в групу

# основні змінні для гри
run = True
finish = False
FPS = 60
score = 0
lost = 0

#ігровий цикл
while run:
    for e in event.get():
        if e.type == QUIT: # якщо вікно закривається
            run = False #гра зупиняється
        if e.type == KEYDOWN:
            if e.key == K_SPACE:  #якщо натиснуто пробіл
                player.fire() #постріл

    if not finish: #якщо гра не закінчена
        player.update() #рух гравця
        bullets.update() # рух куль
        ufos.update()

        #зіткнення групи куль та групи ворогів
        spritelist = sprite.groupcollide(ufos, bullets, True, True)
        for collide in spritelist:
            score += 1
            score_text.set_text("Рахунок:" + str(score))
            rand_y = randint(-500, -100)
            rand_x = randint(0, WIDTH - 70)
            rand_speed = randint(2, 4)
            ufos.add(Enemy(alien_image, width = 80,  height = 50, x = rand_x, y = rand_y, speed = rand_speed))
        
        #зіткнення гравця і групи ворогів
        spritelist = sprite.spritecollide(player, ufos, False)
        for collide in spritelist: # для кожного спрайта що зіткнувся
            finish = True
            result_text.set_text("ПРОГРАШ!")
        if lost >= 10: # якщо пропущено більше 10 ворогів
            finish = True
            result_text.set_text("ПРОГРАШ!")

        window.blit(bg, (0, 0))  #додаємо фон
       
        player.draw() #відрисовуємо спрайти
        ufos.draw(window)
        bullets.draw(window)  #відрисовка куль
    else:
        result_text.draw()
    lost_text.draw()
    score_text.draw()
    display.update()
    clock.tick(FPS)