import pygame
import sys
import random

WHITE = (255, 255, 255)
coin_count = 0
gm_flag = False
payed_des = False
payed_for = False
high_score = 0
current_score = 0


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, frame_change_delay=3):
        super().__init__(all_sprites)
        self.frames = []
        self.original_frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.jump_flag = False
        self.jump_count = 15
        self.resize_flag = False
        self.resize_duration = 30
        self.resize_counter = 0
        self.falling_flag = False
        self.dino_speed = 5
        self.obstacle_appear_time = 0

        self.frame_change_delay = frame_change_delay
        self.current_delay = 0

    def cut_sheet(self, sheet, columns, rows):
        frame_width = sheet.get_width() // columns
        frame_height = sheet.get_height() // rows

        for j in range(rows):
            for i in range(columns):
                frame_location = (frame_width * i, frame_height * j)
                original_frame = sheet.subsurface(pygame.Rect(frame_location, (frame_width, frame_height)))
                self.original_frames.append(original_frame)
                resized_frame = pygame.transform.scale(original_frame, (50, 70))
                self.frames.append(resized_frame)

    def update(self):
        if self.jump_flag or self.falling_flag:
            self.cur_frame = 0
            self.image = pygame.transform.scale(pygame.image.load("ninja_jump.png"), (50, 50))
        elif self.resize_flag:
            self.cur_frame = 0
            self.image = pygame.transform.scale(pygame.image.load("ninja_slide.png"), (70, 25))
        else:
            if self.current_delay <= 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = pygame.transform.scale(self.frames[self.cur_frame], (50, 70))
                self.current_delay = self.frame_change_delay
            else:
                self.current_delay -= 1

        if not self.jump_flag and not self.resize_flag:
            self.image = self.frames[self.cur_frame]


def reset_game():
    global dino_sprite, obstacle_group, star_group, gm_flag, current_score
    dino_sprite.kill()
    for particle in all_sprites:
        if isinstance(particle, Particle):
            particle.kill()
    dino_sprite = AnimatedSprite(dino_sheet, columns=3, rows=2, x=100, y=SCREEN_HEIGHT - 100)
    obstacle_group.empty()
    star_group.empty()
    gm_flag = False
    current_score = 0
    dino_sprite.obstacle_appear_time = 0


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(star_group)
        self.image = pygame.image.load("star.png")
        self.rect = self.image.get_rect(topleft=(x, y - 40))  # Располагаем звезду над препятствием

    def update(self):
        self.rect.x -= dino_sprite.dino_speed + 1  # двигаем звезду вместе с динозавром
        if self.rect.x + self.rect.width < 0:
            self.kill()  # удаление звезды, если она выходит за пределы экрана


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width=30, height=30, color=WHITE):
        super().__init__(obstacle_group)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.star = Star(x, y)  # Создание экземпляра класса Star при создании препятствия
        self.animation_timer = 0

    def update(self):
        global gm_flag
        self.rect.x -= dino_sprite.dino_speed + 1  # двигаем препятствие вместе с динозавром
        self.star.update()  # обновление позиции звезды

        # Если столкновение со звездой, начинаем анимацию
        if pygame.sprite.collide_rect(self.star, dino_sprite):
            if not self.animation_timer:
                create_particles((self.star.rect.x, self.star.rect.y))
                global coin_count
                coin_count += 1
                self.star.kill()
                self.animation_timer = pygame.time.get_ticks() + 500  # Устанавливаем таймер на 0.5 секунды
        if gm_flag:
            game_over_menu()
        # Проверяем, истек ли таймер
        if self.animation_timer and pygame.time.get_ticks() >= self.animation_timer:
            self.animation_timer = 0  # Обнуляем таймер
        # Обработка столкновения с динозавром
        elif pygame.sprite.collide_rect(self, dino_sprite):
            # Воспроизведение анимации частиц при столкновении с препятствием
            print("Игра окончена!")
            gm_flag = True


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, speed):
        self.dx = -speed
        self.dy = 0


# Определение класса для частиц
class Particle(pygame.sprite.Sprite):
    fire = [pygame.transform.scale(pygame.image.load("star.png"), (scale, scale)) for scale in (5, 10, 20)]

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = [dx, dy]
        self.gravity = 0.5

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]


pygame.init()

# Определение цветов
BLACK = (0, 0, 0)

# Размеры экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ninja_runner")

# Определение группы спрайтов
all_sprites = pygame.sprite.Group()

# Создание группы для препятствий
obstacle_group = pygame.sprite.Group()

