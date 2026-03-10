import pygame
import sys
import random
import pygame.gfxdraw

pygame.init()

# ============================
# SETTINGS
# ============================

loop1 = True
loop2 = False

doBallLimit = True
COLLISION_COOLDOWN = 0
collision_timer = 0
lose_energy = -1
GRAVITY = 500
FPS = 60
NUM_BALLS = 2
AIR_DRAG = 0.999
AIR_DRAG_ENABLED = False
doSpeedScaling = False
BALL_MULTIP = True
fullscreen = False
WINDOWED_SIZE = [1000, 700]
BALL_LIMIT = 20
max_v = 1200
finalradius = 20
posneg = [1, -1]

rvx1_i = 200
rvx2_i = 300
rvy1_i = 50
rvy2_i = 100

rvx1, rvx2, rvy1, rvy2 = rvx1_i, rvx2_i, rvy1_i, rvy2_i
# ============================
# BALL FUNCTIONS
# ============================

def create_ball(x, y, vx, vy, radius):
    colour = (random.randint(0,255),
              random.randint(0,255),
              random.randint(0,255))
    return {"x": x, "y": y, "vx": vx, "vy": vy,
            "radius": radius, "colour": colour, "remove": False}

def update_ball(ball, width, height, dt):
    ball["vy"] += GRAVITY * dt
    ball["x"] += ball["vx"] * dt
    ball["y"] += ball["vy"] * dt

    if AIR_DRAG_ENABLED:
        ball["vx"] *= AIR_DRAG

    #Wall collisions
    if ball["x"] - ball["radius"] <= 0 and ball["vx"] < 0:
        ball["x"] = ball["radius"]
        ball["vx"] *= -1

    if ball["x"] + ball["radius"] >= width and ball["vx"] > 0:
        ball["x"] = width - ball["radius"]
        ball["vx"] *= -1

    if ball["y"] + ball["radius"] >= height and ball["vy"] > 0:
        ball["y"] = height - ball["radius"]
        ball["vy"] *= lose_energy

    if ball["y"] - ball["radius"] <= 0 and ball["vy"] < 0:
        ball["y"] = ball["radius"]
        ball["vy"] *= lose_energy

def draw_ball(ball, screen):
    pygame.gfxdraw.filled_circle(
        screen,
        int(ball["x"]),
        int(ball["y"]),
        ball["radius"],
        ball["colour"]
    )
    pygame.gfxdraw.aacircle(
        screen,
        int(ball["x"]),
        int(ball["y"]),
        ball["radius"],
        ball["colour"]
    )

def summon_ball():
    global rvx1, rvx2, rvy1, rvy2
    balls.append(create_ball(
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(rvx1, rvx2) * random.choice(posneg),
        random.randint(rvy1, rvy2) * random.choice(posneg),
        finalradius
    ))

    if rvx1 <= max_v and doSpeedScaling:
        rvx1 = int(rvx1 * 1.5)
        rvx2 = int(rvx2 * 1.5)
        rvy1 = int(rvy1 * 1.5)
        rvy2 = int(rvy2 * 1.5)

def reset_simulation():
    global balls, rvx1, rvx2, rvy1, rvy2
    balls = []
    rvx1, rvx2, rvy1, rvy2 = rvx1_i, rvx2_i, rvy1_i, rvy2_i
    for _ in range(NUM_BALLS):
        summon_ball()

def handle_collision(ball1, ball2):
    global collision_timer

    dx = ball2["x"] - ball1["x"]
    dy = ball2["y"] - ball1["y"]
    distance = (dx**2 + dy**2) ** 0.5
    if distance == 0:
        distance = 0.1

    if distance < ball1["radius"] + ball2["radius"]:

        if (len(balls) < BALL_LIMIT2
            and collision_timer <= 0
            and BALL_MULTIP):

            summon_ball()
            collision_timer = COLLISION_COOLDOWN
        elif doBallLimit == False:
            summon_ball()

        nx, ny = dx / distance, dy / distance
        tx, ty = -ny, nx

        v1n = ball1["vx"]*nx + ball1["vy"]*ny
        v1t = ball1["vx"]*tx + ball1["vy"]*ty
        v2n = ball2["vx"]*nx + ball2["vy"]*ny
        v2t = ball2["vx"]*tx + ball2["vy"]*ty

        v1n, v2n = v2n, v1n

        ball1["vx"] = v1n*nx + v1t*tx
        ball1["vy"] = v1n*ny + v1t*ty
        ball2["vx"] = v2n*nx + v2t*tx
        ball2["vy"] = v2n*ny + v2t*ty

        overlap = 0.5 * (
            ball1["radius"] + ball2["radius"] - distance
        )

        ball1["x"] -= nx * overlap
        ball1["y"] -= ny * overlap
        ball2["x"] += nx * overlap
        ball2["y"] += ny * overlap

# ============================
# MAIN LOOP
# ============================
screen = pygame.display.set_mode(WINDOWED_SIZE)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Bouncing Balls")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

balls = []
reset_simulation()

BALL_LIMIT2 = BALL_LIMIT

while loop1:
    dt = clock.tick(FPS) / 1000

    if collision_timer > 0:
        collision_timer -= dt

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            loop1 = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                reset_simulation()

            if event.key == pygame.K_KP_PLUS:
                BALL_LIMIT2 += 10

            if event.key == pygame.K_KP_MINUS:
                BALL_LIMIT2 -= 10

            if event.key == pygame.K_e:
                summon_ball()

            if event.key == pygame.K_ESCAPE:
                loop1 = False
                
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                info = pygame.display.Info()  # always refresh display info

                if fullscreen:
                    # Borderless fullscreen (fake fullscreen)
                    screen = pygame.display.set_mode(
                        (info.current_w, info.current_h),
                        pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF
                    )
                else:
                    # Normal windowed mode
                    screen = pygame.display.set_mode(
                        (WINDOWED_SIZE[0], WINDOWED_SIZE[1]),
                        pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
                    )

                # Update width and height for all simulation logic
    WIDTH, HEIGHT = screen.get_size()

    if doBallLimit:
        while len(balls) > BALL_LIMIT2:
            balls.pop()

    screen.fill((30, 30, 30))

    for ball in balls:
        update_ball(ball, WIDTH, HEIGHT, dt)

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            handle_collision(balls[i], balls[j])

    for ball in balls:
        
        if ball["x"] <= 0:
            ball["remove"] = True
            summon_ball()
            summon_ball()
            
        balls[:] = [b for b in balls if not b.get("remove", False)]

        draw_ball(ball, screen)

    text = font.render(
        f"Balls: {len(balls)}",
        True,
        (255, 255, 255)
    )
    screen.blit(text, (20, 20))

    if doBallLimit:
        text = font.render(
            f"Ball_Limit: {BALL_LIMIT2}",
            True,
            (255, 255, 255)
        )
        screen.blit(text, (20, 50))
    else:
        text = font.render(
            f"Ball_Limit: NO LIMIT!",
            True,
            (255, 255, 255)
        )
        screen.blit(text, (20, 50))
    
    pygame.display.flip()

# ============================
# MAIN LOOP2
# ============================
while loop2:
    print(WIDTH)
    
pygame.quit()
sys.exit()
