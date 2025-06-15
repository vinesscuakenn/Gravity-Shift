import asyncio
import platform
import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
width = 600
height = 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gravity Shift")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)

# Player properties
ball_radius = 10
ball_x = 50
ball_y = height // 2
ball_speed = 3
gravity = 0.2
velocity_y = 0
gravity_direction = "down"  # Possible: "up", "down", "left", "right"

# Game elements
gems = []
spikes = []
gem_size = 8
spike_size = 10
spawn_rate = 0.02  # Probability of spawning per frame

# Game variables
score = 0
health = 3
game_time = 30  # Game duration in seconds
start_time = pygame.time.get_ticks() // 1000
running = True

# Function to create a new gem
def create_gem():
    x = random.randint(50, width - 50)
    y = random.randint(50, height - 50)
    return {'x': x, 'y': y}

# Function to create a new spike
def create_spike():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x = random.randint(0, width)
        y = 0
    elif side == "bottom":
        x = random.randint(0, width)
        y = height - spike_size
    elif side == "left":
        x = 0
        y = random.randint(0, height)
    else:  # right
        x = width - spike_size
        y = random.randint(0, height)
    return {'x': x, 'y': y, 'side': side}

# Setup function for initialization
def setup():
    global ball_x, ball_y, velocity_y, gravity_direction, gems, spikes, score, health, start_time, running
    ball_x = 50
    ball_y = height // 2
    velocity_y = 0
    gravity_direction = "down"
    gems = [create_gem() for _ in range(3)]
    spikes = [create_spike() for _ in range(5)]
    score = 0
    health = 3
    start_time = pygame.time.get_ticks() // 1000
    running = True
    window.fill(black)
    pygame.display.update()

# Update loop for game logic
async def update_loop():
    global ball_x, ball_y, velocity_y, gravity_direction, gems, spikes, score, health, running

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Switch gravity direction
                gravity_directions = ["down", "up", "left", "right"]
                current_idx = gravity_directions.index(gravity_direction)
                gravity_direction = gravity_directions[(current_idx + 1) % 4]
                velocity_y = 0  # Reset velocity on gravity switch

    # Handle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and ball_x > ball_radius:
        ball_x -= ball_speed
    if keys[pygame.K_RIGHT] and ball_x < width - ball_radius:
        ball_x += ball_speed
    if keys[pygame.K_UP] and ball_y > ball_radius:
        ball_y -= ball_speed
    if keys[pygame.K_DOWN] and ball_y < height - ball_radius:
        ball_y += ball_speed

    # Apply gravity
    if gravity_direction == "down":
        velocity_y += gravity
        ball_y += velocity_y
        if ball_y > height - ball_radius:
            ball_y = height - ball_radius
            velocity_y = 0
    elif gravity_direction == "up":
        velocity_y -= gravity
        ball_y += velocity_y
        if ball_y < ball_radius:
            ball_y = ball_radius
            velocity_y = 0
    elif gravity_direction == "left":
        velocity_y -= gravity
        ball_x += velocity_y
        if ball_x < ball_radius:
            ball_x = ball_radius
            velocity_y = 0
    elif gravity_direction == "right":
        velocity_y += gravity
        ball_x += velocity_y
        if ball_x > width - ball_radius:
            ball_x = width - ball_radius
            velocity_y = 0

    # Spawn new gems and spikes
    if random.random() < spawn_rate:
        gems.append(create_gem())
    if random.random() < spawn_rate / 2:
        spikes.append(create_spike())

    # Check collisions
    ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
    for gem in gems[:]:
        gem_rect = pygame.Rect(gem['x'] - gem_size // 2, gem['y'] - gem_size // 2, gem_size, gem_size)
        if ball_rect.colliderect(gem_rect):
            score += 1
            gems.remove(gem)
    for spike in spikes[:]:
        spike_rect = pygame.Rect(spike['x'], spike['y'], spike_size, spike_size)
        if ball_rect.colliderect(spike_rect):
            health -= 1
            spikes.remove(spike)
            if health <= 0:
                return False

    # Check time limit
    current_time = pygame.time.get_ticks() // 1000
    if current_time - start_time >= game_time:
        return False

    # Draw the screen
    window.fill(black)
    pygame.draw.circle(window, white, (int(ball_x), int(ball_y)), ball_radius)  # Draw ball
    for gem in gems:
        pygame.draw.rect(window, yellow, (gem['x'] - gem_size // 2, gem['y'] - gem_size // 2, gem_size, gem_size))  # Draw gems
    for spike in spikes:
        pygame.draw.rect(window, red, (spike['x'], spike['y'], spike_size, spike_size))  # Draw spikes
    pygame.display.set_caption(f"Gravity Shift - Score: {score} | Health: {health} | Time: {game_time - (current_time - start_time)}")
    pygame.display.update()

    return True

# Main game loop
FPS = 60

async def main():
    setup()
    global running
    while running:
        running = await update_loop()
        await asyncio.sleep(1.0 / FPS)

    # Game over message
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over - Score: {score}", True, white)
    window.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
    pygame.display.update()
    await asyncio.sleep(2)  # Wait 2 seconds
    pygame.quit()

# Run the game based on platform
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
