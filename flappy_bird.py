import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 600
GRAVITY = 0.25
BIRD_JUMP = -7
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQ = 1500  # milliseconds
CLOUD_FREQ = 2000  # milliseconds
FPS = 60
GROUND_HEIGHT = 80
TEXT_PADDING = 10  # Padding for text backgrounds

# Colors
WHITE = (255, 255, 255)
SKY = (135, 206, 235)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
GROUND_COLOR = (34, 139, 34)

# Bird class
class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.flap_timer = 0

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        if self.flap_timer > 0:
            self.flap_timer -= 1

    def jump(self):
        self.velocity = BIRD_JUMP
        self.flap_timer = 10  # Flap animation for 10 frames

    def draw(self, screen):
        flapping = self.flap_timer > 0

        # Body
        pygame.draw.ellipse(screen, YELLOW, (int(self.x - 17), int(self.y - 8), 34, 16))

        # Head
        pygame.draw.circle(screen, YELLOW, (int(self.x + 10), int(self.y - 5)), 8)

        # Beak
        beak_points = [(self.x + 15, self.y - 5), (self.x + 23, self.y - 5), (self.x + 15, self.y)]
        pygame.draw.polygon(screen, ORANGE, beak_points)

        # Eye
        pygame.draw.circle(screen, BLACK, (int(self.x + 12), int(self.y - 6)), 2)

        # Wings
        if flapping:
            # Wings down
            wing_left_start = (self.x - 5, self.y - 5)
            wing_left_end = (self.x - 25, self.y + 10)
            wing_right_start = (self.x + 5, self.y - 5)
            wing_right_end = (self.x + 25, self.y + 10)
        else:
            # Wings up
            wing_left_start = (self.x - 5, self.y - 5)
            wing_left_end = (self.x - 25, self.y - 20)
            wing_right_start = (self.x + 5, self.y - 5)
            wing_right_end = (self.x + 25, self.y - 20)

        pygame.draw.line(screen, YELLOW, wing_left_start, wing_left_end, 8)
        pygame.draw.line(screen, YELLOW, wing_right_start, wing_right_end, 8)

# Pipe class
class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.top_height = random.randint(100, HEIGHT - GROUND_HEIGHT - PIPE_GAP - 100)
        self.bottom_y = self.top_height + PIPE_GAP
        self.bottom_height = HEIGHT - GROUND_HEIGHT - self.bottom_y
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, GREEN, (self.x, 0, 50, self.top_height))
        # Top pipe head
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.top_height - 20, 60, 20))

        # Bottom pipe
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, 50, self.bottom_height))
        # Bottom pipe head
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.bottom_y, 60, 20))

    def collides(self, bird):
        bird_rect = pygame.Rect(bird.x - 20, bird.y - 10, 40, 20)
        top_pipe = pygame.Rect(self.x, 0, 50, self.top_height)
        bottom_pipe = pygame.Rect(self.x, self.bottom_y, 50, self.bottom_height)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

# Cloud class
class Cloud:
    def __init__(self):
        self.x = WIDTH
        self.y = random.randint(50, 200)
        self.speed = 1

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Simple cloud: three overlapping circles
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 30)
        pygame.draw.circle(screen, WHITE, (int(self.x + 25), int(self.y + 5)), 20)
        pygame.draw.circle(screen, WHITE, (int(self.x - 25), int(self.y + 5)), 20)

# Game variables
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
bird = Bird()
pipes = []
clouds = []
score = 0
last_score = 0
font = pygame.font.Font(None, 36)
last_pipe = pygame.time.get_ticks()
last_cloud = pygame.time.get_ticks()
game_state = "ready"

def setup():
    global bird, pipes, score, last_score, last_pipe, game_state
    last_score = score
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    game_state = "ready"

def update_loop():
    global score, last_pipe, last_cloud, game_state

    current_time = pygame.time.get_ticks()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_state == "ready":
                game_state = "playing"
                bird.jump()
            elif game_state == "playing":
                bird.jump()

    # Update clouds always
    for cloud in clouds[:]:
        cloud.update()
        if cloud.x < -50:
            clouds.remove(cloud)

    # Spawn clouds always
    if current_time - last_cloud > CLOUD_FREQ:
        clouds.append(Cloud())
        last_cloud = current_time

    if game_state == "playing":
        # Update bird
        bird.update()

        # Spawn pipes
        if current_time - last_pipe > PIPE_FREQ:
            pipes.append(Pipe())
            last_pipe = current_time

        # Update pipes
        for pipe in pipes[:]:
            pipe.update()
            if pipe.x < -50:
                pipes.remove(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1

        # Check collisions
        game_over = bird.y + 10 > HEIGHT - GROUND_HEIGHT or bird.y - 10 < 0
        for pipe in pipes:
            if pipe.collides(bird):
                game_over = True

        if game_over:
            setup()

    # Draw
    screen.fill(SKY)
    for cloud in clouds:
        cloud.draw(screen)
    # Draw ground
    pygame.draw.rect(screen, GROUND_COLOR, (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
    for pipe in pipes:
        pipe.draw(screen)
    bird.draw(screen)

    # Score text with padding
    score_text = font.render(str(score), True, BLACK)
    score_bg = pygame.Surface((score_text.get_width() + 2 * TEXT_PADDING, score_text.get_height() + 2 * TEXT_PADDING))
    score_bg.fill(WHITE)
    screen.blit(score_bg, (WIDTH // 2 - score_text.get_width() // 2 - TEXT_PADDING, 50 - TEXT_PADDING))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 50))

    if game_state == "ready":
        # Start text with padding
        start_text = font.render("Press SPACE to start", True, BLACK)
        start_bg = pygame.Surface((start_text.get_width() + 2 * TEXT_PADDING, start_text.get_height() + 2 * TEXT_PADDING))
        start_bg.fill(WHITE)
        screen.blit(start_bg, (WIDTH // 2 - start_text.get_width() // 2 - TEXT_PADDING, HEIGHT // 2 - 50 - TEXT_PADDING))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 - 50))

        # Instruction text with padding
        instr_text = font.render("Press SPACE to flap and avoid pipes", True, BLACK)
        instr_bg = pygame.Surface((instr_text.get_width() + 2 * TEXT_PADDING, instr_text.get_height() + 2 * TEXT_PADDING))
        instr_bg.fill(WHITE)
        screen.blit(instr_bg, (WIDTH // 2 - instr_text.get_width() // 2 - TEXT_PADDING, HEIGHT // 2 - TEXT_PADDING))
        screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT // 2))

        # Game over text with padding
        if last_score > 0:
            over_text = font.render(f"Game Over! Score: {last_score}", True, BLACK)
            over_bg = pygame.Surface((over_text.get_width() + 2 * TEXT_PADDING, over_text.get_height() + 2 * TEXT_PADDING))
            over_bg.fill(WHITE)
            screen.blit(over_bg, (WIDTH // 2 - over_text.get_width() // 2 - TEXT_PADDING, HEIGHT // 2 - 100 - TEXT_PADDING))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 100))

    pygame.display.flip()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())