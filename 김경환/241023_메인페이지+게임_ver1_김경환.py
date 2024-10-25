import tkinter as tk
from tkinter import ttk
import random


def create_items(canvas, item_info, images):
    items = []

    def is_overlapping(x, y, item_size):
        for item, _ in items:
            item_coords = canvas.coords(item)
            existing_x = item_coords[0]
            existing_y = item_coords[1]
            if (existing_x - item_size[0] < x < existing_x + item_size[0] and
                existing_y - item_size[1] < y < existing_y + item_size[1]):
                return True
        return False

    for item_type, info in item_info.items():
        item_photo = tk.PhotoImage(file=info['path'])
        images.append(item_photo)

        item_size = (item_photo.width() // 2, item_photo.height() // 2)

        for _ in range(info["count"]):
            while True:
                x = random.randint(100, 928)
                y = random.randint(50, 670)
                if not is_overlapping(x, y, item_size):
                    break

            item = canvas.create_image(x, y, image=item_photo)
            if item:
                items.append((item, item_type))
            else:
                print(f"{item_type} 생성 실패")

    return items


def create_background(canvas):
    background_image = tk.PhotoImage(file='bg_img/main_page.png')  # 배경 이미지 파일 경로
    canvas.create_image(0, 0, anchor='nw', image=background_image)
    canvas.background_image = background_image  # 배경 이미지를 유지하기 위해 참조 저장


def create_game_window():
    root = tk.Tk()
    root.title("누가누가 꼴찌할까?")

    canvas = tk.Canvas(root, width=1280, height=720)
    canvas.pack()

    create_background(canvas)  # 배경 생성

    item_info = {
        "chestnut": {"path": "icon_img/chestnut.png", "count": 2},
        "cobweb": {"path": "icon_img/cobweb.png", "count": 2},
        "poison": {"path": "icon_img/poison.png", "count": 2},
        "ballon": {"path": "icon_img/ballon.png", "count": 2},
        "gold": {"path": "icon_img/gold.png", "count": 2},
        "hole": {"path": "icon_img/hole.png", "count": 2},
        "random": {"path": "icon_img/random.png", "count": 2},
    }

    root.images = []
    items = create_items(canvas, item_info, root.images)

    player_images = [
        tk.PhotoImage(file='icon_img/cat.png'),
        tk.PhotoImage(file='icon_img/dog.png'),
        tk.PhotoImage(file='icon_img/frog.png'),
        tk.PhotoImage(file='icon_img/panda.png'),
        tk.PhotoImage(file='icon_img/pig.png'),
        tk.PhotoImage(file='icon_img/rabbit.png'),
        tk.PhotoImage(file='icon_img/squirrel.png'),
    ]

    root.images.extend(player_images)

    players = []
    for i in range(7):
        player = canvas.create_image(60, 100 + i * 100, image=player_images[i])
        players.append(player)

    start_button = ttk.Button(root, text="Start", command=lambda: start_race(canvas, players, start_button, items))
    start_button.pack()

    return root, canvas, players, items


def start_race(canvas, players, start_button, items):
    start_button.config(state='disabled')
    print(f"Starting race with {len(items)} items")

    for player in players:
        canvas.after(100, lambda p=player: move_player(canvas, p, items))


def move_player(canvas, player, items):
    print(f"Moving player {player}")

    dx = 5
    vertical_direction = random.choice([-1, 0, 1])
    dy = vertical_direction * 10 if vertical_direction != 0 else 0

    canvas.move(player, dx, dy)

    player_coords = canvas.coords(player)
    if player_coords[1] < 20:
        canvas.move(player, 0, 20 + player_coords[1])
    elif player_coords[1] > 700:
        canvas.move(player, 0, 700 - player_coords[1])

    for item, item_type in items[:]:
        item_coords = canvas.coords(item)
        if check_collision(player_coords, item_coords):
            if item_type == "chestnut":
                canvas.move(player, -100, 0)
            elif item_type == "cobweb":
                canvas.move(player, -100, 0)
            elif item_type == "ballon":
                canvas.move(player, +100, 0)
            elif item_type == "gold":
                canvas.move(player, +100, 0)
            elif item_type == "hole":
                canvas.move(player, +100, 0)
            elif item_type == "poison":
                canvas.move(player, -100, 0)
            elif item_type == "random":
                canvas.move(player, -100, 0)

            canvas.delete(item)
            items.remove((item, item_type))
            print(f"Player {player} 아이템 획득!")

    if not check_finish(canvas, player):
        print(f"Scheduling next move for player {player}")
        canvas.after(100, lambda: move_player(canvas, player, items))


def check_collision(player_coords, item_coords):
    player_center_x = player_coords[0] + 10
    player_center_y = player_coords[1] + 10

    item_center_x, item_center_y = item_coords

    distance = ((player_center_x - item_center_x) ** 2 + (player_center_y - item_center_y) ** 2) ** 0.5

    collision_distance = 10 + 10

    return distance <= collision_distance


def check_finish(canvas, player):
    coords = canvas.coords(player)
    if coords[0] >= 1008:
        print(f"Player {player} 완주!")
        return True
    return False


# 게임 윈도우 생성 및 메인 루프 시작
root, canvas, players, items = create_game_window()
root.mainloop()
