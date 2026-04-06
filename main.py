import pygame
import sys
import math
import random
import os

# Инициализация
pygame.init()

WIDTH, HEIGHT = 900, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐬 Подводные друзья: Доброе исследование океана")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Arial", 42, bold=True)
font_med = pygame.font.SysFont("Arial", 28, bold=True)
font_text = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18, bold=True)

WHITE = (255, 255, 255)
YELLOW = (255, 220, 100)

# Данные персонажей
NPC_DATA = {
    1: {
        "name": "Осьминог Оливер", 
        "lines": [
            "Привет, Дельфин! Смотри, сколько у меня щупалец! Целых восемь штук.", 
            "Когда мне страшно, я могу пускать чернильное облако. Но с тобой мне совсем не страшно!",
            "Я очень люблю искать блестящие ракушки на дне. Хочешь поплавать со мной?"
        ]
    },
    2: {
        "name": "Медуза Мия", 
        "lines": [
            "Буль-буль... Знаешь ли ты, что я почти полностью состою из водички?", 
            "У меня нет ни косточек, ни сердечка, но я очень плавно и красиво танцую в воде.",
            "Посмотри, как нежно я свечусь! Это помогает мне общаться с другими медузами."
        ]
    },
    3: {
        "name": "Черепашка Честер", 
        "lines": [
            "Здравствуй, малыш. В океане спешить некуда, вся красота открывается тем, кто плывет медленно.", 
            "Мой прочный панцирь — это мой уютный домик. Я ношу его на своей спинке всю жизнь!",
            "Я путешествовал по всему свету, и этот риф — одно из самых красивых мест."
        ]
    },
    4: {
        "name": "Глубоководный Марти", 
        "lines": [
            "Ой, привет! Здесь, на глубине, бывает очень темно. Хорошо, что у меня есть свой природный фонарик на голове!", 
            "Не суди меня по внешности: зубы у меня большие, но я очень добрый и люблю сказки.",
            "На самом-самом дне скрыто много удивительных тайн. Когда-нибудь мы их разгадаем."
        ]
    },
    5: {
        "name": "Рыбка-пила Пиппа", 
        "lines": [
            "Какой прекрасный день! Мой нос действительно похож на острую пилу, правда?", 
            "На самом деле я использую его не для драк, а чтобы копать мягкий песочек и искать вкусняшки.",
            "Давай поиграем в прятки в водорослях? Только чур, носом в песок не зарываться!"
        ]
    },
    6: {
        "name": "Электрический угорь Эл", 
        "lines": [
            "Д-д-добрый день! Я не з-з-злой, просто иногда от радости случайно бьюсь током!", 
            "Своим электричеством я мог бы зажечь небольшую лампочку. Здорово, правда?",
            "Давай дружить! Только, чур, не обниматься слишком крепко, а то заискрим!"
        ]
    }
}

# Функции загрузки

def extract_frames(sheet, scale=1.5):
    """Нарезает кадры из горизонтального спрайт-листа."""
    w, h = sheet.get_size()
    frames = []
    frame_w = h  # По опыту спрайтов: ширина кадра равна его высоте
    for x in range(0, w, frame_w):
        frame = sheet.subsurface(pygame.Rect(x, 0, frame_w, h))
        if scale != 1.0:
            frame = pygame.transform.scale(frame, (int(frame_w * scale), int(h * scale)))
        frames.append(frame)
    return frames

def load_npc_animations(folder, scale=1.5):
    """Считывает кадры Walk.png и Idle.png из папки."""
    animations = {"Walk": [], "Idle": []}
    
    # Пытаемся загрузить Walk
    path_walk = os.path.join(folder, "Walk.png")
    if os.path.exists(path_walk):
        try:
            sheet = pygame.image.load(path_walk).convert_alpha()
            animations["Walk"] = extract_frames(sheet, scale)
        except:
            pass

    # Пытаемся загрузить Idle
    path_idle = os.path.join(folder, "Idle.png")
    if os.path.exists(path_idle):
        try:
            sheet = pygame.image.load(path_idle).convert_alpha()
            animations["Idle"] = extract_frames(sheet, scale)
        except:
            pass
            
    # Если Idle отсутствует, используем Walk в качестве Idle и наоборот
    if not animations["Idle"] and animations["Walk"]:
        animations["Idle"] = animations["Walk"]
    if not animations["Walk"] and animations["Idle"]:
        animations["Walk"] = animations["Idle"]
        
    return animations

