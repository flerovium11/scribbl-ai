from time import sleep
import pygame
from components.colors import colors
import random
import sys

# Initialize Pygame
pygame.init()

# Set the screen size
screen_width = 650
screen_height = 550
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('ScribblAI')
logo = pygame.image.load('./assets/logo.png')
pygame.display.set_icon(logo)

# Set fonts
handwriting_font = pygame.font.SysFont('Ink Free', 120)
subtitle_font = pygame.font.SysFont('Ink Free', 30)
credits_font = pygame.font.SysFont('Ink Free', 20)
text_font = pygame.font.SysFont('Arial', 30)

# Set text
title_text = 'ScribblAI'
subtitle_text = 'Bist du besser als die KI?'
gamemode_text1 = 'Mehrspieler'
gamemode_text2 = 'Sandkiste'
credits_text = 'Ennio Binder 2024'

# Create text surfaces
title_surface = handwriting_font.render(title_text, True, colors.purple)
title_bg_surface = handwriting_font.render(title_text, True, colors.pink)
subtitle_surface = subtitle_font.render(subtitle_text, True, colors.purple)
gamemode_text1_surface = text_font.render(gamemode_text1, True, colors.salmon)
gamemode_text2_surface = text_font.render(gamemode_text2, True, colors.purple)
credits_surface = credits_font.render(credits_text, True, colors.purple)

# Create gamemode buttons with rounded edges
button_radius = 10
buttons_distance = 10
button_width = button1_width = button2_width = 240
button_height = button1_height = button2_height = 140
question_button_radius = qbr = 40

running = True
rotate_title = 0.1
rotate_bg = -0.1
rotate = pygame.USEREVENT + 1

pygame.time.set_timer(rotate, 500)

while running:
    gamemode_button1 = pygame.Rect(screen_width/2 - button_width - buttons_distance/2 + button_width/2 - button1_width/2, 200 + button_height/2 - button1_height/2, button1_width, button1_height).inflate(-2 * button_radius, -2 * button_radius)
    gamemode_button2 = pygame.Rect(screen_width/2 + buttons_distance/2 + button_width/2 - button2_width/2, 200 + button_height/2 - button2_height/2, button2_width, button2_height).inflate(-2 * button_radius, -2 * button_radius)
    question_button = pygame.Rect(screen_width // 2 - qbr, screen_height - 140 - qbr, 2 * qbr, 2 * qbr)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == rotate:
            rotate_title *= -1
            rotate_bg *= -1

        buttons = [gamemode_button1, gamemode_button2, question_button]
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Handle mouse clicks
        if gamemode_button1.collidepoint(mouse_pos):
            button1_width = button_width * 1.05
            button1_height = button_height * 1.05
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Button 1 clicked')
        else:
            button1_width = button_width
            button1_height = button_height

        if gamemode_button2.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            button2_width = button_width * 1.05
            button2_height = button_height * 1.05
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Button 2 clicked')
        else:
            button2_width = button_width
            button2_height = button_height

        if question_button.collidepoint(mouse_pos):
            qbr = question_button_radius * 1.1
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                print('Question mark button clicked')
        else:
            qbr = question_button_radius
    
    # Fill the screen with pink
    screen.fill(colors.beige)

    # Draw the title with centered placement
    title_x = screen_width // 2 - title_surface.get_width() // 2
    screen.blit(pygame.transform.rotate(title_bg_surface, rotate_bg), (title_x, 40))
    screen.blit(pygame.transform.rotate(title_surface, rotate_title), (title_x, 30))

    # Draw the subtitle with centered placement
    subtitle_x = screen_width // 2 - subtitle_surface.get_width() // 2
    screen.blit(subtitle_surface, (subtitle_x, 145))

    # Draw the gamemode buttons with rounded edges
    pygame.draw.rect(screen, colors.purple, gamemode_button1, border_radius=button_radius)
    pygame.draw.rect(screen, colors.salmon, gamemode_button2, border_radius=button_radius)

    # Draw the gamemode text within their respective buttons
    screen.blit(gamemode_text1_surface, (gamemode_button1.x + gamemode_button1.width // 2 - gamemode_text1_surface.get_width() // 2, gamemode_button1.y + gamemode_button1.height // 2 - gamemode_text1_surface.get_height() // 2))
    screen.blit(gamemode_text2_surface, (gamemode_button2.x + gamemode_button2.width // 2 - gamemode_text2_surface.get_width() // 2, gamemode_button2.y + gamemode_button2.height // 2 - gamemode_text2_surface.get_height() // 2))

    # Draw the question mark button with rounded edges
    pygame.draw.circle(screen, colors.pink, (question_button.center), qbr)
    question_mark_font = pygame.font.SysFont(None, 60)
    question_mark_text = '?'
    question_mark_surface = question_mark_font.render(question_mark_text, True, colors.beige)
    screen.blit(question_mark_surface, (question_button.center[0] - question_mark_surface.get_width() // 2, question_button.center[1] - question_mark_surface.get_height() // 2))

    # Draw the credits with centered placement
    credits_x = screen_width // 2 - credits_surface.get_width() // 2
    screen.blit(credits_surface, (credits_x, screen_height - credits_surface.get_height() - 10))

    # Update the display
    pygame.display.flip()
    pygame.display.update()

# Quit Pygame
pygame.quit()
