import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
canvas = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drawing Canvas")

# Variables
drawing = False
pen_size = 5
eraser_size = 20
pen_mode = True
points = []

# Function to draw on the canvas
def draw(canvas, color, points, size):
    if len(points) < 2:
        return
    pygame.draw.lines(canvas, color, False, points, size)

# Main loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                drawing = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
        elif event.type == pygame.MOUSEMOTION:
            if drawing and pen_mode:
                points.append(event.pos)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                pen_mode = False
            elif event.key == pygame.K_p:
                pen_mode = True
    
    # Fill canvas once at the beginning of each iteration
    canvas.fill(WHITE)
    
    # Draw buttons
    delete_button = pygame.draw.rect(canvas, BLACK, (50, HEIGHT-50, 100, 40))
    erase_button = pygame.draw.rect(canvas, BLACK, (200, HEIGHT-50, 100, 40))
    pen_size_button = pygame.draw.rect(canvas, BLACK, (350, HEIGHT-50, 100, 40))
    pencil_button = pygame.draw.rect(canvas, BLACK, (500, HEIGHT-50, 100, 40))
    
    # Text on buttons
    font = pygame.font.SysFont(None, 30)
    delete_text = font.render("Delete", True, WHITE)
    erase_text = font.render("Erase", True, WHITE)
    pen_size_text = font.render("Pen Size", True, WHITE)
    pencil_text = font.render("Pencil", True, WHITE)
    
    canvas.blit(delete_text, (70, HEIGHT-40))
    canvas.blit(erase_text, (220, HEIGHT-40))
    canvas.blit(pen_size_text, (360, HEIGHT-40))
    canvas.blit(pencil_text, (520, HEIGHT-40))
    
    # Draw pencil trace
    draw(canvas, BLACK, points, pen_size)
    
    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
