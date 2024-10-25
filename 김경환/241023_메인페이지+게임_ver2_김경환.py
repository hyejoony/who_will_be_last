import tkinter as tk
from tkinter import ttk
import random

# 전역 변수 초기화
mouse_x = 0
mouse_y = 0
mouse_c = 0
cnt = 0
# 플레이어의 속도와 정지 상태를 관리할 딕셔너리
player_speeds = {}
player_stopped = {}
players = []

def mouse_move(e):
    """마우스가 움직일 때 호출되는 함수"""
    global mouse_x, mouse_y
    mouse_x = e.x  # 마우스의 현재 x 좌표 저장
    mouse_y = e.y  # 마우스의 현재 y 좌표 저장

def mouse_press(e):
    """마우스 버튼을 눌렀을 때 호출되는 함수"""
    global mouse_c
    mouse_c = 1  # 마우스 클릭 상태를 1로 설정

# Tkinter 윈도우 생성 및 설정
root = tk.Tk()
root.title('노부부와 보호인')  # 윈도우 제목 설정
root.resizable(False, False)  # 창 크기 조정 비활성화
root.bind("<Motion>", mouse_move)  # 마우스 움직임 이벤트 바인딩
root.bind("<ButtonPress>", mouse_press)  # 마우스 클릭 이벤트 바인딩
root.geometry('1280x720')  # 창 크기 설정

# 캔버스 생성 및 배경 이미지 설정
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# 초기 화면에 보여줄 이미지 설정
img = tk.PhotoImage(file='bg_img/intro_page.png')
canvas.create_image(640, 360, image=img)  # 캔버스에 중앙에 배경 이미지 추가

# 전역 변수 초기화
index = 'intro_page'  # 현재 페이지를 나타내는 변수 (인트로 페이지부터 시작)
image_id = None  # 현재 캔버스에 표시된 이미지 객체의 ID 저장
image_ids = []  # info 페이지에서 추가된 이미지를 저장할 리스트
img_objects = []  # 이미지 참조를 유지하기 위한 리스트 (이미지 해제를 방지)