BG_IMAGE = None
DOLPHIN_IMAGE = None
NPC_ANIMATIONS = {}
NPC_ICONS = {}

HUD_NUMBERS = {}
BUBBLE_IMAGES = []
SEAWEED_IMAGES = []
STATUS_STICKERS = {}

def init_assets():
    global BG_IMAGE, DOLPHIN_IMAGE
    
    # Фон
    try:
        bg = pygame.image.load(os.path.join("assets", "11", "game_background.png")).convert()
        BG_IMAGE = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except:
        BG_IMAGE = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            r = int(20 * (1 - y/HEIGHT) + 10 * (y/HEIGHT))
            g = int(100 * (1 - y/HEIGHT) + 50 * (y/HEIGHT))
            b = int(200 * (1 - y/HEIGHT) + 100 * (y/HEIGHT))
            pygame.draw.line(BG_IMAGE, (r, g, b), (0, y), (WIDTH, y))
            
    # Затемнение на глубине
    dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(int(HEIGHT * 0.6), HEIGHT):
        alpha = int(150 * (y - HEIGHT * 0.6) / (HEIGHT * 0.4))
        pygame.draw.line(dark_overlay, (0, 10, 40, alpha), (0, y), (WIDTH, y))
    BG_IMAGE.blit(dark_overlay, (0, 0))
            
    # Дельфин
    try:
        d_img = pygame.image.load(os.path.join("assets", "11", "dolphin.png")).convert_alpha()
        DOLPHIN_IMAGE = pygame.transform.scale(d_img, (100, 100))
    except:
        DOLPHIN_IMAGE = pygame.Surface((100, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(DOLPHIN_IMAGE, (100, 180, 220), (0, 0, 100, 50))
        pygame.draw.circle(DOLPHIN_IMAGE, WHITE, (80, 15), 5)

    # Загружаем друзей 1-6
    for i in range(1, 7):
        NPC_ANIMATIONS[i] = load_npc_animations(os.path.join("assets", str(i)), scale=2.5)
        
        # Подготовка иконок для Дневника друзей
        if NPC_ANIMATIONS[i]["Idle"]:
            img = NPC_ANIMATIONS[i]["Idle"][0]
        elif NPC_ANIMATIONS[i]["Walk"]:
            img = NPC_ANIMATIONS[i]["Walk"][0]
        else:
            img = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 220, 100), (20, 20), 20)
        
        icon = pygame.transform.scale(img, (50, 50))
        NPC_ICONS[i] = icon

    # HUD Цифры (Папка 7)
    for i in range(10):
        try:
            img = pygame.image.load(os.path.join("assets", "7", f"hud_number_{i}.png")).convert_alpha()
            HUD_NUMBERS[str(i)] = pygame.transform.scale(img, (32, 40))
        except:
            pass

    # Пузыри (Папка 8)
    for b_name in ["bubble_a.png", "bubble_b.png", "bubble_c.png"]:
        try:
            img = pygame.image.load(os.path.join("assets", "8", b_name)).convert_alpha()
            BUBBLE_IMAGES.append(pygame.transform.scale(img, (18, 18)))
        except:
            pass

    # Водоросли (Папка 9)
    bases = [
        "seaweed_grass_a", "seaweed_grass_b", "seaweed_green_a", "seaweed_green_b",
        "seaweed_green_c", "seaweed_green_d", "seaweed_orange_a", "seaweed_orange_b",
        "seaweed_pink_a", "seaweed_pink_b", "seaweed_pink_c", "seaweed_pink_d"
    ]
    for b in bases:
        try:
            img = pygame.image.load(os.path.join("assets", "9", f"{b}.png")).convert_alpha()
            outline = pygame.image.load(os.path.join("assets", "9", f"{b}_outline.png")).convert_alpha()
            # Немного увеличим
            img = pygame.transform.scale(img, (int(img.get_width()*1.4), int(img.get_height()*1.4)))
            outline = pygame.transform.scale(outline, (int(outline.get_width()*1.4), int(outline.get_height()*1.4)))
            SEAWEED_IMAGES.append({"img": img, "outline": outline})
        except:
            pass

    # Стикеры статусов (Папка 10)
    for t in [100, 300, 500, 1000]:
        try:
            img = pygame.image.load(os.path.join("assets", "10", f"status_{t}.png")).convert_alpha()
            STATUS_STICKERS[t] = pygame.transform.scale(img, (200, 200))
        except:
            pass

