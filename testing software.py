# import pygame
# import sys
# import random
# import math

# def main():
#     pygame.init()

#     # -- FULLSCREEN SETUP --
#     # This creates a full-screen window using the current screen resolution.
#     screen_info = pygame.display.Info()
#     width, height = screen_info.current_w, screen_info.current_h
#     screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#     pygame.display.set_caption("Joystick Circle vs. Random Target")

#     # -- JOYSTICK SETUP --
#     joystick_count = pygame.joystick.get_count()
#     if joystick_count == 0:
#         print("No joystick detected. Connect a joystick and try again.")
#         pygame.quit()
#         sys.exit()
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#     print(f"Initialized joystick: {joystick.get_name()}")

#     # -- VARIABLES FOR ADJUSTING SENSITIVITY & SPEED --
#     # Adjust these to change how "fast" or "responsive" the circle moves
#     sensitivity = 1.5   # Increase to make small axis movements more significant
#     base_speed = 5.0    # Base speed (pixels per update)

#     # -- GREEN CIRCLE (PLAYER) PROPERTIES --
#     circle_color = (0, 255, 0)   # Green
#     circle_radius = 20
#     circle_x = width // 2
#     circle_y = height // 2

#     # -- RED TARGET PROPERTIES --
#     target_color = (255, 0, 0)
#     target_radius = 15

#     # Function to pick a random position within screen boundaries
#     def random_position(radius):
#         """Return a (x, y) within the screen so the entire circle is on screen."""
#         x = random.randint(radius, width - radius)
#         y = random.randint(radius, height - radius)
#         return x, y

#     target_x, target_y = random_position(target_radius)

#     # -- DISTANCE THRESHOLD --
#     # If the green circle center is within this distance from the red target, it "hits" the target.
#     threshold_distance = 30

#     clock = pygame.time.Clock()
#     running = True

#     while running:
#         # Limit the framerate to ~60 FPS
#         clock.tick(60)

#         # Process events
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.KEYDOWN:
#                 # ESC key to quit fullscreen quickly
#                 if event.key == pygame.K_ESCAPE:
#                     running = False

#         # Read joystick axis values
#         axis_x = joystick.get_axis(0)  # Typically the horizontal axis
#         axis_y = joystick.get_axis(1)  # Typically the vertical axis

#         # Convert axis values into circle position updates
#         # Typically joystick axes range from -1.0 to +1.0
#         delta_x = axis_x * base_speed * sensitivity
#         delta_y = axis_y * base_speed * sensitivity

#         # Update circle position
#         circle_x += int(delta_x)
#         circle_y += int(delta_y)

#         # (Optional) Keep the circle within screen bounds
#         if circle_x < circle_radius:
#             circle_x = circle_radius
#         if circle_x > width - circle_radius:
#             circle_x = width - circle_radius
#         if circle_y < circle_radius:
#             circle_y = circle_radius
#         if circle_y > height - circle_radius:
#             circle_y = height - circle_radius

#         # Check if the green circle is close enough to the target
#         # Use Euclidean distance between circle center and target center
#         dist = math.hypot(circle_x - target_x, circle_y - target_y)
#         if dist <= threshold_distance:
#             # The circle "reached" the target
#             # Move the target to a new random location
#             target_x, target_y = random_position(target_radius)

#         # Clear the screen (black background)
#         screen.fill((0, 0, 0))

#         # Draw the target
#         pygame.draw.circle(screen, target_color, (target_x, target_y), target_radius)

#         # Draw the green circle (the player)
#         pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

#         # Update the display
#         pygame.display.flip()

#     pygame.quit()

# if __name__ == "__main__":
#     main()
import pygame
import sys
import random
import math
import time