# Создание группы для звезд
star_group = pygame.sprite.Group()

# Загрузка анимированного изображения динозавра
dino_sheet = pygame.image.load("pygame-8-1.png")

# Создание объекта AnimatedSprite для динозавра
dino_sprite = AnimatedSprite(dino_sheet, columns=3, rows=2, x=100, y=SCREEN_HEIGHT - 100)


def spawn_obstacle(mode):
    obstacle_x = SCREEN_WIDTH
    obstacle_y = SCREEN_HEIGHT - 100
    if random.choice([True, False, False]):
        if mode == "easy":
            color = (138, 43, 226)
        elif mode == "medium":
            color = (255, 165, 0)
        elif mode == "hard":
            color = (34, 139, 34)
        obstacle = Obstacle(obstacle_x, obstacle_y, width=30, height=70, color=color)
    else:
        if mode == "easy":
            color = (138, 43, 226)
            # Оранжевый цвет для пустыни
        elif mode == "medium":
            color = (255, 165, 0)
            # Зеленый цвет для леса
        elif mode == "hard":
            color = (34, 139, 34)
            # Фиолетовый цвет для Японии
        obstacle = Obstacle(obstacle_x, obstacle_y, width=30, height=30, color=color)
    return obstacle


# Определение функции для создания частиц
def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def main_menu():
    global payed_for, payed_des, coin_count
    font = pygame.font.Font(None, 36)
    title = font.render("Ninja runner", True, WHITE)
    mode_text = font.render("Выберите уровень:", True, WHITE)

    easy_button = pygame.Rect(300, 200, 200, 50)
    medium_button = pygame.Rect(300, 300, 200, 50)
    hard_button = pygame.Rect(300, 400, 200, 50)

    lock_rect_desert = pygame.Rect(530, 300, 30, 30)
    lock_rect_forest = pygame.Rect(530, 400, 30, 30)
    lock_image = pygame.image.load("lock.png")
    unlock_text = font.render("16 монет", True, WHITE)
    unlock_text1 = font.render("50 монет", True, WHITE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if easy_button.collidepoint(mouse_pos):
                    reset_game()
                    game_loop('easy')
                elif medium_button.collidepoint(mouse_pos) and (coin_count >= 16 or payed_des):
                    if not payed_des:
                        coin_count -= 16
                        payed_des = True
                        lock_rect_desert = None
                        unlock_text = None
                    reset_game()
                    game_loop('medium')
                elif hard_button.collidepoint(mouse_pos) and (coin_count >= 16 or payed_for):
                    if not payed_for:
                        coin_count -= 50
                        payed_for = True
                        lock_rect_forest = None
                        unlock_text = None
                    reset_game()
                    game_loop('hard')

        screen.fill(BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        screen.blit(mode_text, (SCREEN_WIDTH // 2 - mode_text.get_width() // 2, 150))

        star_image = pygame.image.load("star.png")
        screen.blit(star_image, (10, 10))
        coin_text = font.render(f"Монеты: {coin_count}", True, WHITE)
        screen.blit(coin_text, (40, 10))

        pygame.draw.rect(screen, WHITE, easy_button)
        pygame.draw.rect(screen, WHITE, medium_button)
        pygame.draw.rect(screen, WHITE, hard_button)

        if not payed_des:
            screen.blit(lock_image, (lock_rect_desert.x, lock_rect_desert.y))
            screen.blit(unlock_text, (lock_rect_desert.x + 60, lock_rect_desert.y + 10))
        if not payed_for:
            screen.blit(lock_image, (lock_rect_forest.x, lock_rect_forest.y))
            screen.blit(unlock_text1, (lock_rect_forest.x + 60, lock_rect_forest.y + 10))

        easy_text = font.render("Япония", True, BLACK)
        medium_text = font.render("Пустыня", True, BLACK)
        hard_text = font.render("Лес", True, BLACK)

        screen.blit(easy_text, (easy_button.x + easy_button.width // 2 - easy_text.get_width() // 2,
                                easy_button.y + easy_button.height // 2 - easy_text.get_height() // 2))
        screen.blit(medium_text, (medium_button.x + medium_button.width // 2 - medium_text.get_width() // 2,
                                  medium_button.y + medium_button.height // 2 - medium_text.get_height() // 2))
        screen.blit(hard_text, (hard_button.x + hard_button.width // 2 - hard_text.get_width() // 2,
                                hard_button.y + hard_button.height // 2 - hard_text.get_height() // 2))

        pygame.display.flip()


def game_over_menu():
    font = pygame.font.Font(None, 36)
    game_over_text = font.render("Игра окончена!", True, WHITE)
    return_to_menu_button = pygame.Rect(200, 300, 400, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if return_to_menu_button.collidepoint(mouse_pos):
                    main_menu()

        screen.fill(BLACK)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 50))

        star_image = pygame.image.load("star.png")
        screen.blit(star_image, (10, 10))
        coin_text = font.render(f"Монеты: {coin_count}", True, WHITE)
        screen.blit(coin_text, (40, 10))

        pygame.draw.rect(screen, WHITE, return_to_menu_button)
        return_to_menu_text = font.render("Вернуться в главное меню", True, BLACK)
        screen.blit(return_to_menu_text, (return_to_menu_button.x + return_to_menu_button.width //
                                          2 - return_to_menu_text.get_width() // 2,
                                          return_to_menu_button.y + return_to_menu_button.height //
                                          2 - return_to_menu_text.get_height() // 2))

        pygame.display.flip()


def game_loop(mode):
    global current_score, high_score
    clock = pygame.time.Clock()

    if mode == "easy":
        background_image = pygame.image.load("japan.jpg")
    elif mode == "medium":
        background_image = pygame.image.load("desert.jpg")
    elif mode == "hard":
        background_image = pygame.image.load("forest.jpg")
    if mode == "easy":
        color = (138, 43, 226)
        # Оранжевый цвет для пустыни
    elif mode == "medium":
        color = (255, 165, 0)
        # Зеленый цвет для леса
    elif mode == "hard":
        color = (34, 139, 34)
    font = pygame.font.Font(None, 36)
    camera = Camera()
    while True:
        screen.fill(BLACK)
        screen.blit(background_image, (0, 0))
        camera.update(0)
        for sprite in all_sprites:
            camera.apply(sprite)
        pygame.draw.rect(screen, color, (0, SCREEN_HEIGHT - 30, SCREEN_WIDTH, SCREEN_HEIGHT))
        obstacle_appear_interval = random.randint(70, 200)
        current_score += 0.5
        if current_score > high_score:
            high_score = current_score
        star_image = pygame.image.load("star.png")
        screen.blit(star_image, (10, 10))
        coin_text = font.render(f"Монеты: {coin_count}", True, WHITE)
        screen.blit(coin_text, (40, 10))
        current_score_text = font.render(f"Счёт: {int(current_score)}", True, WHITE)
        screen.blit(current_score_text, (SCREEN_WIDTH - current_score_text.get_width() - 20, 30))
        high_score_text = font.render(f"Рекорд: {int(high_score)}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH - current_score_text.get_width() - 57, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not dino_sprite.jump_flag and not dino_sprite.resize_flag \
                and not dino_sprite.falling_flag:
            dino_sprite.jump_flag = True
            dino_sprite.jump_count = 15
        if keys[pygame.K_DOWN] and not dino_sprite.resize_flag and not dino_sprite.jump_flag \
                and not dino_sprite.falling_flag:
            dino_sprite.resize_flag = True
            dino_sprite.rect.y = SCREEN_HEIGHT - 55
        elif not keys[pygame.K_DOWN] and dino_sprite.resize_flag:
            dino_sprite.rect.y = SCREEN_HEIGHT - 100
            dino_sprite.resize_flag = False
        if dino_sprite.jump_flag:
            dino_sprite.rect.y -= 10
            dino_sprite.jump_count -= 1
            if dino_sprite.jump_count == 0:
                dino_sprite.jump_flag = False
        if not dino_sprite.jump_flag and dino_sprite.rect.y < SCREEN_HEIGHT - 100:
            dino_sprite.rect.y += 5
            dino_sprite.falling_flag = True
        else:
            dino_sprite.falling_flag = False
        current_time = pygame.time.get_ticks() / 1000  # Время в секундах
        if current_time - dino_sprite.obstacle_appear_time >= obstacle_appear_interval / 100:
            obstacle = spawn_obstacle(mode)
            obstacle_group.add(obstacle)
            star_group.add(obstacle.star)  # Добавляем звезду в группу звезд
            dino_sprite.obstacle_appear_time = current_time
        obstacle_group.update()
        star_group.update()

        all_sprites.update()
        all_sprites.draw(screen)
        obstacle_group.draw(screen)
        star_group.draw(screen)

        pygame.display.flip()
        clock.tick(70)


if __name__ == "__main__":
    main_menu()
