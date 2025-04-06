import pygame
import sys
import random
import math
import time
import os

def main():
    pygame.init()

    # --------------------------------------------------------------------------
    # -- ADJUSTABLE PARAMETERS --
    # --------------------------------------------------------------------------
    FULLSCREEN = True                    # Toggle fullscreen or windowed mode

    # Movement / Position Sensitivities
    CIRCLE_POSITION_SENSITIVITY = 20
    SQUARE_POSITION_SENSITIVITY = 60

    TARGET_REACH_THRESHOLD = 30.0        # Distance (pixels) to consider the target reached

    # Circle Size Ranges (for randomizing each trial)
    RED_RADIUS_MIN = 5
    RED_RADIUS_MAX = 200
    GREEN_RADIUS_MIN = 5
    GREEN_RADIUS_MAX = 200

    # Clamps for green circle growth/shrink
    CIRCLE_MIN_RADIUS = 5                # Green circle can't get smaller than this
    CIRCLE_MAX_RADIUS = 200              # Green circle can't get larger than this
    SIZE_SENSITIVITY = 4.0               # How fast the green circle grows/shrinks

    # ±10% size tolerance relative to the red circle’s radius
    RELATIVE_SIZE_TOLERANCE = 0.1        # 0.1 => ±10%

    # Joystick Deadzones
    DEADZONEx_circ = 0.1
    DEADZONEy_circ = 0.1
    DEADZONEz_circ = 0

    DEADZONEx_sq = 0
    DEADZONEy_sq = 0

    # Minimum distance constraints
    MIN_START_DISTANCE = 150             # green circle vs. red circle must be at least this far
    MIN_RADIUS_DIFFERENCE = 30           # |RedRadius - GreenRadius| must be >= this at trial start
    MIN_ELEMENT_DISTANCE = 150           # circle vs. square min distance

    # -------------------------------
    # JOYSTICK AXIS CONFIG (Circle)
    # -------------------------------
    CIRCLE_X_AXIS_INDEX = 5
    CIRCLE_X_AXIS_INVERT = 1

    CIRCLE_Y_AXIS_INDEX = 6
    CIRCLE_Y_AXIS_INVERT = -1

    CIRCLE_Z_AXIS_INDEX = 7  # used for circle size
    CIRCLE_Z_AXIS_INVERT = 1

    # -------------------------------
    # JOYSTICK AXIS CONFIG (Square)
    # -------------------------------
    SQUARE_X_AXIS_INDEX = 2
    SQUARE_X_AXIS_INVERT = -1

    SQUARE_Y_AXIS_INDEX = 0
    SQUARE_Y_AXIS_INVERT = -1

    # Square size
    RED_SQUARE_MIN = 50
    RED_SQUARE_MAX = 200
    # The green square uses the same side length each trial (no in-trial size change).

    # --------------------------------------------------------------------------

    # -- SCREEN SETUP --
    display_info = pygame.display.Info()
    screen_width, screen_height = display_info.current_w, display_info.current_h

    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((1280, 720))

    pygame.display.set_caption("Circle & Square Locking Once Target Reached")

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

    # Colors
    circle_color = (0, 255, 0)         # Green Circle
    circle_target_color = (255, 0, 0)  # Red Circle
    square_color = (0, 180, 0)         # Green Square
    square_target_color = (180, 0, 0)  # Red Square

    # For storing object states (positions, sizes).
    circle_x = 0
    circle_y = 0
    green_circle_radius = 0
    target_circle_x = 0
    target_circle_y = 0
    red_circle_radius = 0

    square_x = 0
    square_y = 0
    green_square_side = 0
    target_square_x = 0
    target_square_y = 0
    red_square_side = 0

    # -------------------------------------------------------------------------
    # Helper: circles_overlap (used to ensure no start overlap between shapes)
    # -------------------------------------------------------------------------
    def circles_overlap(x1, y1, r1, x2, y2, r2):
        dist = math.hypot(x2 - x1, y2 - y1)
        return dist < (r1 + r2)

    # -------------------------------------------------------------------------
    # Helper: random_circle_center
    # -------------------------------------------------------------------------
    def random_circle_center(rad):
        x = random.randint(rad, screen_width - rad)
        y = random.randint(rad, screen_height - rad)
        return x, y

    # -------------------------------------------------------------------------
    # Helper: random_square_center
    # -------------------------------------------------------------------------
    def random_square_center(s):
        half_s = s / 2.0
        x = random.randint(int(half_s), int(screen_width - half_s))
        y = random.randint(int(half_s), int(screen_height - half_s))
        return x, y

    # -------------------------------------------------------------------------
    # randomize_new_trial
    # -------------------------------------------------------------------------
    def randomize_new_trial():
        """
        Picks new positions/sizes for:
          - Red & Green circles
          - Red & Green squares
        Ensures no overlap and meets minimal distance constraints.
        """
        while True:
            # 1) Red / Green circle radius
            r_red = random.randint(RED_RADIUS_MIN, RED_RADIUS_MAX)
            r_green = random.randint(GREEN_RADIUS_MIN, GREEN_RADIUS_MAX)
            if abs(r_red - r_green) < MIN_RADIUS_DIFFERENCE:
                continue

            # 2) Red circle position
            rcx, rcy = random_circle_center(r_red)

            # 3) Green circle position (≥ MIN_START_DISTANCE away)
            attempts = 0
            while True:
                attempts += 1
                gcx, gcy = random_circle_center(r_green)
                dist_c = math.hypot(rcx - gcx, rcy - gcy)
                if dist_c >= MIN_START_DISTANCE:
                    break
                if attempts > 5000:
                    break

            # 4) Red square side + position
            rs_side = random.randint(RED_SQUARE_MIN, RED_SQUARE_MAX)
            red_sq_bound = (rs_side * math.sqrt(2)) / 2.0
            rsx, rsy = random_square_center(rs_side)

            # 5) Green square side + position (same side length as red)
            gs_side = rs_side
            green_sq_bound = (gs_side * math.sqrt(2)) / 2.0

            # Attempt to place green square
            attempts2 = 0
            while True:
                attempts2 += 1
                gsx, gsy = random_square_center(gs_side)
                # Check no overlap with red circle
                if circles_overlap(rcx, rcy, r_red, gsx, gsy, green_sq_bound):
                    pass
                # Check no overlap with green circle
                elif circles_overlap(gcx, gcy, r_green, gsx, gsy, green_sq_bound):
                    pass
                # Check no overlap with red square
                elif circles_overlap(rsx, rsy, red_sq_bound, gsx, gsy, green_sq_bound):
                    pass
                else:
                    break
                if attempts2 > 5000:
                    break

            # Also ensure red square doesn't overlap red circle
            if circles_overlap(rcx, rcy, r_red, rsx, rsy, red_sq_bound):
                continue

            # Check minimal distances among shapes
            dist_redcirc_redsq = math.hypot(rcx - rsx, rcy - rsy)
            if dist_redcirc_redsq < (r_red + red_sq_bound + MIN_ELEMENT_DISTANCE):
                continue
            dist_redcirc_greensq = math.hypot(rcx - gsx, rcy - gsy)
            if dist_redcirc_greensq < (r_red + green_sq_bound + MIN_ELEMENT_DISTANCE):
                continue
            dist_greencirc_redsq = math.hypot(gcx - rsx, gcy - rsy)
            if dist_greencirc_redsq < (r_green + red_sq_bound + MIN_ELEMENT_DISTANCE):
                continue
            dist_greencirc_greensq = math.hypot(gcx - gsx, gcy - gsy)
            if dist_greencirc_greensq < (r_green + green_sq_bound + MIN_ELEMENT_DISTANCE):
                continue

            # If valid, return
            return (r_red, rcx, rcy,
                    r_green, gcx, gcy,
                    rs_side, rsx, rsy,
                    gs_side, gsx, gsy)

    def start_screen():
        """Show a 'Press ENTER to Start' screen. Press ESC to quit."""
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

            screen.fill((0, 0, 0))
            title_text = font.render("Press ENTER to Start", True, (255, 255, 255))
            rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(title_text, rect)
            pygame.display.flip()

    def wait_for_continue(average_score, total_trials):
        """Pause after each 10 trials and show average score."""
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

            screen.fill((0, 0, 0))
            msg1 = f"Trials {total_trials} Completed!"
            msg2 = f"Average Score (last 10): {average_score:.2f}"
            msg3 = "Press ENTER to continue or ESC to quit."

            text1 = font.render(msg1, True, (255, 255, 255))
            rect1 = text1.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
            screen.blit(text1, rect1)

            text2 = font.render(msg2, True, (255, 255, 255))
            rect2 = text2.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(text2, rect2)

            text3 = font.render(msg3, True, (255, 255, 255))
            rect3 = text3.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
            screen.blit(text3, rect3)

            pygame.display.flip()
            clock.tick(60)

    # --------------------------------------------------------------------------
    # Initialize the first trial
    # --------------------------------------------------------------------------
    (red_circle_radius,
     target_circle_x, target_circle_y,
     green_circle_radius, circle_x, circle_y,
     red_square_side, target_square_x, target_square_y,
     green_square_side, square_x, square_y) = randomize_new_trial()

    trial_number = 1
    trial_start_time = time.time()

    # --------------------------------------------------------------------------
    # Calculate the "needed distance" from the initial positions
    # (the direct distance from green shapes to red targets)
    # --------------------------------------------------------------------------
    circle_needed_distance = math.hypot(circle_x - target_circle_x,
                                        circle_y - target_circle_y)
    square_needed_distance = math.hypot(square_x - target_square_x,
                                        square_y - target_square_y)

    # Distances traveled (still tracked, but NOT used for scoring)
    circle_travel_distance = 0.0
    old_circle_x, old_circle_y = circle_x, circle_y

    square_travel_distance = 0.0
    old_square_x, old_square_y = square_x, square_y

    # Lock flags: set True once each shape meets its condition
    circle_locked = False
    square_locked = False

    clock = pygame.time.Clock()
    running = True

    # We'll store all trial records here, then write them to CSV upon exit.
    # Format (CSV columns):
    #   Trial,Time,CircleDist,SquareDist,
    #   CircleNeededDist,SquareNeededDist,
    #   RedCircleRadius,GreenCircleRadius,
    #   MinAllowedSize,MaxAllowedSize,RadiusDiff,Score
    records = []
    all_scores = []

    start_screen()

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not running:
            break

        # ---------------------------------------------------------
        # Circle updates (only if not locked)
        # ---------------------------------------------------------
        if not circle_locked:
            raw_cx = joystick.get_axis(CIRCLE_X_AXIS_INDEX)
            raw_cy = joystick.get_axis(CIRCLE_Y_AXIS_INDEX)
            raw_cz = joystick.get_axis(CIRCLE_Z_AXIS_INDEX)

            # Inversion
            axis_cx = raw_cx * CIRCLE_X_AXIS_INVERT
            axis_cy = raw_cy * CIRCLE_Y_AXIS_INVERT
            axis_cz = raw_cz * CIRCLE_Z_AXIS_INVERT

            # Deadzones
            if abs(axis_cx) < DEADZONEx_circ:
                axis_cx = 0
            if abs(axis_cy) < DEADZONEy_circ:
                axis_cy = 0
            if abs(axis_cz) < DEADZONEz_circ:
                axis_cz = 0

            # Movement
            delta_x_circ = axis_cx * CIRCLE_POSITION_SENSITIVITY
            delta_y_circ = axis_cy * CIRCLE_POSITION_SENSITIVITY
            circle_x += delta_x_circ
            circle_y += delta_y_circ

            # Clamp to screen
            if circle_x < green_circle_radius:
                circle_x = green_circle_radius
            if circle_x > screen_width - green_circle_radius:
                circle_x = screen_width - green_circle_radius
            if circle_y < green_circle_radius:
                circle_y = green_circle_radius
            if circle_y > screen_height - green_circle_radius:
                circle_y = screen_height - green_circle_radius

            # Adjust circle size
            green_circle_radius += axis_cz * SIZE_SENSITIVITY
            if green_circle_radius < CIRCLE_MIN_RADIUS:
                green_circle_radius = CIRCLE_MIN_RADIUS
            if green_circle_radius > CIRCLE_MAX_RADIUS:
                green_circle_radius = CIRCLE_MAX_RADIUS

            # Distance traveled (NOT used in final score)
            step_dist_circ = math.hypot(circle_x - old_circle_x, circle_y - old_circle_y)
            circle_travel_distance += step_dist_circ
            old_circle_x, old_circle_y = circle_x, circle_y

            # Check if circle reached
            dist_circ_to_target = math.hypot(circle_x - target_circle_x, circle_y - target_circle_y)
            min_allowed_size = red_circle_radius * (1 - RELATIVE_SIZE_TOLERANCE)
            max_allowed_size = red_circle_radius * (1 + RELATIVE_SIZE_TOLERANCE)
            if dist_circ_to_target <= TARGET_REACH_THRESHOLD and \
               min_allowed_size <= green_circle_radius <= max_allowed_size:
                # Lock the circle in place
                circle_locked = True

        # ---------------------------------------------------------
        # Square updates (only if not locked)
        # ---------------------------------------------------------
        if not square_locked:
            raw_sx = joystick.get_axis(SQUARE_X_AXIS_INDEX)
            raw_sy = joystick.get_axis(SQUARE_Y_AXIS_INDEX)

            axis_sx = raw_sx * SQUARE_X_AXIS_INVERT
            axis_sy = raw_sy * SQUARE_Y_AXIS_INVERT

            if abs(axis_sx) < DEADZONEx_sq:
                axis_sx = 0
            if abs(axis_sy) < DEADZONEy_sq:
                axis_sy = 0

            # Movement
            delta_x_sq = axis_sx * SQUARE_POSITION_SENSITIVITY
            delta_y_sq = axis_sy * SQUARE_POSITION_SENSITIVITY
            square_x += delta_x_sq
            square_y += delta_y_sq

            # Clamp to screen
            half_gs = green_square_side / 2.0
            if square_x < half_gs:
                square_x = half_gs
            if square_x > screen_width - half_gs:
                square_x = screen_width - half_gs
            if square_y < half_gs:
                square_y = half_gs
            if square_y > screen_height - half_gs:
                square_y = screen_height - half_gs

            # Distance traveled (NOT used in final score)
            step_dist_sq = math.hypot(square_x - old_square_x, square_y - old_square_y)
            square_travel_distance += step_dist_sq
            old_square_x, old_square_y = square_x, square_y

            # Check if square reached
            dist_sq_to_target = math.hypot(square_x - target_square_x, square_y - target_square_y)
            if dist_sq_to_target <= TARGET_REACH_THRESHOLD:
                # Lock the square in place
                square_locked = True

        # ---------------------------------------------------------
        # If both locked, this trial is done
        # ---------------------------------------------------------
        if circle_locked and square_locked:
            response_time = time.time() - trial_start_time

            # Score based on:
            #   1) radius_diff * 3.0 / response_time
            #   2) (circle_needed_distance + square_needed_distance) / response_time
            radius_diff = abs(red_circle_radius - green_circle_radius)
            needed_dist_sum = circle_needed_distance + square_needed_distance

            score = (radius_diff * 3.0 / response_time) + \
                    (needed_dist_sum / response_time)

            print(f"\nTrial {trial_number} Reached!")
            print(f"  Time: {response_time:.2f}s")
            print(f"  (Actual) Circle Dist: {circle_travel_distance:.2f}px")
            print(f"  (Actual) Square Dist: {square_travel_distance:.2f}px")
            print(f"  (Needed) Circle Dist: {circle_needed_distance:.2f}px")
            print(f"  (Needed) Square Dist: {square_needed_distance:.2f}px")
            print(f"  Circle Final Size: {green_circle_radius:.2f}px "
                  f"(Allowed Range: [{min_allowed_size:.1f}, {max_allowed_size:.1f}])")
            print(f"  Red Circle Radius: {red_circle_radius:.2f}px")
            print(f"  Radius Diff: {radius_diff:.2f}px")
            print(f"  Score: {score:.2f}")

            # Record
            records.append((
                trial_number,
                round(response_time, 2),
                round(circle_travel_distance, 2),  # actual traveled
                round(square_travel_distance, 2),  # actual traveled
                round(circle_needed_distance, 2),  # needed
                round(square_needed_distance, 2),  # needed
                round(red_circle_radius, 2),
                round(green_circle_radius, 2),
                round(min_allowed_size, 2),
                round(max_allowed_size, 2),
                round(radius_diff, 2),
                round(score, 2)
            ))

            # Check if we do a wait_for_continue
            if trial_number % 10 == 0:
                all_scores.append(score)
                last_10_scores = all_scores[-10:]
                avg_10 = sum(last_10_scores) / len(last_10_scores)
                wait_for_continue(avg_10, trial_number)
            else:
                all_scores.append(score)

            # Next trial
            trial_number += 1
            trial_start_time = time.time()

            circle_travel_distance = 0.0
            square_travel_distance = 0.0

            # Randomize everything for the next trial
            (red_circle_radius,
             target_circle_x, target_circle_y,
             green_circle_radius, circle_x, circle_y,
             red_square_side, target_square_x, target_square_y,
             green_square_side, square_x, square_y) = randomize_new_trial()

            # Store the new initial "needed distance" for next trial
            circle_needed_distance = math.hypot(circle_x - target_circle_x,
                                                circle_y - target_circle_y)
            square_needed_distance = math.hypot(square_x - target_square_x,
                                                square_y - target_square_y)

            # Reset old coords and locks
            old_circle_x, old_circle_y = circle_x, circle_y
            old_square_x, old_square_y = square_x, square_y
            circle_locked = False
            square_locked = False

        # ----------------------------------------------------------------------
        # DRAW
        # ----------------------------------------------------------------------
        screen.fill((0, 0, 0))

        # Draw red circle target ONLY if not locked
        if not circle_locked:
            pygame.draw.circle(
                screen, circle_target_color,
                (int(target_circle_x), int(target_circle_y)),
                red_circle_radius
            )
        # Always draw the green circle
        pygame.draw.circle(
            screen, circle_color,
            (int(circle_x), int(circle_y)),
            int(green_circle_radius)
        )

        # Draw red square target ONLY if not locked
        if not square_locked:
            half_rs = red_square_side / 2.0
            red_sq_rect = pygame.Rect(
                target_square_x - half_rs,
                target_square_y - half_rs,
                red_square_side,
                red_square_side
            )
            pygame.draw.rect(screen, square_target_color, red_sq_rect)

        # Always draw the green square
        half_gs = green_square_side / 2.0
        green_sq_rect = pygame.Rect(
            square_x - half_gs,
            square_y - half_gs,
            green_square_side,
            green_square_side
        )
        pygame.draw.rect(screen, square_color, green_sq_rect)

        # Info text
        info_lines = [
            f"Trial: {trial_number}",
            f"Circle Pos=({int(circle_x)}, {int(circle_y)}) Radius={int(green_circle_radius)}" +
            (" [LOCKED]" if circle_locked else ""),
            f"Square Pos=({int(square_x)}, {int(square_y)}) Side={int(green_square_side)}" +
            (" [LOCKED]" if square_locked else ""),
            f"(Actual) CircleDist={circle_travel_distance:.1f}  (Needed) CircleDist={circle_needed_distance:.1f}",
            f"(Actual) SquareDist={square_travel_distance:.1f}  (Needed) SquareDist={square_needed_distance:.1f}"
        ]
        for i, line in enumerate(info_lines):
            text_surf = font.render(line, True, (255, 255, 255))
            screen.blit(text_surf, (10, 10 + i*30))

        pygame.display.flip()

    pygame.quit()

    # --------------------------------------------------------------------------
    # Write records to CSV upon exit
    # --------------------------------------------------------------------------
    if records:
        csv_path = "C:\\Capstone Values\\values.csv"
        with open(csv_path, "w") as f:
            # Headers:
            f.write(
                "Trial,Time,"
                "CircleTraveledDist,SquareTraveledDist,"
                "CircleNeededDist,SquareNeededDist,"
                "RedCircleRadius,GreenCircleRadius,"
                "MinAllowedSize,MaxAllowedSize,RadiusDiff,Score\n"
            )
            for row in records:
                f.write(",".join(map(str, row)) + "\n")

        print(f"Data saved to {csv_path}")
    else:
        print("No trials were completed, so no data was saved.")


if __name__ == "__main__":
    main()