def main():
    pygame.init()

    # -- FULLSCREEN SETUP --
    display_info = pygame.display.Info()
    width, height = display_info.current_w, display_info.current_h
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Joystick Experiment with Data Logging")

    # -- FONTS --
    pygame.font.init()
    font = pygame.font.SysFont(None, 36)

    # -- JOYSTICK SETUP --
    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print("No joystick detected. Connect a joystick and try again.")
        pygame.quit()
        sys.exit()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Initialized joystick: {joystick.get_name()}")
    print(f"Number of axes: {joystick.get_numaxes()}")

    # -- VARIABLES FOR ADJUSTING SENSITIVITY & SPEED --
    sensitivity = 1.0    # Increase to make small axis movements more significant
    base_speed = 5.0     # Base speed (pixels per update)

    # -- GREEN CIRCLE (PLAYER) PROPERTIES --
    circle_color = (0, 255, 0)   # Green
    circle_radius = 20
    circle_x = width // 2
    circle_y = height // 2

    # -- RED TARGET PROPERTIES --
    target_color = (255, 0, 0)
    target_radius = 15

    # Distance threshold to consider the target "reached"
    threshold_distance = 30

    # Function to pick a random position within screen boundaries
    def random_position(radius):
        """Return (x, y) within the screen so the entire circle is on screen."""
        x = random.randint(radius, width - radius)
        y = random.randint(radius, height - radius)
        return x, y

    # Start screen: wait for ENTER
    def start_screen():
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        waiting = False

            # Draw start screen text
            screen.fill((0, 0, 0))
            title_text = font.render("Press ENTER to Start", True, (255, 255, 255))
            rect = title_text.get_rect(center=(width // 2, height // 2))
            screen.blit(title_text, rect)
            pygame.display.flip()

    start_screen()

    # After pressing Enter, spawn first target and begin
    target_x, target_y = random_position(target_radius)

    # Keep track of trials
    trial_number = 1

    # Timing and distance for the current target
    trial_start_time = time.time()
    travel_distance = 0.0

    # Keep track of the circle's position from the previous frame for distance
    old_x, old_y = circle_x, circle_y

    clock = pygame.time.Clock()
    running = True

    def draw_axes():
        """Draw simple axes lines through the center, labeled 'X=0, Y=0'."""
        center_x, center_y = width // 2, height // 2

        # Draw vertical axis line
        pygame.draw.line(screen, (100, 100, 100), (center_x, 0), (center_x, height), 2)
        # Draw horizontal axis line
        pygame.draw.line(screen, (100, 100, 100), (0, center_y), (width, center_y), 2)

        # Label near the center
        label_text = font.render("X=0, Y=0", True, (255, 255, 255))
        label_rect = label_text.get_rect(center=(center_x + 60, center_y - 20))
        screen.blit(label_text, label_rect)

    # OPTIONAL: Open file in 'write' mode initially to create or overwrite it, and write header
    with open("results.txt", "w") as f:
        f.write("Trial,Time,Distance\n")

    while running:
        clock.tick(60)

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Read joystick axis values
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)

        # Convert axis values into position updates
        delta_x = axis_x * base_speed * sensitivity
        delta_y = axis_y * base_speed * sensitivity

        # Update circle position
        circle_x += int(delta_x)
        circle_y += int(delta_y)

        # Keep the circle within screen bounds
        if circle_x < circle_radius:
            circle_x = circle_radius
        if circle_x > width - circle_radius:
            circle_x = width - circle_radius
        if circle_y < circle_radius:
            circle_y = circle_radius
        if circle_y > height - circle_radius:
            circle_y = height - circle_radius

        # Accumulate travel distance (Euclidean) from the previous position
        step_dist = math.hypot(circle_x - old_x, circle_y - old_y)
        travel_distance += step_dist
        old_x, old_y = circle_x, circle_y

        # Check if the green circle is close enough to the red target
        dist_to_target = math.hypot(circle_x - target_x, circle_y - target_y)
        if dist_to_target <= threshold_distance:
            # The circle "reached" the target
            response_time = time.time() - trial_start_time
            print(f"Target {trial_number} Reached! Time: {response_time:.2f}s, Distance: {travel_distance:.2f}px")

            # -- LOG DATA TO THE TEXT FILE --
            with open("results.txt", "a") as f:
                f.write(f"{trial_number},{response_time:.2f},{travel_distance:.2f}\n")

            # Spawn a new target and reset for the next trial
            trial_number += 1
            target_x, target_y = random_position(target_radius)
            trial_start_time = time.time()
            travel_distance = 0.0

        # Draw everything
        screen.fill((0, 0, 0))

        # Draw axis lines & label
        draw_axes()

        # Draw the target
        pygame.draw.circle(screen, target_color, (target_x, target_y), target_radius)

        # Draw the green circle (player)
        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

        # Optional: display some info on screen (e.g., real-time travel distance)
        info_text = (
            f"Trial: {trial_number}   "
            f"Travel Distance: {travel_distance:.1f}px   "
            f"Axes: ({axis_x:.2f}, {axis_y:.2f})"
        )
        text_surf = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surf, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
