import time

from config import (
    PRESS_ZONE_X,
    SCREEN_HEIGHT,
    TICK_DURATION,
    ABILITY_IMAGES,
    ABILITY_SPACING_Y,
    SCREEN_WIDTH,
    EXCLUDED_DIAL_ANIMATIONS,
    USER_KEYBINDS,
    BOSS_FILE,
)
from dial_animation import DialAnimation
from ability import Ability, TickBar
import pygame

# import tkinter as tk
from tkinter import messagebox

import sys
import json
import os
import threading
import keyboard
import win32con
import win32gui


def make_window_always_on_top():
    hwnd = win32gui.GetForegroundWindow()  # Get current foreground window
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )


# Initialize Pygame
def triggerrstrainer(rotation_file: str):
    try:
        with open(USER_KEYBINDS, "r", encoding="utf-8") as f:
            keybinds = json.load(f)
    except json.JSONDecodeError as e:
        error_message = (
            f"Error: Your .JSON file is not formatted correctly.\n"
            f"Fix it at: '{USER_KEYBINDS}'\n"
            f"Line {e.lineno}, Column {e.colno}.\n"
            f"Message: {e.msg}"
        )
        messagebox.showerror("Error", error_message)
        sys.exit()
    except FileNotFoundError:
        error_message = f"Error: The file '{USER_KEYBINDS}' was not found."
        messagebox.showerror("Error", error_message)
        sys.exit()

    ABILITY_KEYBINDS = keybinds["ABILITY_KEYBINDS"]

    try:
        with open(rotation_file, "r", encoding="utf-8") as f:
            ability_sequence = json.load(f)
    except json.JSONDecodeError as e:
        error_message = (
            f"Error: Your .JSON file is not formatted correctly.\n"
            f"Fix it at: '{rotation_file}'\n"
            f"Line {e.lineno}, Column {e.colno}.\n"
            f"Message: {e.msg}"
        )
        messagebox.showerror("Error", error_message)
        sys.exit()
    except FileNotFoundError:
        error_message = f"Error: The file '{rotation_file}' was not found."
        messagebox.showerror("Error", error_message)
        sys.exit()

    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        error_message = (
            f"Error: Your .JSON file is not formatted correctly.\n"
            f"Fix it at: '{os.path.abspath('config.json')}'\n"
            f"Line {e.lineno}, Column {e.colno}.\n"
            f"Message: {e.msg}"
        )
        messagebox.showerror("Error", error_message)
        sys.exit()
    except FileNotFoundError:
        error_message = f"Error: The file '{USER_KEYBINDS}' was not found."
        messagebox.showerror("Error", error_message)
        sys.exit()

    pygame.init()
    pygame.display.set_caption("RS Trainer")
    icon = pygame.image.load("resources/azulyn_icon.ico")
    pygame.display.set_icon(icon)

    win_w, win_h = 800, 600

    # Create Pygame screen and set window position
    screen = pygame.display.set_mode((win_w, win_h))
    make_window_always_on_top()

    # Game Variables
    press_zone_rect = pygame.Rect(
        PRESS_ZONE_X, (SCREEN_HEIGHT // 2) - 225, 1, 450
    )  # 1 pixel wide with extra height
    tick_bars: list[TickBar] = []  # Store tick bars

    # Game variables
    global running
    running = True
    clock = pygame.time.Clock()
    spawned_abilities: list[Ability] = []
    current_tick = 0
    next_tick_time = time.time() + TICK_DURATION
    score = 0
    total_abilities = len(ability_sequence)
    missed_abilities = 0
    tick_ability_counts = {}  # Dictionary to track abilities stacking per tick
    pygame.event.set_allowed(
        [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.KEYUP]
    )
    dial_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
    dial_animation_queue = []  # Queue for animations
    current_animation = None  # Track the currently playing animation
    feedback_message = None  # Store feedback message
    feedback_timer = 0  # Timer for feedback message
    global held_keys, new_keys
    held_keys = set()
    new_keys = set()

    # Main Game Loop
    def global_key_listener():
        global running
        global held_keys
        global testvariablehook

        def on_key_event(e: keyboard.KeyboardEvent):
            global new_keys

            key: str | None = e.name
            if key is not None:
                if e.event_type == "down":
                    if "shift" in key.lower():
                        key = "shift"
                    if "ctrl" in key.lower():
                        key = "ctrl"
                    if "alt" in key.lower():
                        key = "alt"
                    if key not in held_keys:
                        held_keys.add(key)
                        new_keys.add(key)
                        print(f"[GLOBAL] Key pressed: {key}")

                elif e.event_type == "up":
                    if "shift" in key.lower():
                        key = "shift"
                    if "ctrl" in key.lower():
                        key = "ctrl"
                    if "alt" in key.lower():
                        key = "alt"
                    if key in held_keys:
                        print(f"[GLOBAL] Key released: {key}")
                        held_keys.discard(key)
                    if key in new_keys:
                        new_keys.discard(key)

        testvariablehook = keyboard.hook(on_key_event)
        keyboard.wait("esc")
        keyboard.unhook_all()
        print("Hook unset")
        # sys.exit()
        # print(testvariablehook)

    # Start the global key listener
    threading.Thread(target=global_key_listener, daemon=True).start()

    while running:
        screen.fill((0, 0, 0))  # Clear screen
        dt = clock.tick(60) / 1000.0  # Convert milliseconds to seconds

        if config["see_global_cooldown_animation"]:
            # Update animation
            dial_animation.update(dt)

            # If no animation is playing, start the next one from the queue
            if current_animation is None and dial_animation_queue:
                current_animation = dial_animation_queue.pop(
                    0
                )  # Start the next animation
                current_animation.start()  # Ensure it begins playing

            # Update and draw the current animation
            if current_animation:
                current_animation.update(dt)
                if not current_animation.active:
                    current_animation = None  # Move to the next animation when done

            # Draw the current animation
            if current_animation:
                current_animation.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Tick system: Check if it's time for the next tick
        current_time = time.time()
        if current_time >= next_tick_time:
            current_tick += 1
            next_tick_time += TICK_DURATION  # Add 0.6s to next tick

            # Spawn abilities based on tick timing
            for ability_data in ability_sequence:
                if ability_data["tick"] == current_tick:
                    ability = ability_data["ability"]

                    if ability in ABILITY_KEYBINDS and ability in ABILITY_IMAGES:
                        key = ABILITY_KEYBINDS[ability]  # Get mapped keybind
                        image_path = ABILITY_IMAGES[ability]  # Get mapped image
                        width = ability_data.get(
                            "width", 75
                        )  # Default width to 75 if not provided

                        # Debug log for missing abilities
                        print(
                            f"Spawning ability: {ability}, Keys: {key}, Tick: {current_tick}, Width: {width}"
                        )

                        tick_count = tick_ability_counts.get(current_tick, 0)
                        ability_y = (SCREEN_HEIGHT // 4) + (
                            tick_count * ABILITY_SPACING_Y
                        )
                        if key == []:
                            key = ["MOUSE"]
                        ability = Ability(
                            ability=ability,
                            key=key,
                            image_path=image_path,
                            start_x=SCREEN_WIDTH,  # + added_x_spacing,
                            start_y=ability_y,
                            width=width,
                            visible=config["see_ability_icons"],
                            keybinds_visible=config["see_keybinds"],
                        )
                        spawned_abilities.append(ability)
                        tick_ability_counts[current_tick] = tick_count + 1

            tick_bars.append(TickBar(SCREEN_WIDTH))  # Always spawn from the right side

        # Update and draw abilities
        for ability in spawned_abilities:
            result = ability.update(dt)
            if result == "missed":
                missed_abilities += 1
            ability.draw(screen)

        # Update and draw tick bars
        for bar in tick_bars:
            bar.update(press_zone_rect, dt)
            bar.draw(screen)

        # Remove expired tick bars and abilities
        tick_bars = [bar for bar in tick_bars if bar.active]
        spawned_abilities = [ability for ability in spawned_abilities if ability.active]

        # Draw pressing zone
        pygame.draw.rect(screen, (255, 0, 0), press_zone_rect)

        # keys = pygame.key.get_pressed()

        # Check for hits
        for ability in spawned_abilities[:]:
            try:
                required_keys_pressed: bool = False  # Assume key is NOT pressed

                # for k in ability.key:
                #     k = k.strip().upper()  # Normalize key formatting

                #     required_keys_pressed = all(
                #         (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
                #         if k == "SHIFT"
                #         else (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL])
                #         if k in ["CTRL", "LCTRL"]
                #         else (keys[pygame.K_LALT] or keys[pygame.K_RALT])
                #         if k == "ALT"
                #         else (
                #             keys[pygame.K_LEFTBRACKET]
                #             if k == "["
                #             else keys[pygame.K_RIGHTBRACKET]
                #             if k == "]"
                #             else keys[pygame.K_BACKSLASH]
                #             if k == "\\"
                #             else keys[pygame.K_MINUS]
                #             if k == "-"
                #             else keys[pygame.K_COMMA]
                #             if k == ","
                #             else keys[pygame.K_BACKQUOTE]
                #             if k == "`"
                #             else pygame.mouse.get_pressed()[0]
                #             if k == "MOUSE"
                #             else keys[getattr(pygame, f"K_F{k[1:]}")]
                #             if k.startswith("F") and k[1:].isdigit()
                #             else keys[getattr(pygame, f"K_{k.lower()}")]
                #             if getattr(pygame, f"K_{k.lower()}", None)
                #             else False
                #         )
                #         for k in ability.key
                #     )
                # if not required_keys_pressed:

                if any(k.lower() in new_keys for k in ability.key) and all(
                    (k.lower() in new_keys or k.lower() in held_keys)
                    for k in ability.key
                ):
                    required_keys_pressed = True
                    new_keys = set()

                # ✅ **Check if the ability should trigger the dial animation**
                if required_keys_pressed and press_zone_rect.colliderect(ability.rect):
                    print(f"Hit detected: {ability.ability}")  # Debugging log
                    score += 1
                    spawned_abilities.remove(ability)
                    feedback_message = "Correct"
                    feedback_timer = time.time() + 1
                    # ✅ **Only add animation if the ability is NOT in the exclusion list**
                    if ability.ability not in EXCLUDED_DIAL_ANIMATIONS:
                        new_animation = DialAnimation(win_w // 2 - 25, win_h - 75)
                        dial_animation_queue.append(new_animation)
                if feedback_message and time.time() < feedback_timer:
                    font = pygame.font.Font(None, 22)
                    if config["see_correct_or_incorrect_feedback_message"]:
                        if feedback_message == "Wrong!":
                            # TODO: This doesn't actually fire
                            feedback_text = font.render(
                                feedback_message, True, (255, 0, 0)
                            )
                        else:
                            feedback_text = font.render(
                                feedback_message, True, (0, 255, 0)
                            )
                        screen.blit(
                            feedback_text,
                            (
                                win_w // 2 - feedback_text.get_width() // 2,
                                win_h // 2 - feedback_text.get_height() // 2,
                            ),
                        )
                else:
                    feedback_message = None
            except KeyError:
                print(f"Warning: Unrecognized ability in ability: {ability.ability}")

        # Display score
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        # clock.tick(30)  # 60 FPS

        # Check if all abilities have played
        if (current_tick - 15) >= max(
            [n["tick"] for n in ability_sequence]
        ) and not spawned_abilities:
            # game_over = True
            running = False  # End game loop

    # Show results screen
    def show_results(screen, score, total_abilities, missed_abilities):
        accuracy = (score / total_abilities) * 100 if total_abilities > 0 else 0
        font = pygame.font.Font(None, 48)
        screen.fill((0, 0, 0))

        results = [
            "Game Over!",
            f"Final Score: {score}",
            f"Total Abilities: {total_abilities}",
            f"Missed Abilities: {missed_abilities}",
            f"Accuracy: {accuracy:.2f}%",
            "Press ESC to exit",
        ]

        for i, text in enumerate(results):
            rendered_text = font.render(text, True, (255, 255, 255))
            screen.blit(rendered_text, (SCREEN_WIDTH // 2 - 150, 200 + i * 50))

        pygame.display.flip()

    # Display results
    show_results(screen, score, total_abilities, missed_abilities)

    # Exit screen handling
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                waiting = False
    keyboard.unhook_all()
    pygame.quit()


if __name__ == "__main__":
    triggerrstrainer(BOSS_FILE)