# Вспомогательная функция для отрисовки текста

def draw_text_wrapped(surface, text, color, rect, font, line_spacing=5):
    """Рисует текст с переносом по словам внутри заданного rect."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        fw, fh = font.size(' '.join(current_line))
        if fw > rect[2]:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    y = rect[1]
    for line in lines:
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (rect[0], y))
        y += fh + line_spacing

# Классы игры

class BubbleRing:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 45
        self.particles = []
        for _ in range(16):
            angle = random.uniform(0, 2 * math.pi)
            img = random.choice(BUBBLE_IMAGES) if BUBBLE_IMAGES else None
            self.particles.append({
                "x": math.cos(angle) * self.radius,
                "y": math.sin(angle) * self.radius,
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.8, -0.2),
                "size": random.randint(3, 8),
                "img": img
            })
        self.active = True

    def update(self, dt, bg_speed):
        self.x -= bg_speed
        for p in self.particles:
            p["y"] += p["vy"] * dt * 0.06
            p["x"] += p["vx"] * dt * 0.06

    def draw(self, surface):
        if not self.active: return
        for p in self.particles:
            px = int(self.x + p["x"])
            py = int(self.y + p["y"])
            if p["img"]:
                surface.blit(p["img"], p["img"].get_rect(center=(px, py)))
            else:
                pygame.draw.circle(surface, (150, 255, 200), (px, py), p["size"])
                pygame.draw.circle(surface, WHITE, (px - 1, py - 1), 1)

class ForegroundLayer:
    def __init__(self):
        self.plants = []
        for i in range(20):
            x = i * (WIDTH * 1.2 / 20) + random.randint(-40, 40)
            if SEAWEED_IMAGES:
                data = random.choice(SEAWEED_IMAGES)
                self.plants.append({
                    "x": x,
                    "y": HEIGHT - data["img"].get_height() + random.randint(10, 40),
                    "img": data["img"],
                    "outline": data["outline"],
                    "w": data["img"].get_width(),
                    "h": data["img"].get_height()
                })
            else:
                self.plants.append({"x": x, "h": random.randint(40, 110), "poly": True})
            
    def update_and_draw(self, surface, dt, base_speed, dolphin):
        speed = base_speed * 1.5
        for p in self.plants:
            p["x"] -= speed
            width = p.get("w", 50)
            if p["x"] < -width:
                max_x = max([plant["x"] for plant in self.plants])
                p["x"] = max(WIDTH + width, max_x + random.randint(40, 100))
                
            if p.get("poly"):
                rx, h = int(p["x"]), p["h"]
                pygame.draw.polygon(surface, (5, 20, 35, 230), [(rx, HEIGHT), (rx - 10, HEIGHT - h), (rx + 10, HEIGHT - h)])
            else:
                surface.blit(p["img"], (int(p["x"]), int(p["y"])))
                
                # Сияние контура
                if dolphin.ocean_credit >= 300:
                    px_center = p["x"] + p["w"]/2
                    py_center = p["y"] + p["h"]/2
                    dist = math.hypot(dolphin.x - px_center, dolphin.y - py_center)
                    if dist < 250:
                        alpha = int(255 * (1 - dist/250))
                        p["outline"].set_alpha(alpha)
                        surface.blit(p["outline"], (int(p["x"]), int(p["y"])))
                        p["outline"].set_alpha(255) # reset


class Dolphin:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.vx = 0.0
        self.vy = 0.0
        self.accel = 0.4
        self.base_accel = 0.4
        self.friction = 0.9
        
        self.facing_right = True
        self.image = DOLPHIN_IMAGE
        self.rect = self.image.get_rect()
        self.rotation = 0.0
        
        self.is_flipping = False
        self.flip_angle = 0.0
        self.particles = []
        self.trick_event = False
        
        self.speed_buff_timer = 0
        self.echo_active = False
        self.echo_timer = 0
        self.echo_radius = 0
        
        # Social Credit
        self.ocean_credit = 0
        self.status = ""
        self.status_timer = 0
        self.medusa_glow_timer = 0
        self.pending_achievement = None
        
        self.status_thresholds = {
            100: "НОВЫЙ СТАТУС: ДОБРЫЙ СОСЕД!",
            300: "НОВЫЙ СТАТУС: ХРАНИТЕЛЬ РИФА!",
            500: "НОВЫЙ СТАТУС: ГЕРОЙ ОКЕАНА!",
            1000: "НОВЫЙ СТАТУС: ЛЕГЕНДА МОРЕЙ!"
        }
        self.achieved_thresholds = []
        self.score_cooldowns = {}

    def add_credit(self, amount):
        self.ocean_credit += amount
        for limit in sorted(self.status_thresholds.keys()):
            if self.ocean_credit >= limit and limit not in self.achieved_thresholds:
                self.achieved_thresholds.append(limit)
                self.status = self.status_thresholds[limit]
                self.pending_achievement = limit

    def update(self, keys, dt, in_dialogue=False):
        self.trick_event = False
        if not in_dialogue:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
                self.facing_right = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
                
            # Нормализация для диагоналей
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707

            if self.speed_buff_timer > 0:
                self.speed_buff_timer -= dt
                self.accel = self.base_accel * 2.0
            else:
                self.accel = self.base_accel

            self.vx += dx * self.accel * dt * 0.06
            self.vy += dy * self.accel * dt * 0.06
            
            # Эмоции: сальто по Shift
            if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.is_flipping:
                self.is_flipping = True
                self.flip_angle = 0.0
                self.trick_event = True
                
            # Эхолокация по E
            if keys[pygame.K_e] and not self.echo_active and self.echo_timer <= 0:
                self.echo_active = True
                self.echo_radius = 0
                self.echo_timer = 2000

        if self.echo_active:
            self.echo_radius += 12 * dt * 0.06
            if self.echo_radius > 600:
                self.echo_active = False
        if self.echo_timer > 0:
            self.echo_timer -= dt

        if self.status_timer > 0:
            self.status_timer -= dt
        if self.medusa_glow_timer > 0:
            self.medusa_glow_timer -= dt

        if self.is_flipping:
            self.flip_angle += 15 * dt * 0.06
            if self.flip_angle >= 360:
                self.flip_angle = 0.0
                self.is_flipping = False
            # Спавн пузырьков
            if random.random() < 0.3:
                px = self.x + random.uniform(-30, 30)
                py = self.y + random.uniform(-20, 20)
                pr_size = random.uniform(2, 6)
                self.particles.append([px, py, pr_size])

        # Обновление пузырьков
        for p in self.particles[:]:
            p[1] -= 2 * dt * 0.06 # поднимаются вверх
            if p[1] < -10:
                self.particles.remove(p)

        # Трение
        self.vx *= self.friction
        self.vy *= self.friction

        # Применяем скорость
        self.x += self.vx * dt * 0.06
        self.y += self.vy * dt * 0.06

        # Границы экрана
        half_w = self.rect.width / 2
        half_h = self.rect.height / 2
        self.x = max(half_w, min(WIDTH - half_w, self.x))
        self.y = max(half_h, min(HEIGHT - half_h, self.y))
        
        self.rect.center = (int(self.x), int(self.y))
        
        # Легкий наклон дельфина по ходу движения
        target_rot = -self.vy * 3
        if not self.facing_right:
            target_rot = -target_rot
        self.rotation += (target_rot - self.rotation) * 0.1 * dt * 0.06

    def draw(self, surface):
        if self.medusa_glow_timer > 0:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            glow_radius = int(self.rect.width * 1.2)
            glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (150, 255, 255, int(120 * pulse)), (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))
            
        # Волны эхолокации
        if self.echo_active:
            alpha = max(0, 255 - int(self.echo_radius / 600 * 255))
            pulse = pygame.Surface((int(self.echo_radius*2), int(self.echo_radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(pulse, (150, 200, 255, alpha), (int(self.echo_radius), int(self.echo_radius)), int(self.echo_radius), max(1, int(10 * alpha/255)))
            surface.blit(pulse, (int(self.x - self.echo_radius), int(self.y - self.echo_radius)))
            
        # Отрисовка пузырьков
        for p in self.particles:
            pygame.draw.circle(surface, (200, 230, 255), (int(p[0]), int(p[1])), int(p[2]))
            pygame.draw.circle(surface, (255, 255, 255), (int(p[0]) - 1, int(p[1]) - 1), 1)

        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        final_rot = self.rotation
        if self.is_flipping:
            final_rot += self.flip_angle * (-1 if self.facing_right else 1)
            
        rot_img = pygame.transform.rotate(img, final_rot)
        surface.blit(rot_img, rot_img.get_rect(center=self.rect.center))

    def get_interaction_point(self):
        return (self.x, self.y)


class FriendlyNPC:
    def __init__(self, npc_id, start_x, start_y):
        self.id = npc_id
        self.x = start_x
        self.y = start_y
        self.origin_y = start_y
        
        data = NPC_DATA.get(npc_id, {"name": "Неизвестный друг", "lines": ["Привет!"]})
        self.name = data["name"]
        self.lines = data["lines"]
        self.current_lines = self.lines.copy()
        
        self.animations = NPC_ANIMATIONS[npc_id]
        self.state = "Walk"  # Walk когда плавает, Idle когда разговаривает
        self.reaction_text = ""
        self.reaction_timer = 0
        self.frame_index = 0.0
        self.anim_speed = 0.1
        
        self.speed = random.uniform(0.5, 1.5)
        self.wobble = random.uniform(0, 100)
        
        # Направление (случайное)
        self.facing_right = random.choice([True, False])
        
        if self.animations["Walk"]:
            self.rect = self.animations["Walk"][0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 70, 70)

    def update(self, dt, in_dialogue=False):
        if in_dialogue:
            if self.state != "Idle":
                self.state = "Idle"
                self.frame_index = 0.0
            # Смягченная анимация покоя
            self.wobble += 0.02 * dt * 0.06
            self.y = self.origin_y + math.sin(self.wobble) * 5
        else:
            if self.state != "Walk":
                self.state = "Walk"
                self.frame_index = 0.0
                
            # Зацикленное плавание от края до края экрана
            self.wobble += 0.05 * dt * 0.06
            self.y = self.origin_y + math.sin(self.wobble) * 15
            
            direction = 1 if self.facing_right else -1
            self.x += self.speed * direction * dt * 0.06
            
            # Разворот у границ
            if self.x > WIDTH + 100:
                self.facing_right = False
            elif self.x < -100:
                self.facing_right = True

        # Обновление кадра
        frames = self.animations.get(self.state, [])
        if frames:
            self.frame_index += self.anim_speed * dt * 0.06
            if self.frame_index >= len(frames):
                self.frame_index = 0.0
                
        self.rect.center = (int(self.x), int(self.y))
        
        if self.reaction_timer > 0:
            self.reaction_timer -= dt

    def draw(self, surface, show_prompt=False):
        frames = self.animations.get(self.state, [])
        if frames:
            idx = int(self.frame_index) % len(frames)
            img = frames[idx]
            
            # По умолчанию все спрайты смотрят влево. Переворачиваем, если идем вправо.
            if self.facing_right:
                img = pygame.transform.flip(img, True, False)
                
            surface.blit(img, img.get_rect(center=(int(self.x), int(self.y))))
        else:
            # Заглушка, если нет графики
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 35)
            
        # Рисуем пульсирующую подсказку над NPC
        if show_prompt:
            alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 200 + 55)
            # Тень
            prompt_shadow = font_small.render("[ПРОБЕЛ]: поговорить", True, (20,20,50))
            prompt_shadow.set_alpha(alpha)
            surface.blit(prompt_shadow, (self.x - prompt_shadow.get_width()//2 + 2, self.y - 70 + 2))
            
            prompt = font_small.render("[ПРОБЕЛ]: поговорить", True, WHITE)
            prompt.set_alpha(alpha)
            surface.blit(prompt, (self.x - prompt.get_width()//2, self.y - 70))
            
        if self.reaction_timer > 0 and self.reaction_text:
            text_surf = font_small.render(self.reaction_text, True, (255, 220, 100))
            bg_rect = text_surf.get_rect(center=(int(self.x), int(self.y - 90)))
            pygame.draw.rect(surface, (0, 0, 0, 150), bg_rect.inflate(10, 10), border_radius=5)
            surface.blit(text_surf, bg_rect)


# Диалоговое Окно

def draw_dialogue_box(surface, speaker_name, text):
    box_w, box_h = WIDTH - 80, 160
    box_x, box_y = 40, HEIGHT - 180
    
    # Полупрозрачная подложка
    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(box, (20, 50, 120, 210), box.get_rect(), border_radius=20)
    pygame.draw.rect(box, (150, 220, 255, 255), box.get_rect(), 4, border_radius=20)
    surface.blit(box, (box_x, box_y))
    
    # Имя NPC
    name_surf = font_med.render(speaker_name, True, YELLOW)
    surface.blit(name_surf, (box_x + 30, box_y + 20))
    
    # Линия разделения
    pygame.draw.line(surface, (100, 180, 255), (box_x + 30, box_y + 60), (box_x + box_w - 30, box_y + 60), 2)
    
    # Текст диалога с переносами
    text_rect = [box_x + 30, box_y + 80, box_w - 60, box_h - 100]
    draw_text_wrapped(surface, text, WHITE, text_rect, font_text, line_spacing=5)
    
    # Подсказка для продолжения
    alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255)
    next_txt = font_small.render("ENTER или ПРОБЕЛ ->", True, (180, 230, 255))
    next_txt.set_alpha(alpha)
    surface.blit(next_txt, (box_x + box_w - 220, box_y + box_h - 35))


# Главный цикл
def main():
    init_assets()

    dolphin = Dolphin()
    
    # Черепаха и Медуза сверху, Монстр и Угорь снизу
    npcs = [
        FriendlyNPC(1, 150, 380),   # Осьминог
        FriendlyNPC(2, 700, 110),   # Медуза сверху
        FriendlyNPC(3, 400, 90),    # Черепаха у поверхности
        FriendlyNPC(4, 200, 530),   # Глубоководный (внизу)
        FriendlyNPC(5, 750, 400),   # Рыбка-пила
        FriendlyNPC(6, 500, 500),   # Угорь (внизу)
    ]

    state = "play" # "play" или "dialogue"
    met_friends = set() # Дневник друзей
    current_npc = None
    dialogue_index = 0
    space_pressed = False
    enter_pressed = False

    # Переменные для бесконечного параллакс-фона
    bg_x1 = 0
    bg_x2 = WIDTH
    
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    foreground = ForegroundLayer()
    rings = []
    ring_spawn_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        keys = pygame.key.get_pressed()
        is_space = keys[pygame.K_SPACE]
        is_enter = keys[pygame.K_RETURN]
        
        # Защита от "залипания" клавиши
        space_just_pressed = is_space and not space_pressed
        enter_just_pressed = is_enter and not enter_pressed
        
        space_pressed = is_space
        enter_pressed = is_enter

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Обновление логики
        nearest_npc = None
        min_dist = 140 # Дистанция взаимодействия

        # Ищем ближайшего NPC, чтобы показать подсказку (только в режиме play)
        if state == "play":
            for npc in npcs:
                d = math.hypot(npc.x - dolphin.x, npc.y - dolphin.y)
                if d < min_dist:
                    nearest_npc = npc
                    min_dist = d

            # Реакция на трюк дельфина
            if dolphin.trick_event:
                for npc in npcs:
                    if math.hypot(npc.x - dolphin.x, npc.y - dolphin.y) < 200:
                        if npc not in dolphin.score_cooldowns or pygame.time.get_ticks() - dolphin.score_cooldowns[npc] > 2000:
                            npc.reaction_text = "Вау, какой классный трюк!"
                            npc.reaction_timer = 2000
                            dolphin.add_credit(5)
                            dolphin.score_cooldowns[npc] = pygame.time.get_ticks()

            # Если нажали пробел около друга -> начинаем разговор
            if space_just_pressed and nearest_npc:
                state = "dialogue"
                current_npc = nearest_npc
                dialogue_index = 0
                met_friends.add(current_npc.id)
                
                if dolphin.ocean_credit < 50:
                    current_npc.current_lines = ["Привет.", "Извини, я немного занят!"]
                else:
                    current_npc.current_lines = current_npc.lines.copy()
                    if dolphin.ocean_credit >= 300:
                        if current_npc.id == 3: # turtle
                            dolphin.speed_buff_timer += 5000 
                            current_npc.current_lines.append("Держи мою магическую скорость океана, спаситель!")
                        elif current_npc.id == 2: # medusa
                            dolphin.medusa_glow_timer = 15000 
                            current_npc.current_lines.append("Я подарю тебе частичку своего света в темноте!")
                            
                dolphin.add_credit(5)
                
                # Поворачиваем дельфина и NPC лицом друг к другу
                if current_npc.x > dolphin.x:
                    dolphin.facing_right = True
                    current_npc.facing_right = False
                else:
                    dolphin.facing_right = False
                    current_npc.facing_right = True
        
        elif state == "dialogue":
            # Разговор продолжается. Переключение реплик по ПРОБЕЛУ или ENTER
            if space_just_pressed or enter_just_pressed:
                dialogue_index += 1
                if dialogue_index >= len(current_npc.current_lines):
                    # Фразы закончились, возвращаемся в игру
                    state = "play"
                    current_npc = None
        elif state == "achievement":
            achievement_timer -= dt
            if achievement_timer <= 0:
                state = "play"

        if dolphin.pending_achievement is not None:
            state = "achievement"
            achievement_id = dolphin.pending_achievement
            achievement_timer = 3000
            dolphin.pending_achievement = None

        if state != "achievement":
            # Обновляем дельфина и других сущностей
            in_dialogue = (state == "dialogue")
            dolphin.update(keys, dt, in_dialogue=in_dialogue)
            
            for npc in npcs:
                is_this_npc_talking = (npc == current_npc)
                npc.update(dt, in_dialogue=in_dialogue)

            # Обновляем бесконечный фон
            bg_speed = 1.0 * dt * 0.06
            bg_x1 -= bg_speed
            bg_x2 -= bg_speed

            if bg_x1 <= -WIDTH:
                bg_x1 = bg_x2 + WIDTH
            if bg_x2 <= -WIDTH:
                bg_x2 = bg_x1 + WIDTH

            # Логика колец
            ring_spawn_timer -= dt
            if ring_spawn_timer <= 0:
                rings.append(BubbleRing(WIDTH + 50, random.randint(150, HEIGHT - 150)))
                ring_spawn_timer = random.randint(3000, 7000)
                
            for r in rings[:]:
                r.update(dt, bg_speed * 1.2)
                if r.active and math.hypot(dolphin.x - r.x, dolphin.y - r.y) < r.radius:
                    r.active = False
                    dolphin.is_flipping = True
                    dolphin.flip_angle = 0.0
                    dolphin.speed_buff_timer = 3000
                    dolphin.add_credit(10)
                if r.x < -100:
                    rings.remove(r)
        else:
            bg_speed = 0

        # Отрисовка промежуточного экрана (game_surface)
        game_surface.blit(BG_IMAGE, (int(bg_x1), 0))
        game_surface.blit(BG_IMAGE, (int(bg_x2), 0))

        for r in rings:
            r.draw(game_surface)

        for npc in npcs:
            show_prompt = (npc == nearest_npc and state == "play")
            npc.draw(game_surface, show_prompt=show_prompt)

        dolphin.draw(game_surface)
        
        # Передний план (параллакс)
        foreground.update_and_draw(game_surface, dt, bg_speed, dolphin)
        
        # Масштабирование при разговоре (Zoom)
        if state == "dialogue" and current_npc is not None:
            zoom_f = 1.25
            sw, sh = int(WIDTH * zoom_f), int(HEIGHT * zoom_f)
            scaled_surf = pygame.transform.smoothscale(game_surface, (sw, sh))
            
            mid_x = (dolphin.x + current_npc.x) / 2
            mid_y = (dolphin.y + current_npc.y) / 2
            
            off_x = WIDTH / 2 - mid_x * zoom_f
            off_y = HEIGHT / 2 - mid_y * zoom_f
            off_x = min(0, max(WIDTH - sw, off_x))
            off_y = min(0, max(HEIGHT - sh, off_y))
            
            screen.blit(scaled_surf, (int(off_x), int(off_y)))
            
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 100))
            screen.blit(dark, (0, 0))
        else:
            screen.blit(game_surface, (0, 0))

        # Отрисовка стрелки эхолокации
        if dolphin.echo_timer > 0 and nearest_npc and state == "play":
            nx, ny = nearest_npc.x, nearest_npc.y
            if nx < 0 or nx > WIDTH or ny < 0 or ny > HEIGHT:
                dx, dy = nx - dolphin.x, ny - dolphin.y
                angle = math.atan2(dy, dx)
                
                arrow_x = max(30, min(WIDTH - 30, dolphin.x + math.cos(angle) * (WIDTH//2 - 50)))
                arrow_y = max(30, min(HEIGHT - 30, dolphin.y + math.sin(angle) * (HEIGHT//2 - 50)))
                
                alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255)
                p1 = (arrow_x + math.cos(angle)*20, arrow_y + math.sin(angle)*20)
                p2 = (arrow_x + math.cos(angle + 2.5)*15, arrow_y + math.sin(angle + 2.5)*15)
                p3 = (arrow_x + math.cos(angle - 2.5)*15, arrow_y + math.sin(angle - 2.5)*15)
                arrow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(arrow_surf, (200, 255, 100, alpha), [p1, p2, p3])
                screen.blit(arrow_surf, (0, 0))

        # Отрисовка диалога поверх всего
        if state == "dialogue" and current_npc is not None:
            text_to_show = current_npc.current_lines[dialogue_index]
            draw_dialogue_box(screen, current_npc.name, text_to_show)

        # Отрисовка "Дневника друзей" в правом верхнем углу
        diary_title = font_small.render("Дневник друзей:", True, WHITE)
        screen.blit(diary_title, (WIDTH - 200, 10))
        
        icon_x = WIDTH - 200
        icon_y = 35
        for i in range(1, 7):
            if i in NPC_ICONS:
                icon_img = NPC_ICONS[i].copy()
                if i not in met_friends:
                    # Делаем иконку темной, если друг еще не встречен
                    icon_img.fill((80, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(icon_img, (icon_x, icon_y))
            icon_x += 55
            if i == 3:
                icon_x = WIDTH - 200
                icon_y += 55

        # Отрисовка HUD "Ocean Credit"
        hud_bg = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, (0, 0, 0, 100), (0, 0, 400, 70), border_bottom_right_radius=30)
        screen.blit(hud_bg, (0, 0))
        
        credit_txt = font_med.render("Ocean Credit:", True, (200, 240, 255))
        screen.blit(credit_txt, (20, 20))
        
        x_offset = 20 + credit_txt.get_width() + 15
        for char in str(int(dolphin.ocean_credit)):
            if char in HUD_NUMBERS:
                img = HUD_NUMBERS[char]
                screen.blit(img, (x_offset, 15))
                x_offset += img.get_width() + 2
                
        # Status text / Achievement Drawer
        if state == "achievement":
            alpha = 255
            scale_pulse = 1.0
            elapsed = 3000 - achievement_timer
            
            if elapsed < 500:
                alpha = int((elapsed / 500) * 255)
            elif elapsed > 2500:
                alpha = int(((3000 - elapsed) / 500) * 255)
                
            scale_pulse = 1.0 + math.sin(elapsed * 0.005) * 0.1
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(150, alpha)))
            screen.blit(overlay, (0, 0))
            
            if achievement_id in STATUS_STICKERS:
                img = STATUS_STICKERS[achievement_id]
                w, h = int(img.get_width() * scale_pulse), int(img.get_height() * scale_pulse)
                scaled_img = pygame.transform.smoothscale(img, (w, h))
                scaled_img.set_alpha(alpha)
                screen.blit(scaled_img, scaled_img.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
            
            stat_surf = font_big.render(dolphin.status, True, (255, 230, 80))
            stat_shadow = font_big.render(dolphin.status, True, (0, 0, 0))
            stat_rect = stat_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
            
            temp = pygame.Surface((stat_rect.width + 10, stat_rect.height + 10), pygame.SRCALPHA)
            temp.blit(stat_shadow, (7, 7))
            temp.blit(stat_surf, (5, 5))
            temp.set_alpha(alpha)
            screen.blit(temp, temp.get_rect(center=(WIDTH//2, HEIGHT//2 + 90)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