# 게임 시작 함수
def create_items(canvas, item_info, images):
    items = []

    def is_overlapping(x, y, item_size):
        # 상하좌우 100px 범위를 고려한 겹침 여부 검사
        for item, _ in items:
            item_coords = canvas.coords(item)
            existing_x = item_coords[0]
            existing_y = item_coords[1]
            
            # 아이템 간 최소 거리 (상하좌우 100px)
            min_distance_x = item_size[0] + 100
            min_distance_y = item_size[1] + 100
            
            # 아이템 간 거리 비교
            if (existing_x - min_distance_x < x < existing_x + min_distance_x and
                existing_y - min_distance_y < y < existing_y + min_distance_y):
                return True
        return False

    for item_type, info in item_info.items():
        item_photo = tk.PhotoImage(file=info['path'])
        images.append(item_photo)

        item_size = (item_photo.width() // 2, item_photo.height() // 2)

        for _ in range(info["count"]):
            while True:
                # 아이템을 화면 범위 내에서 랜덤한 좌표에 배치
                x = random.randint(100, 928)
                y = random.randint(50, 670)
                # 다른 아이템과 겹치지 않을 때까지 반복
                if not is_overlapping(x, y, item_size):
                    break

            # 아이템을 생성하고 리스트에 추가
            item = canvas.create_image(x, y, image=item_photo)
            if item:
                items.append((item, item_type))
            else:
                print(f"{item_type} 생성 실패")

    return items



def create_game_window():
    global players

    item_info = {
        "chestnut": {"path": "icon_img/chestnut.png", "count": 3},
        "cobweb": {"path": "icon_img/cobweb.png", "count": 3},
        "poison": {"path": "icon_img/poison.png", "count": 3},
        "ballon": {"path": "icon_img/ballon.png", "count": 3},
        "gold": {"path": "icon_img/gold.png", "count": 3},
        "hole": {"path": "icon_img/hole.png", "count": 3},
        "random": {"path": "icon_img/random.png", "count": 3},
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
        player = canvas.create_image(24, 72 + i * 96, image=player_images[i])
        players.append(player)

    start_button = ttk.Button(root, text="Start", command=lambda: start_race(canvas, players, start_button, items))
    start_button.place(x=1100, y=600)
    return players, items

def start_race(canvas, players, start_button, items):
    start_button.config(state='disabled')
    print(f"Starting race with {len(items)} items")

    for player in players:
        canvas.after(100, lambda p=player: move_player(canvas, p, items, start_button))


def move_player(canvas, player, items, start_button):
    # 플레이어별 기본 속도 설정 (없으면 4로 기본 설정)
    if player not in player_speeds:
        player_speeds[player] = 4

    # 플레이어 정지 상태가 없으면 False로 기본 설정
    if player not in player_stopped:
        player_stopped[player] = False

    # 정지 상태인 경우 움직이지 않음
    if player_stopped[player]:
        print(f"Player {player} is stopped!")
        canvas.after(100, lambda: move_player(canvas, player, items, start_button))
        return

    speed = player_speeds[player]
    
    print(f"Moving player {player} with speed {speed}")

    # dx는 플레이어의 현재 속도 범위에 맞게 설정
    dx = speed
    vertical_direction = random.choice([-1, 0, 1])
    dy = vertical_direction * speed if vertical_direction != 0 else 0

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
            # 해당 플레이어를 2초간 정지 상태로 변경
            elif item_type == "cobweb":
                print(f"Player {player} is caught in a cobweb and will stop for 2 seconds!")
                player_stopped[player] = True
                canvas.after(3000, lambda: resume_player(player))  # 2초 후 다시 움직임
            elif item_type == "ballon":
                canvas.move(player, +100, 0)
            # 해당 플레이어의 속도만 5로 설정
            elif item_type == "gold":
                player_speeds[player] = 5
                print(f"Player {player}'s speed increased to {player_speeds[player]}")
            # 해당 플레이어를 처음 위치로 이동
            elif item_type == "hole":
                canvas.move(player, -player_coords[0] + 24, 0)
            # 해당 플레이어의 속도만 3으로 설정
            elif item_type == "poison":
                player_speeds[player] = 3
                print(f"Player {player}'s speed increased to {player_speeds[player]}")
            elif item_type == "random":
                # 랜덤 동작 수행
                print(f"Player {player} hit a random item!")
                random_action(canvas)

            canvas.delete(item)
            items.remove((item, item_type))
            print(f"Player {player} 아이템 획득!")

    if not check_finish(canvas, player, start_button):
        print(f"Scheduling next move for player {player}")
        canvas.after(100, lambda: move_player(canvas, player, items, start_button))

# 2초 후 플레이어를 다시 움직이게 함
def resume_player(player):
    player_stopped[player] = False
    print(f"Player {player} is now free from the cobweb!")

# 랜덤 행동 함수
def random_action(canvas):
    global players  # 전역 변수 players 참조
    # 두 가지 동작 중 하나를 선택
    action = random.choice(["all_to_start", "shuffle_players"])

    if action == "all_to_start":
        # 모든 플레이어를 처음 위치(24픽셀)로 이동
        print("All players are moved to the start!")
        for player in players:
            canvas.coords(player, 24, canvas.coords(player)[1])
    elif action == "shuffle_players":
        # 모든 플레이어의 위치를 섞음
        print("Shuffling all players!")
        
        # 1. 각 플레이어의 현재 위치 가져오기
        player_positions = [canvas.coords(player) for player in players]
        
        # 2. 플레이어들의 위치를 섞기
        random.shuffle(player_positions)
        
        # 3. 섞인 위치를 플레이어들에게 적용
        for i, player in enumerate(players):
            new_position = player_positions[i]
            canvas.coords(player, new_position[0], new_position[1])

def check_collision(player_coords, item_coords):
    player_center_x = player_coords[0] + 50 / 2
    player_center_y = player_coords[1] + 50 / 2
    item_center_x = item_coords[0] + 35 / 2
    item_center_y = item_coords[1] + 35 / 2
    distance = ((player_center_x - item_center_x) ** 2 + (player_center_y - item_center_y) ** 2) ** 0.5
    collision_distance = (45 / 2) + (30 / 2)

    return distance <= collision_distance



def check_finish(canvas, player, start_button):
    global cnt, index, image_id, image_ids
    coords = canvas.coords(player)
    if coords[0] >= 1008:
        print(f"Player {player} 완주!")
        cnt += 1
        if cnt == 7:
            start_button.destroy()
            img = tk.PhotoImage(file='bg_img/end_page1.png')
            img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
            canvas.delete(image_id)  # 현재 이미지 삭제
            image_id = canvas.create_image(640, 360, image=img)  # 메인 페이지로 돌아감
            index = 'end_page1'  # 메인 페이지로 상태 변경
            game_main()
        return True
    return False

def game_main():
    global mouse_c, index, image_id, image_ids, cnt
    cnt = 0

    # 인트로 화면 처리
    if index == 'intro_page':
        if mouse_c == 1:  # 마우스 클릭 시
            # 게임 설명 버튼 클릭
            if 300 < mouse_x < 550 and 580 < mouse_y < 690:
                img = tk.PhotoImage(file='bg_img/dc_page1.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                if image_id:  # 이전 이미지가 있으면 삭제
                    canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)  # 새로운 이미지 생성
                index = 'dc_page1'  # 페이지 상태 업데이트
            # 참여하기 버튼 클릭
            if 730 < mouse_x < 980 and 580 < mouse_y < 690:
                img = tk.PhotoImage(file='bg_img/info_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                if image_id:  # 이전 이미지가 있으면 삭제
                    canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)  # 새로운 이미지 생성
                index = 'info_page'  # 페이지 상태 업데이트
            mouse_c = 0  # 클릭 상태 초기화


    # 게임 설명 페이지 1 처리
    if index == 'dc_page1':
        if mouse_c == 1:
            # 다음 버튼 클릭
            if 1080 < mouse_x < 1180 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/dc_page2.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'dc_page2'  # 페이지 상태 업데이트
            # 이전 버튼 클릭
            if 100 < mouse_x < 200 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/intro_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'intro_page'  # 인트로 페이지로 이동
            mouse_c = 0  # 클릭 상태 초기화

    # 게임 설명 페이지 2 처리
    if index == 'dc_page2':
        if mouse_c == 1:
            # 다음 버튼 클릭
            if 1080 < mouse_x < 1180 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/dc_page3.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'dc_page3'  # 페이지 상태 업데이트
            # 이전 버튼 클릭
            if 100 < mouse_x < 200 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/dc_page1.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'dc_page1'  # 이전 페이지로 이동
            mouse_c = 0  # 클릭 상태 초기화

    # 게임 설명 페이지 3 처리
    if index == 'dc_page3':
        if mouse_c == 1:
            # 다음 버튼 클릭
            if 1080 < mouse_x < 1180 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/dc_page4.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'dc_page4'  # 페이지 상태 업데이트
            # 이전 버튼 클릭
            if 100 < mouse_x < 200 and 150 < mouse_y < 250:
                img = tk.PhotoImage(file='bg_img/dc_page2.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'dc_page2'  # 이전 페이지로 이동
            mouse_c = 0  # 클릭 상태 초기화

    # 게임 설명 페이지 4 처리
    if index == 'dc_page4':
        if mouse_c == 1:
            # 처음으로 버튼 클릭
            if 540 < mouse_x < 740 and 600 < mouse_y < 700:
                img = tk.PhotoImage(file='bg_img/intro_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 새 이미지 생성
                index = 'intro_page'  # 인트로 페이지로 이동
            mouse_c = 0  # 클릭 상태 초기화

    # 조 입력 페이지 처리
    if index == 'info_page':
        if mouse_c == 1:
            img = tk.PhotoImage(file='icon_img/info.png')
            img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장

            # 추가하기 버튼 클릭 (여러 이미지 추가)
            if 1120 < mouse_x < 1200 and 110 < mouse_y < 155:
                image_id1 = canvas.create_image(635, 205, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            if 1120 < mouse_x < 1200 and 185 < mouse_y < 230:
                image_id1 = canvas.create_image(635, 280, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            if 1120 < mouse_x < 1200 and 260 < mouse_y < 305:
                image_id1 = canvas.create_image(635, 355, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            if 1120 < mouse_x < 1200 and 335 < mouse_y < 380:
                image_id1 = canvas.create_image(635, 430, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            if 1120 < mouse_x < 1200 and 410 < mouse_y < 455:
                image_id1 = canvas.create_image(635, 505, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            if 1120 < mouse_x < 1200 and 485 < mouse_y < 530:
                image_id1 = canvas.create_image(635, 580, image=img)
                image_ids.append(image_id1)  # 추가된 이미지 ID 저장
            mouse_c = 0
            # 게임 시작 버튼 클릭
            if 1050 < mouse_x < 1210 and 620 < mouse_y < 700:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 이전 메인 이미지 삭제
                for img_id in image_ids:
                    canvas.delete(img_id)  # info_page에서 추가된 모든 이미지 삭제
                image_ids = []  # 이미지 ID 리스트 초기화
                image_id = canvas.create_image(640, 360, image=img)  # 새 메인 이미지 추가
                index = 'main_page'  # 메인 페이지로 이동
            mouse_c = 0  # 클릭 상태 초기화

    # 조뽑기 종료 페이지 처리(아직 조 별 재생버튼 처리는 안함)
    if index == 'end_page1':
        if mouse_c == 1:
            # 다시하기 버튼 클릭
            if 30 < mouse_x < 330 and 400 < mouse_y < 550:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 현재 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 메인 페이지로 돌아감
                index = 'main_page'  # 메인 페이지로 상태 변경
            mouse_c = 0  # 클릭 상태 초기화

            # 여러 재생 버튼 클릭 처리 (같은 기능 반복)
            if 800 < mouse_x < 840 and 175 < mouse_y < 205:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 240 < mouse_y < 270:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 305 < mouse_y < 335:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 370 < mouse_y < 400:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 435 < mouse_y < 465:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 500 < mouse_y < 530:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 800 < mouse_x < 840 and 565 < mouse_y < 595:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            # 종료 버튼 클릭
            if 30 < mouse_x < 330 and 550 < mouse_y < 700:
                img = tk.PhotoImage(file='bg_img/intro_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 현재 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 인트로 페이지로 이동
                index = 'intro_page'  # 인트로 페이지로 상태 변경
            mouse_c = 0

    # 조뽑기 종료 페이지 2 처리 (아직 조별 다시하기 버튼 처리는 안함)
    if index == 'end_page2':
        if mouse_c == 1:
            # 종료 버튼 클릭
            if 30 < mouse_x < 330 and 550 < mouse_y < 700:
                img = tk.PhotoImage(file='bg_img/intro_page.png')
                img_objects.append(img)  # 이미지 참조를 유지하기 위해 리스트에 저장
                canvas.delete(image_id)  # 현재 이미지 삭제
                image_id = canvas.create_image(640, 360, image=img)  # 인트로 페이지로 이동
                index = 'intro_page'  # 인트로 페이지로 상태 변경
            mouse_c = 0
            # 여러 다시하기 버튼 클릭 처리 (같은 기능 반복)
            if 770 < mouse_x < 840 and 175 < mouse_y < 205:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 240 < mouse_y < 270:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 305 < mouse_y < 335:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 370 < mouse_y < 400:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 435 < mouse_y < 465:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 500 < mouse_y < 530:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0
            if 770 < mouse_x < 840 and 565 < mouse_y < 595:
                img = tk.PhotoImage(file='bg_img/main_page.png')
                img_objects.append(img)
                canvas.delete(image_id)
                image_id = canvas.create_image(640, 360, image=img)
                index = 'main_page'
            mouse_c = 0

    if index != 'main_page':
        # 반복적으로 game_main 호출하여 게임 진행
        root.after(100, game_main)  # 100ms 후에 다시 호출
    elif index == 'main_page':
        # 게임 시작 함수 호출
        create_game_window()


# 게임을 시작하는 함수 호출
game_main()

# Tkinter 메인 루프 실행
root.mainloop()
