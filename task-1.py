import pygame
import random
import sys
import math

# Initialize Pygame and Font subsystems
pygame.init()
pygame.font.init()

# Game Window Setup
WIDTH, HEIGHT = 420, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird: Up & Down Evolution")

CLOCK = pygame.time.Clock()
FPS = 60

# Palette Definitions (Curated Harmonious HSL colors converted to RGB)
SKY_DAY_TOP = (95, 190, 230)
SKY_DAY_BOT = (180, 235, 250)
GREEN = (70, 180, 55)
DARK_GREEN = (35, 120, 35)
LIGHT_GREEN = (130, 230, 90)
YELLOW = (255, 215, 40)
ORANGE = (255, 140, 30)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GROUND = (210, 170, 90)
GRASS = (90, 200, 70)

# Fonts
FONT = pygame.font.SysFont("Arial", 40, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 22, bold=True)
TINY_FONT = pygame.font.SysFont("Arial", 14, bold=True)


class Particle:
    """Handles aesthetic vector physics particles for feather, smoke, wind, and sparkle trails."""
    def __init__(self, x, y, dx, dy, color, size, life, shape="circle", decay=0.97, gravity=0.04):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.shape = shape
        self.decay = decay
        self.gravity = gravity
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4, 4)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
        self.dx *= self.decay
        self.dy *= self.decay
        self.life -= 1
        self.angle += self.rot_speed

    def draw(self, screen):
        if self.life <= 0:
            return
        ratio = max(0.0, min(1.0, self.life / self.max_life))
        current_size = max(1, int(self.size * ratio))

        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)
        elif self.shape == "sparkle":
            x, y = int(self.x), int(self.y)
            pygame.draw.line(screen, self.color, (x - current_size, y), (x + current_size, y), 2)
            pygame.draw.line(screen, self.color, (x, y - current_size), (x, y + current_size), 2)
        elif self.shape == "feather":
            # Float / drift simulation
            drift = math.sin(self.life * 0.1) * 1.5
            x = int(self.x + drift)
            y = int(self.y)
            rad_angle = math.radians(self.angle)
            lx = int(x + math.cos(rad_angle) * current_size * 2.2)
            ly = int(y + math.sin(rad_angle) * current_size * 1.2)
            pygame.draw.line(screen, self.color, (x, y), (lx, ly), max(1, current_size // 2))
        elif self.shape == "speed_line":
            pygame.draw.line(
                screen, 
                self.color, 
                (int(self.x), int(self.y)), 
                (int(self.x - self.dx * 1.8), int(self.y - self.dy * 1.8)), 
                max(1, current_size // 3)
            )


class BackgroundManager:
    """Manages multi-layered parallax scrolling and transitionary Day-Sunset-Night-Sunrise sky cycles."""
    def __init__(self):
        self.phase = 0  # 0=Day, 1=Sunset, 2=Night, 3=Sunrise
        self.transition = 0.0
        self.star_twinkle = 0.0
        self.stars = [
            (random.randint(0, WIDTH), random.randint(0, HEIGHT - 180), random.uniform(1.2, 3.0))
            for _ in range(35)
        ]

        # Phase Sky Color Gradients
        self.gradients = [
            # Day Sky
            ((95, 190, 230), (180, 235, 250)),
            # Sunset Sky
            ((35, 25, 80), (225, 95, 50)),
            # Night Sky
            ((8, 10, 30), (22, 28, 65)),
            # Sunrise Sky
            ((140, 60, 100), (245, 180, 125))
        ]

        self.sun_moon_colors = [
            (255, 230, 90),   # Sun (Day)
            (255, 120, 40),   # Orange Sun (Sunset)
            (230, 230, 255),  # Moon (Night)
            (255, 205, 110)   # Soft Sun (Sunrise)
        ]

        self.hill1_offset = 0.0
        self.hill2_offset = 0.0

    def update(self, score, speed):
        # Interpolate color transitions based on score
        target_phase = (score // 10) % 4
        if self.phase != target_phase:
            self.transition += 0.015
            if self.transition >= 1.0:
                self.phase = target_phase
                self.transition = 0.0
        else:
            if self.transition > 0.0:
                self.transition -= 0.015
                self.transition = max(0.0, self.transition)

        # Scroll speeds are scaled based on parallax layer depth
        self.hill1_offset = (self.hill1_offset + speed * 0.15) % WIDTH
        self.hill2_offset = (self.hill2_offset + speed * 0.45) % WIDTH
        self.star_twinkle += 0.06

    def get_current_colors(self):
        curr_g = self.gradients[self.phase]
        next_phase = (self.phase + 1) % 4
        next_g = self.gradients[next_phase]

        t = self.transition
        top = (
            int(curr_g[0][0] * (1 - t) + next_g[0][0] * t),
            int(curr_g[0][1] * (1 - t) + next_g[0][1] * t),
            int(curr_g[0][2] * (1 - t) + next_g[0][2] * t)
        )
        bot = (
            int(curr_g[1][0] * (1 - t) + next_g[1][0] * t),
            int(curr_g[1][1] * (1 - t) + next_g[1][1] * t),
            int(curr_g[1][2] * (1 - t) + next_g[1][2] * t)
        )

        curr_sun = self.sun_moon_colors[self.phase]
        next_sun = self.sun_moon_colors[next_phase]
        sun = (
            int(curr_sun[0] * (1 - t) + next_sun[0] * t),
            int(curr_sun[1] * (1 - t) + next_sun[1] * t),
            int(curr_sun[2] * (1 - t) + next_sun[2] * t)
        )

        return top, bot, sun

    def draw_hills(self, screen, offset, spacing, color, y_base, hill_height):
        num_hills = 6
        hill_width = WIDTH // 3 + 70
        for i in range(-1, num_hills + 1):
            cx = int(i * (WIDTH / (num_hills - 1)) - offset)
            cy = y_base + 65
            pygame.draw.ellipse(screen, color, (cx - hill_width // 2, cy - hill_height, hill_width, hill_height * 2))

    def draw(self, screen):
        top, bot, sun_color = self.get_current_colors()

        # Sky Gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(top[0] * (1 - ratio) + bot[0] * ratio)
            g = int(top[1] * (1 - ratio) + bot[1] * ratio)
            b = int(top[2] * (1 - ratio) + bot[2] * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        # Twinkling night stars
        if self.phase in (1, 2, 3):
            alpha_mult = 1.0 if self.phase == 2 else (0.5 if self.phase == 1 else 0.3)
            for star in self.stars:
                twinkle = int(140 + 115 * math.sin(self.star_twinkle + star[2]))
                brightness = max(0, min(255, int(twinkle * alpha_mult)))
                pygame.draw.circle(screen, (brightness, brightness, brightness), (star[0], star[1]), int(star[2] * 0.6 + 0.5))

        # Draw celestial body (Sun or Moon)
        sun_x, sun_y = 330, 90
        if self.phase == 2:  # Moon
            pygame.draw.circle(screen, sun_color, (sun_x, sun_y), 32)
            # Overlay a matching circle offset to form a clean crescent
            pygame.draw.circle(screen, top, (sun_x - 12, sun_y - 4), 30)
        else:  # Sun
            pygame.draw.circle(screen, sun_color, (sun_x, sun_y), 34)
            pygame.draw.circle(screen, (sun_color[0], sun_color[1], sun_color[2]), (sun_x, sun_y), 41, 2)

        # Distant Hills (Layer 1 - slow)
        hill1_color = (int(bot[0] * 0.76), int(bot[1] * 0.76), int(bot[2] * 0.76))
        self.draw_hills(screen, self.hill1_offset, 130, hill1_color, HEIGHT - 180, 50)

        # Midground Hills (Layer 2 - medium)
        hill2_color = (int(bot[0] * 0.56), int(bot[1] * 0.56), int(bot[2] * 0.56))
        self.draw_hills(screen, self.hill2_offset, 90, hill2_color, HEIGHT - 135, 40)

class Cloud:
    """Soft aesthetic clouds drifting in the upper atmosphere."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(30, 200)
        self.speed = random.uniform(0.18, 0.45)
        self.size = random.randint(22, 38)

    def update(self):
        self.x -= self.speed
        if self.x < -120:
            self.x = WIDTH + random.randint(30, 110)
            self.y = random.randint(30, 200)
            self.speed = random.uniform(0.18, 0.45)

    def draw(self, screen):
        # Smooth overlapping circles drawing standard cartoon cloud shapes
        pygame.draw.circle(screen, WHITE, (int(self.x), self.y), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x + 22), self.y + 3), self.size - 4)
        pygame.draw.circle(screen, WHITE, (int(self.x - 22), self.y + 6), self.size - 7)
        pygame.draw.ellipse(screen, WHITE, (self.x - 38, self.y, 80, 25))


class Bird:
    """Upgraded player entity with vector transformations, physics state machine, and powerups."""
    def __init__(self):
        self.x = 85
        self.y = HEIGHT // 2
        self.width = 38
        self.height = 28
        self.target_width = 38
        self.target_height = 28
        self.velocity = 0.0
        self.gravity = 0.44
        self.jump_power = -8.4
        self.wing_angle = 0.0
        self.angle = 0.0

        # Advanced gameplay mechanics
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.exhausted = False
        self.state = "NORMAL"  # "NORMAL", "GLIDING", "DIVING"
        self.shield = 0
        self.invincible_time = 0

    def jump(self):
        self.velocity = self.jump_power
        # Squeeze/Stretch on Jump
        self.width = 32
        self.height = 34

    def update_state(self, holding_up, holding_down):
        self.state = "NORMAL"

        if self.exhausted:
            self.stamina = min(self.max_stamina, self.stamina + 0.45)
            if self.stamina >= 30.0:
                self.exhausted = False
            # Force normal controls when stamina breaks
            holding_up = False
            holding_down = False

        # Glide Mode: user holds UP, bird is falling, and stamina is healthy
        if holding_up and self.velocity > -0.5 and self.stamina > 1.5:
            self.state = "GLIDING"
            self.target_width = 45
            self.target_height = 22
            self.stamina -= 1.35
            if self.stamina <= 0:
                self.stamina = 0.0
                self.exhausted = True
        # Dive Mode: user holds DOWN, and stamina is healthy
        elif holding_down and self.stamina > 2.0:
            self.state = "DIVING"
            self.target_width = 28
            self.target_height = 36
            self.stamina -= 1.75
            if self.stamina <= 0:
                self.stamina = 0.0
                self.exhausted = True
        else:
            self.target_width = 38
            self.target_height = 28
            # Recover stamina during standard flight
            self.stamina = min(self.max_stamina, self.stamina + 0.6)

    def update(self):
        # Ease actual dimensions toward target dimensions (Squash & Stretch animation)
        self.width += (self.target_width - self.width) * 0.18
        self.height += (self.target_height - self.height) * 0.18

        if self.state == "GLIDING":
            self.velocity += self.gravity * 0.22  # Gravity heavily dampened
            self.velocity = min(self.velocity, 1.4)  # Clamp glide fall velocity
            self.wing_angle += 0.08
        elif self.state == "DIVING":
            self.velocity += self.gravity * 1.4 + 0.58  # Rapid diving force
            self.wing_angle += 0.45
        else:
            self.velocity += self.gravity
            self.wing_angle += 0.25

        self.y += self.velocity

        # Smooth flight angle adjustments
        if self.state == "GLIDING":
            target_angle = -14.0
        elif self.state == "DIVING":
            target_angle = 38.0
        else:
            target_angle = max(-30.0, min(70.0, self.velocity * 5.8))

        self.angle += (target_angle - self.angle) * 0.2

        if self.invincible_time > 0:
            self.invincible_time -= 1

    def draw(self, screen):
        # Blinking effect when damaged/invincible
        if self.invincible_time > 0 and (self.invincible_time // 4) % 2 == 0:
            return

        # Vector transformations via rotation-buffer surfaces
        bird_surf = pygame.Surface((70, 70), pygame.SRCALPHA)
        cx, cy = 35, 35
        w, h = int(self.width), int(self.height)
        bx, by = cx - w // 2, cy - h // 2

        # Feather Shadow
        pygame.draw.ellipse(bird_surf, (0, 0, 0, 35), (bx - 2, by + h - 5, w + 4, 9))

        # Main Body
        pygame.draw.ellipse(bird_surf, YELLOW, (bx, by, w, h))
        pygame.draw.ellipse(bird_surf, (225, 160, 15), (bx, by, w, h), 2)

        # Belly Accent
        pygame.draw.ellipse(bird_surf, (255, 245, 140), (bx + w * 0.18, by + h * 0.35, w * 0.6, h * 0.5))

        # Flapping Wing
        wing_w = int(w * 0.44)
        wing_h = int(h * 0.42)
        wing_x = bx + w * 0.12
        wing_y = by + h * 0.35 + math.sin(self.wing_angle) * (4.5 if self.state != "GLIDING" else 1.2)
        pygame.draw.ellipse(bird_surf, ORANGE, (wing_x, wing_y, wing_w, wing_h))
        pygame.draw.ellipse(bird_surf, (200, 90, 20), (wing_x, wing_y, wing_w, wing_h), 2)

        # Big Eye
        eye_r = max(2, int(w * 0.14))
        eye_x = bx + w * 0.72
        eye_y = by + h * 0.28
        pygame.draw.circle(bird_surf, WHITE, (int(eye_x), int(eye_y)), eye_r)
        pygame.draw.circle(bird_surf, BLACK, (int(eye_x + 1), int(eye_y)), max(1, eye_r // 2))

        # Beak
        beak_pts = [
            (bx + w - 3, by + h * 0.38),
            (bx + w + 11, by + h * 0.52),
            (bx + w - 3, by + h * 0.68)
        ]
        pygame.draw.polygon(bird_surf, ORANGE, beak_pts)
        pygame.draw.polygon(bird_surf, (200, 90, 20), beak_pts, 2)

        # Blit rotated bird onto main canvas
        rotated_surf = pygame.transform.rotate(bird_surf, -self.angle)
        new_rect = rotated_surf.get_rect(center=(int(self.x + self.width / 2), int(self.y + self.height / 2)))
        screen.blit(rotated_surf, new_rect.topleft)

        # Glowing Active Shield Bubble
        if self.shield > 0:
            pulse = int(4.5 * math.sin(pygame.time.get_ticks() * 0.012))
            rad = max(w, h) // 2 + 13 + pulse
            s_center = (int(self.x + self.width / 2), int(self.y + self.height / 2))
            
            # Draw semi-transparent shield circle
            shield_surf = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (80, 160, 255, 110), (rad + 2, rad + 2), rad, 2)
            pygame.draw.circle(shield_surf, (130, 200, 255, 45), (rad + 2, rad + 2), rad - 3)
            screen.blit(shield_surf, (s_center[0] - rad - 2, s_center[1] - rad - 2))

    def get_rect(self):
        # Slightly shrink collision boundaries for smoother, fairer gameplay
        return pygame.Rect(self.x + 3, self.y + 2, self.width - 6, self.height - 4)


class Pipe:
    """Obstacles representing industrial green pipes with optional vertical dynamic oscillation."""
    def __init__(self, x, is_moving=False):
        self.x = x
        self.width = 68
        self.gap = 158
        self.speed = 3
        self.top_height = random.randint(90, 310)
        self.bottom_y = self.top_height + self.gap
        self.passed = False

        self.is_moving = is_moving
        self.start_top_height = self.top_height
        self.oscillation_speed = random.uniform(0.014, 0.026)
        self.amplitude = random.randint(35, 70)
        self.tick = random.uniform(0.0, 100.0)

    def update(self):
        self.x -= self.speed
        if self.is_moving:
            self.tick += self.oscillation_speed
            offset = math.sin(self.tick) * self.amplitude
            new_top = self.start_top_height + offset
            # Keep gaps perfectly bounds-safe on height limits
            new_top = max(60, min(HEIGHT - 85 - self.gap - 60, new_top))
            self.top_height = new_top
            self.bottom_y = self.top_height + self.gap

    def draw_pipe_body(self, screen, rect):
        pygame.draw.rect(screen, GREEN, rect)
        # Dynamic metallic pipes vertical highlights
        pygame.draw.rect(screen, LIGHT_GREEN, (rect.x + 8, rect.y, 10, rect.height))
        pygame.draw.rect(screen, (170, 245, 140), (rect.x + 6, rect.y, 2, rect.height))
        pygame.draw.rect(screen, DARK_GREEN, (rect.right - 12, rect.y, 12, rect.height))
        pygame.draw.rect(screen, BLACK, rect, 3)

    def draw(self, screen):
        # Top Pipe components
        top_body = pygame.Rect(self.x, 0, self.width, self.top_height)
        top_cap = pygame.Rect(self.x - 7, self.top_height - 28, self.width + 14, 28)

        # Bottom Pipe components
        bottom_body = pygame.Rect(self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y - 85)
        bottom_cap = pygame.Rect(self.x - 7, self.bottom_y, self.width + 14, 28)

        self.draw_pipe_body(screen, top_body)
        self.draw_pipe_body(screen, top_cap)
        self.draw_pipe_body(screen, bottom_body)
        self.draw_pipe_body(screen, bottom_cap)

    def collide(self, bird):
        if bird.invincible_time > 0:
            return False
        bird_rect = bird.get_rect()
        top_pipe = pygame.Rect(self.x - 7, 0, self.width + 14, self.top_height)
        bottom_pipe = pygame.Rect(self.x - 7, self.bottom_y, self.width + 14, HEIGHT - self.bottom_y - 85)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

    def off_screen(self):
        return self.x + self.width < -10


class Collectible:
    """Floating seed-coins and shields providing score boosters and shielding mechanics."""
    def __init__(self, x, y, item_type="coin"):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.width = 18 if item_type == "coin" else 22
        self.height = 18 if item_type == "coin" else 22
        self.speed = 3
        self.collected = False
        self.bounce_tick = random.uniform(0.0, 100.0)

    def update(self):
        self.x -= self.speed
        self.bounce_tick += 0.05

    def draw(self, screen):
        if self.collected:
            return
        draw_x = int(self.x)
        draw_y = int(self.y + math.sin(self.bounce_tick) * 5.0)

        if self.item_type == "coin":
            # 3D spinning illusion through elliptical scaling
            spin = abs(math.sin(self.bounce_tick * 1.4))
            rw = max(2, int(9 * spin))
            rh = 9
            # Gold body
            pygame.draw.ellipse(screen, (255, 215, 0), (draw_x - rw, draw_y - rh, rw * 2, rh * 2))
            pygame.draw.ellipse(screen, (230, 160, 0), (draw_x - rw, draw_y - rh, rw * 2, rh * 2), 2)
            if rw > 3:
                pygame.draw.circle(screen, WHITE, (draw_x, draw_y), 2)
        elif self.item_type == "shield":
            # Pulsing blue shield bubble
            pulse = int(3 * math.sin(self.bounce_tick * 1.8))
            # Inner core
            pygame.draw.circle(screen, (100, 190, 255), (draw_x, draw_y), 7)
            pygame.draw.circle(screen, WHITE, (draw_x - 2, draw_y - 2), 2)
            # Outer ring
            pygame.draw.circle(screen, (60, 140, 255), (draw_x, draw_y), 11 + pulse, 2)

    def collide(self, bird):
        if self.collected:
            return False
        bird_rect = bird.get_rect()
        dy = math.sin(self.bounce_tick) * 5.0
        item_rect = pygame.Rect(self.x - self.width // 2, self.y + dy - self.height // 2, self.width, self.height)
        return bird_rect.colliderect(item_rect)


class Ground:
    """Seamless scrolling ground layer wrapping automatically."""
    def __init__(self):
        self.x = 0.0
        self.y = HEIGHT - 85
        self.speed = 3

    def update(self):
        self.x -= self.speed
        if self.x <= -WIDTH:
            self.x = 0.0

    def draw(self, screen):
        # Grass Border
        pygame.draw.rect(screen, GRASS, (0, self.y, WIDTH, 18))
        # Dirt Ground
        pygame.draw.rect(screen, GROUND, (0, self.y + 18, WIDTH, 67))

        # Brick Patterns
        for i in range(0, WIDTH * 2, 35):
            px = int(self.x + i)
            pygame.draw.circle(screen, (170, 120, 55), (px, self.y + 46), 4)
            pygame.draw.rect(screen, (228, 185, 95), (px, self.y + 28, 18, 5))


class FloatingText:
    """Fading floating text overlays displaying alerts and stats directly on coordinates."""
    def __init__(self, x, y, text, color=WHITE, size=20, life=50):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", size, bold=True)
        self.life = life
        self.max_life = life
        self.dy = -1.3

    def update(self):
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int((self.life / self.max_life) * 255)

        # Fading text via temporary transparency surface
        t_surf = self.font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(t_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, alpha))
        t_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Shadow
        s_surf = self.font.render(self.text, True, BLACK)
        s_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        tx, ty = int(self.x - t_surf.get_width() // 2), int(self.y)
        screen.blit(s_surf, (tx + 1, ty + 1))
        screen.blit(t_surf, (tx, ty))


class Game:
    """The central game engine handling states, updates, rendering layers, and player inputs."""
    def __init__(self):
        self.high_score = 0
        self.bg_manager = BackgroundManager()
        self.clouds = [Cloud() for _ in range(4)]
        self.particles = []
        self.collectibles = []
        self.floating_texts = []
        
        self.temp_surf = pygame.Surface((WIDTH, HEIGHT))
        self.shake_intensity = 0.0
        self.running = True
        self.reset()

    def reset(self):
        self.bird = Bird()
        # Initialize first pipe gate
        self.pipes = [Pipe(WIDTH + 100)]
        self.ground = Ground()
        self.score = 0
        self.started = False
        self.game_over = False

        # Combo system details
        self.combo_timer = 0
        self.combo_multiplier = 1

        self.particles.clear()
        self.collectibles.clear()
        self.floating_texts.clear()

    def trigger_shake(self, intensity):
        self.shake_intensity = max(self.shake_intensity, intensity)

    def trigger_death(self):
        self.game_over = True
        self.trigger_shake(15.0)
        
        # Feather blast particle burst
        for _ in range(16):
            self.particles.append(
                Particle(
                    self.bird.x + self.bird.width / 2,
                    self.bird.y + self.bird.height / 2,
                    random.uniform(-5.0, 5.0),
                    random.uniform(-8.0, 2.0),
                    WHITE,
                    random.randint(4, 7),
                    random.randint(35, 60),
                    "feather",
                    0.96,
                    0.06
                )
            )
        # Spark explosion burst
        for _ in range(12):
            self.particles.append(
                Particle(
                    self.bird.x + self.bird.width / 2,
                    self.bird.y + self.bird.height / 2,
                    random.uniform(-4.0, 4.0),
                    random.uniform(-4.0, 4.0),
                    YELLOW,
                    random.randint(3, 5),
                    random.randint(20, 40),
                    "sparkle",
                    0.95,
                    0.08
                )
            )

    def trigger_shield_pop(self):
        self.trigger_shake(9.0)
        self.floating_texts.append(FloatingText(self.bird.x + 20, self.bird.y - 15, "SHIELD BROKEN!", (100, 200, 255), 20))
        # Blue circle expanding burst
        for i in range(20):
            angle = (i / 20.0) * math.pi * 2
            speed = random.uniform(4.0, 6.5)
            self.particles.append(
                Particle(
                    self.bird.x + self.bird.width / 2,
                    self.bird.y + self.bird.height / 2,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    (130, 210, 255),
                    5,
                    25,
                    "circle",
                    0.94,
                    0.0
                )
            )

    def handle_events(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        # Keyboard Continuous Flight hold states
        holding_up = keys[pygame.K_UP] or keys[pygame.K_SPACE] or mouse_buttons[0]
        holding_down = keys[pygame.K_DOWN] or mouse_buttons[2]

        if self.started and not self.game_over:
            self.bird.update_state(holding_up, holding_down)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_SPACE):
                    if not self.started:
                        self.started = True
                    if not self.game_over:
                        self.bird.jump()
                        # Little jump puff details
                        for _ in range(4):
                            self.particles.append(
                                Particle(
                                    self.bird.x + 2,
                                    self.bird.y + self.bird.height / 2,
                                    random.uniform(-3.5, -1.0),
                                    random.uniform(-1.5, 1.5),
                                    WHITE,
                                    random.randint(3, 5),
                                    random.randint(18, 30),
                                    "feather"
                                )
                            )

                if event.key == pygame.K_SPACE and self.game_over:
                    self.reset()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click (Jump)
                    if not self.started:
                        self.started = True
                    if not self.game_over:
                        self.bird.jump()
                        for _ in range(4):
                            self.particles.append(
                                Particle(
                                    self.bird.x + 2,
                                    self.bird.y + self.bird.height / 2,
                                    random.uniform(-3.5, -1.0),
                                    random.uniform(-1.5, 1.5),
                                    WHITE,
                                    random.randint(3, 5),
                                    random.randint(18, 30),
                                    "feather"
                                )
                            )

    def update(self):
        # Always update background transitions and drifting clouds
        self.bg_manager.update(self.score, 3 if (self.started and not self.game_over) else 0.5)
        for cloud in self.clouds:
            cloud.update()

        # Update visual items in background
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        for ft in self.floating_texts:
            ft.update()
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

        if not self.started or self.game_over:
            return

        self.bird.update()
        self.ground.update()

        # Tick combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_multiplier = 1

        # Spawn particle trails based on bird flying states
        if self.bird.state == "GLIDING":
            # Soft trailing wind puffs
            self.particles.append(
                Particle(
                    self.bird.x,
                    self.bird.y + self.bird.height / 2 + random.uniform(-4, 4),
                    random.uniform(-4.5, -3.0),
                    random.uniform(-0.5, 0.5),
                    (210, 240, 255),
                    4,
                    15,
                    "speed_line",
                    0.97,
                    0.0
                )
            )
        elif self.bird.state == "DIVING":
            # Speed streaks & orange fire sparks
            self.particles.append(
                Particle(
                    self.bird.x + self.bird.width / 2 + random.uniform(-6, 6),
                    self.bird.y,
                    random.uniform(-1.0, 1.0),
                    random.uniform(-6.0, -3.8),
                    (255, 150, 40),
                    5,
                    16,
                    "speed_line",
                    0.96,
                    0.05
                )
            )

        # Update collectibles
        for c in self.collectibles:
            c.update()
            
            # Collision checks
            if c.collide(self.bird):
                c.collected = True
                self.trigger_shake(2.5)

                if c.item_type == "coin":
                    # Grant score points scaled by combo
                    points = 1 * self.combo_multiplier
                    self.score += points
                    self.high_score = max(self.high_score, self.score)
                    
                    # Boost stamina
                    self.bird.stamina = min(self.bird.max_stamina, self.bird.stamina + 22.0)
                    
                    # Scale combo
                    self.combo_timer = 150  # 2.5 seconds window
                    self.combo_multiplier = min(4, self.combo_multiplier + 1)

                    text_color = (255, 235, 80) if self.combo_multiplier == 1 else (255, 120, 50)
                    popup_str = f"+{points}" if self.combo_multiplier == 1 else f"+{points} (x{self.combo_multiplier} Combo!)"
                    self.floating_texts.append(FloatingText(c.x, c.y - 10, popup_str, text_color, 21))

                    # Sparkles burst
                    for _ in range(8):
                        self.particles.append(
                            Particle(
                                c.x,
                                c.y,
                                random.uniform(-3, 3),
                                random.uniform(-3, 3),
                                (255, 220, 60),
                                5,
                                25,
                                "sparkle",
                                0.95,
                                0.05
                            )
                        )
                elif c.item_type == "shield":
                    self.bird.shield = min(1, self.bird.shield + 1)
                    self.floating_texts.append(FloatingText(c.x, c.y - 10, "SHIELD CHARGED!", (80, 180, 255), 20))
                    
                    for _ in range(8):
                        self.particles.append(
                            Particle(
                                c.x,
                                c.y,
                                random.uniform(-3, 3),
                                random.uniform(-3, 3),
                                (100, 190, 255),
                                5,
                                25,
                                "sparkle",
                                0.95,
                                0.0
                            )
                        )

        self.collectibles = [c for c in self.collectibles if not c.collected and c.x > -30]

        # Update pipes
        for pipe in self.pipes:
            pipe.update()

            if pipe.collide(self.bird):
                if self.bird.shield > 0:
                    self.bird.shield = 0
                    self.bird.invincible_time = 90  # 1.5 seconds invincibility
                    self.trigger_shield_pop()
                else:
                    self.trigger_death()

            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                self.high_score = max(self.high_score, self.score)
                self.floating_texts.append(FloatingText(self.bird.x + 10, self.bird.y - 20, "+1", WHITE, 24))

                # Display dynamic cycle announcements
                if self.score > 0 and self.score % 10 == 0:
                    cycle_names = ["DAYBREAK", "SUNSET DUSK", "MIDNIGHT", "GOLDEN DAWN"]
                    cycle_colors = [(255, 240, 100), (255, 120, 60), (140, 180, 255), (255, 190, 130)]
                    idx = (self.score // 10) % 4
                    self.floating_texts.append(
                        FloatingText(WIDTH // 2, HEIGHT // 3, f"--- {cycle_names[idx]} ---", cycle_colors[idx], 25, 80)
                    )

        # Spawning logic
        if self.pipes[-1].x < WIDTH - 220:
            # Gradually introduce moving pipes as difficulty scales (score >= 10)
            is_moving = False
            if self.score >= 10:
                is_moving = random.random() < min(0.65, (self.score - 8) * 0.05)

            new_pipe = Pipe(WIDTH, is_moving)
            self.pipes.append(new_pipe)

            # Spawn floating collectibles
            if random.random() < 0.8:
                gap_y = new_pipe.top_height + new_pipe.gap // 2
                item_type = "shield" if (random.random() < 0.08 and self.bird.shield == 0) else "coin"
                self.collectibles.append(Collectible(new_pipe.x + new_pipe.width // 2, gap_y, item_type))

        self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]

        # Roof & Floor boundaries check
        if self.bird.y <= 0:
            if self.bird.shield > 0:
                self.bird.shield = 0
                self.bird.invincible_time = 90
                self.bird.velocity = 2.0
                self.trigger_shield_pop()
            else:
                self.trigger_death()
        elif self.bird.y + self.bird.height >= HEIGHT - 85:
            self.trigger_death()
            self.bird.y = HEIGHT - 85 - self.bird.height
            self.bird.velocity = 0.0

    def draw_hud(self, screen):
        # Centered active score display
        shadow = FONT.render(str(self.score), True, BLACK)
        rendered = FONT.render(str(self.score), True, WHITE)
        screen.blit(shadow, (WIDTH // 2 - rendered.get_width() // 2 + 2, 42))
        screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, 40))

        # Main glowing Stamina HUD panel (top-left)
        stam_x, stam_y = 15, 18
        stam_w, stam_h = 135, 14
        
        # Stamina Label
        label = TINY_FONT.render("STAMINA", True, (240, 240, 240))
        label_shadow = TINY_FONT.render("STAMINA", True, BLACK)
        screen.blit(label_shadow, (stam_x + 1, stam_y - 15))
        screen.blit(label, (stam_x, stam_y - 16))

        # Stamina bar background outline
        pygame.draw.rect(screen, (30, 30, 30, 160), (stam_x, stam_y, stam_w, stam_h), 0, 4)
        pygame.draw.rect(screen, BLACK, (stam_x, stam_y, stam_w, stam_h), 2, 4)

        if self.bird.stamina > 0:
            # Color shifts dynamically to alert on low levels
            if self.bird.exhausted:
                bar_color = (255, 40, 40)
            elif self.bird.stamina < 30.0:
                bar_color = (255, 160, 30)
            else:
                bar_color = (60, 220, 105)
            
            fill_w = int(stam_w * (self.bird.stamina / self.bird.max_stamina))
            pygame.draw.rect(screen, bar_color, (stam_x + 2, stam_y + 2, fill_w - 4, stam_h - 4), 0, 2)
            
            # Subtle shining glass highlights
            pygame.draw.rect(screen, (255, 255, 255, 70), (stam_x + 2, stam_y + 2, fill_w - 4, (stam_h - 4) // 2), 0, 2)

        # Active Exhaustion warning overlay directly above stamina bar
        if self.bird.exhausted:
            warn = TINY_FONT.render("EXHAUSTED!", True, (255, 80, 80))
            screen.blit(warn, (stam_x + stam_w + 8, stam_y - 2))

        # Combo progress meter (bottom-left)
        if self.combo_multiplier > 1 and self.combo_timer > 0:
            ratio = self.combo_timer / 150.0
            comb_x, comb_y = 15, 60
            comb_w, comb_h = 95, 8

            c_text = TINY_FONT.render(f"COMBO x{self.combo_multiplier}", True, (255, 140, 40))
            screen.blit(c_text, (comb_x, comb_y - 16))

            pygame.draw.rect(screen, (30, 30, 30, 160), (comb_x, comb_y, comb_w, comb_h), 0, 2)
            pygame.draw.rect(screen, BLACK, (comb_x, comb_y, comb_w, comb_h), 1, 2)
            pygame.draw.rect(screen, (255, 165, 0), (comb_x + 1, comb_y + 1, int((comb_w - 2) * ratio), comb_h - 2), 0, 1)

    def draw(self):
        # Draw all visual frames on intermediate canvas buffer to allow robust screenshaking
        self.temp_surf.fill(BLACK)
        self.bg_manager.draw(self.temp_surf)

        # Clouds
        for cloud in self.clouds:
            cloud.draw(self.temp_surf)

        # Pipes
        for pipe in self.pipes:
            pipe.draw(self.temp_surf)

        # Collectibles
        for c in self.collectibles:
            c.draw(self.temp_surf)

        # Ground
        self.ground.draw(self.temp_surf)

        # Sparkles & Trailing Particle lists
        for p in self.particles:
            p.draw(self.temp_surf)

        # The Bird
        self.bird.draw(self.temp_surf)

        # Stamina indicators right next to player (mini HUD widget)
        if self.bird.stamina < 100.0 and not self.game_over:
            m_w = self.bird.width + 10
            m_x = self.bird.x - 5
            m_y = self.bird.y - 12
            pygame.draw.rect(self.temp_surf, (30, 30, 30, 180), (m_x, m_y, m_w, 4), 0, 2)
            m_color = (255, 45, 45) if self.bird.exhausted else (65, 215, 95)
            m_fill = int(m_w * (self.bird.stamina / self.bird.max_stamina))
            pygame.draw.rect(self.temp_surf, m_color, (m_x, m_y, m_fill, 4), 0, 2)

        # Floating Popups
        for ft in self.floating_texts:
            ft.draw(self.temp_surf)

        # Main HUD
        self.draw_hud(self.temp_surf)

        # Text menus for non-play states
        if not self.started:
            self.draw_text_center("FLAPPY EVOLUTION", FONT, 220, (255, 215, 40))
            self.draw_text_center("TAPPING UP / CLICK = Jump & Start", SMALL_FONT, 285)
            self.draw_text_center("HOLD UP = Gliding | HOLD DOWN = Diving", SMALL_FONT, 318)
            self.draw_text_center("Tip: Squeeze under moving pipes by diving!", TINY_FONT, 360, (180, 240, 255))

        if self.game_over:
            self.draw_text_center("GAME OVER", FONT, 230, (255, 60, 60))
            self.draw_text_center(f"High Score: {self.high_score}", SMALL_FONT, 295)
            self.draw_text_center("Press SPACE to Fly Again", SMALL_FONT, 328)

        # Calculate Screenshake coordinate offsets
        shake_x, shake_y = 0, 0
        if self.shake_intensity > 0.1:
            shake_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            shake_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            self.shake_intensity *= 0.88

        # Render complete buffer surface onto screen
        SCREEN.blit(self.temp_surf, (shake_x, shake_y))
        pygame.display.update()

    def draw_text_center(self, text, font, y, color=WHITE):
        shadow = font.render(text, True, BLACK)
        rendered = font.render(text, True, color)
        self.temp_surf.blit(shadow, (WIDTH // 2 - rendered.get_width() // 2 + 2, y + 2))
        self.temp_surf.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, y))

    def run(self):
        while self.running:
            CLOCK.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    game = Game()
    game.run()