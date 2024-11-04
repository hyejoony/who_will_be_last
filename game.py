# %% [markdown]
# 
# ## 1. 필요한 모듈 임포트
# - GUI 생성 및 관리를 위한 tkinter 관련 모듈 임포트
# - 게임 로직에 필요한 random 모듈 임포트
# - 이미지 처리를 위한 PIL 모듈 임포트

# %%
import tkinter as tk  # 기본 GUI 생성 및 관리
from tkinter import ttk  # 향상된 tkinter 위젯
import random  # 무작위 요소 생성 (아이템 배치, 플레이어 이동 등)
import copy # 값 복사
from PIL import Image, ImageTk
import pygame  # 사운드 재생을 위한 pygame 추가
#%%
# 사운드 관련 초기화
# pygame 초기화
pygame.mixer.init()

# 배경음악 및 효과음 로드
try:
    pygame.mixer.music.load('./bgm/victory.mp3')  # 배경음악 로드
    finish_sound = pygame.mixer.Sound('./bgm/effect_pocket1.mp3')  # 효과음 로드
except pygame.error as e:
    print(f"사운드 파일 로드 에러: {e}")

# 사운드 관련 전역 변수 추가
sound_played = {}  # 각 플레이어별 효과음 재생 여부 추가
# %% [markdown]
# ## 2. 전역 변수 설정
# - 게임 상태, 플레이어 정보, UI 요소를 관리하기 위한 전역 변수 초기화
# - 마우스 입력, 팀 정보, 게임 모드 등 다양한 게임 요소 관리
# 

# %%
# 마우스 및 게임 진행 관련 변수
mouse_x, mouse_y, mouse_c = 0, 0, 0  # 마우스 x좌표, y좌표, 클릭 상태
cnt = 0  # 완주한 플레이어 수

# 플레이어 관련 변수
player_speeds = {}  # 각 플레이어의 속도
player_stopped = {}  # 각 플레이어의 정지 상태
players = []  # 현재 게임의 플레이어 리스트
order = [] # 현재 게임의 팀 순위
player_rankings = []    # 실시간 랭킹 표시
player_names = [] #플레이어 이름표 표시

# 게임 모드 및 이전 게임 정보
individualGame = False  # 개인전 모드 여부
players_pre = []  # 이전 게임의 플레이어 정보
order_pre = []  # 이전 게임의 순위
team_info_pre = []  # 이전 게임의 팀 정보

# UI 및 게임 상태 관련 변수
index = 'start_page'  # 현재 페이지 상태
image_id = None  # 현재 표시 중인 이미지 ID
img_objects, image_ids = [], []  # 이미지 객체 및 ID 리스트

# 팀 정보 입력 관련 변수
team_info = []  # 현재 게임의 팀 정보
input_texts = ["" for _ in range(7)]  # 팀 입력 텍스트
max_teams = 7  # 최대 팀 수
input_positions = [100]  # 입력 필드 위치
text_ids = [None for _ in range(7)]  # 텍스트 ID 리스트
cursor_id = None  # 커서 ID
edit_button_ids = [None for _ in range(7)]  # 편집 버튼 ID 리스트
edit_mode = [False for _ in range(7)]  # 편집 모드 상태
input_spacing = 75  # 입력 필드 간 간격
active_input = None  # 현재 활성화된 입력 필드

# 이미지 및 UI 요소
input_image_files = [f"./img/icons/input{i}.png" for i in range(2, 8)]  # 입력 필드 이미지 파일
start_button = None  # 시작 버튼 객체
popup_image = None  # 팝업 이미지 객체

# 기타 게임 상태 변수
team_members = None  # 현재 선택된 팀 멤버
flag = False  # 게임 상태 플래그
ran = False  # 랜덤 이벤트 발생 여부
gold = False    # 황금버섯 만남
poison = False  # 독버섯 만남

# %% [markdown]
# ## 3. 마우스 이벤트 처리 함수
# - 마우스 움직임과 클릭을 감지하고 전역 변수를 업데이트
# - 게임 내 사용자 상호작용의 기본이 되는 함수들

# %%
def mouse_move(e):
    """마우스 움직임 이벤트 처리"""
    global mouse_x, mouse_y
    mouse_x, mouse_y = e.x, e.y  # 마우스 현재 위치를 전역 변수에 저장

def mouse_press(e):
    """마우스 클릭 이벤트 처리"""
    global mouse_c
    mouse_c = 1  # 마우스 클릭 상태를 1(클릭됨)로 설정

# %% [markdown]
# ## 4. 윈도우 및 캔버스 설정
# - Tkinter 윈도우 생성 및 기본 설정
# - 게임 화면을 위한 캔버스 설정
# - 초기 페이지 배경 이미지 로드 및 표시

# %%
# 윈도우 및 캔버스 설정
root = tk.Tk()
root.title('노부부와 보호인')
root.resizable(False, False)
root.bind("<Motion>", mouse_move)  # 마우스 움직임 이벤트
root.bind("<ButtonPress>", mouse_press)  # 마우스 클릭 이벤트
root.geometry('1280x720')

canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()

# 초기 페이지 배경 설정
img = tk.PhotoImage(file='./img/background_pages/start_page.png')
canvas.create_image(640, 360, image=img)


# %% [markdown]
# ## 5. 팀 정보 입력 관련 함수
# - 사용자의 키보드 입력을 처리하여 팀 정보를 입력받는 기능
# - 백스페이스, 스페이스, 일반 문자 입력 처리
# - 입력된 텍스트 표시 및 커서 위치 업데이트

# %%
def handle_input(event):
    global active_input
    if active_input is not None:
        if event.keysym == 'BackSpace':
            # 백스페이스 키 입력 시 마지막 문자 삭제
            input_texts[active_input] = input_texts[active_input][:-1]
        elif event.keysym == 'space':
            # 스페이스 키 입력 시 공백 추가
            input_texts[active_input] += ' '
        elif len(event.char) == 1:
            # 일반 문자 입력 시 해당 문자 추가
            input_texts[active_input] += event.char
        
        # 입력된 텍스트 표시 업데이트
        update_text_display(active_input)
        # 커서 위치 업데이트
        update_cursor_position(active_input)

# %% [markdown]
# ## 6. 텍스트 디스플레이 업데이트 함수
# - 입력된 팀 정보 텍스트를 캔버스에 표시하는 기능
# - 기존 텍스트를 삭제하고 새로운 텍스트를 생성하여 업데이트

# %%
def update_text_display(index):
    if text_ids[index]:
        # 기존에 표시된 텍스트가 있다면 삭제
        canvas.delete(text_ids[index])
    
    # 새로운 텍스트 위치 계산
    y_position = input_positions[index]
    
    # 캔버스에 새로운 텍스트 생성 및 표시
    text_ids[index] = canvas.create_text(
        180,  # x 좌표
        y_position + 25,  # y 좌표 (입력 필드 위치에서 25픽셀 아래)
        text=input_texts[index],  # 표시할 텍스트
        anchor='w',  # 왼쪽 정렬
        font=('Arial', 12)  # 폰트 설정
    )

# %% [markdown]
# # 커서 위치 업데이트 함수
# - 입력 필드의 커서 위치를 업데이트하고, 커서를 깜빡이게 하는 기능
# - 텍스트의 길이에 따라 커서의 x 좌표를 조정

# %%
def update_cursor_position(index):
    global cursor_id
    if cursor_id:
        # 기존 커서가 있다면 삭제
        canvas.delete(cursor_id)
    
    # 입력 필드의 y 좌표 계산
    y_position = input_positions[index]
    
    # 현재 텍스트의 너비 계산
    text_width = canvas.bbox(text_ids[index])[2] - canvas.bbox(text_ids[index])[0] if text_ids[index] else 0
    
    # 새로운 커서 생성
    cursor_id = canvas.create_line(
        180 + text_width,  # 커서 x 좌표 (텍스트 너비에 따라 조정)
        y_position + 10,   # 커서 시작 y 좌표
        180 + text_width,  # 커서 끝 x 좌표 (수직선)
        y_position + 40,   # 커서 끝 y 좌표
        fill='black'       # 커서 색상
    )
    
    # 깜빡이는 커서 함수 호출
    blink_cursor()

# %% [markdown]
# # 커서 깜빡임 함수
# - 입력 필드의 커서를 주기적으로 깜빡이게 하는 기능
# - 커서의 상태를 'normal'과 'hidden'으로 전환하여 시각적 효과 제공

# %%
def blink_cursor():
    global cursor_id
    if cursor_id:
        # 현재 커서의 상태를 가져옴
        current_state = canvas.itemcget(cursor_id, 'state')
        # 상태를 반전시켜 커서를 보이거나 숨김
        new_state = 'hidden' if current_state == 'normal' else 'normal'
        canvas.itemconfigure(cursor_id, state=new_state)  # 커서 상태 업데이트
    
    # 현재 활성화된 입력 필드가 있다면, 600ms 후에 다시 호출
    if active_input is not None:
        canvas.after(600, blink_cursor)

# %% [markdown]
# # 입력 활성화 함수
# - 특정 입력 필드를 활성화하고 커서를 해당 위치로 이동
# - 입력 필드에 포커스를 설정하여 사용자의 입력을 받을 준비를 함

# %%
def activate_input(index):
    global active_input
    active_input = index  # 활성화된 입력 필드 인덱스 설정
    canvas.focus_set()  # 캔버스에 포커스 설정 (키보드 입력 가능)
    update_cursor_position(index)  # 커서 위치 업데이트

# %% [markdown]
# # 입력 필드 추가 함수
# - 최대 팀 수에 도달하지 않은 경우 새로운 입력 필드를 추가
# - 입력 필드의 위치를 계산하고, 해당 위치에 이미지를 표시
# - 텍스트 입력을 위한 초기화 및 업데이트 수행

# %%
def add_input_field():
    if len(input_positions) < max_teams:
        new_index = len(input_positions)  # 새 입력 필드의 인덱스
        y_position = input_positions[0] + new_index * input_spacing  # 새로운 y 좌표 계산
        input_positions.append(y_position)  # 입력 필드 위치 리스트에 추가
        
        try:
            if new_index > 0:
                # 이전 입력 필드의 이미지 로드 및 생성
                img_entry = tk.PhotoImage(file=input_image_files[new_index - 1])
                img_objects.append(img_entry)  # 이미지 객체 리스트에 추가
                image_id = canvas.create_image(635, y_position + 25, image=img_entry)  # 이미지 생성
                image_ids.append(image_id)  # 이미지 ID 리스트에 추가
            
            input_texts[new_index] = ""  # 새로운 입력 텍스트 초기화
            update_text_display(new_index)  # 텍스트 디스플레이 업데이트
        except tk.TclError as e:
            print(f"이미지 로딩 오류: {e}")  # 이미지 로딩 오류 처리

# %% [markdown]
# # 편집 버튼 표시 함수
# - 주어진 인덱스에 해당하는 편집 버튼을 캔버스에 표시
# - 버튼의 위치를 계산하기 위해 `get_button_position` 함수를 호출
# 
# # 버튼 위치 계산 함수
# - 인덱스에 따라 버튼의 x, y 좌표를 반환
# - 첫 번째 버튼은 고정된 위치에, 이후 버튼은 입력 필드 위치에 따라 조정

# %%
def display_edit_button(index):
    try:
        # 편집 버튼 이미지 로드 및 생성
        edit_img = tk.PhotoImage(file='./img/icons/edit_button.png')
        img_objects.append(edit_img)  # 이미지 객체 리스트에 추가
        button_x, button_y = get_button_position(index)  # 버튼 위치 계산
        edit_button_ids[index] = canvas.create_image(button_x, button_y, image=edit_img)  # 버튼 생성
    except tk.TclError as e:
        print(f"이미지 로딩 오류: {e}")  # 이미지 로딩 오류 처리

def get_button_position(index):
    if index == 0:
        return 1070, 130  # 첫 번째 버튼의 고정 위치
    else:
        y_position = input_positions[index]  # 입력 필드의 y 좌표
        return 1070, y_position + 25  # 이후 버튼의 위치 조정

# %% [markdown]
# # 팀 입력 페이지 처리 함수
# - 마우스 클릭 이벤트에 따라 입력 필드를 활성화하거나 버튼 클릭을 처리
# - 입력 필드 또는 편집 버튼의 영역 내에서 클릭이 발생했는지 확인

# %%
def handle_team_input_page(event):
    global active_input, cursor_id

    if cursor_id:
        # 기존 커서를 삭제
        canvas.delete(cursor_id)
        cursor_id = None

    # 입력 필드 클릭 처리
    for i, y_position in enumerate(input_positions):
        if 160 < event.x < 1000 and y_position < event.y < y_position + 50:
            activate_input(i)  # 입력 필드 활성화
            return
    
    # 추가 버튼 및 편집 버튼 클릭 처리
    for i, y_position in enumerate(input_positions):
        if 1150 < event.x < 1250 and y_position < event.y < y_position + 50:
            if i >= len(team_info):
                handle_add_button(i)  # 새 팀 추가 처리
            else:
                handle_edit_button(i)  # 팀 편집 처리
            return

    # 편집 버튼 클릭 처리
    for i in range(len(team_info)):
        button_x, button_y = get_button_position(i)
        if button_x - 40 < event.x < button_x + 40 and button_y - 20 < event.y < button_y + 20:
            handle_edit_button(i)  # 팀 편집 처리
            return

    active_input = None  # 활성화된 입력 필드 없음

# %% [markdown]
# # 팀 추가 버튼 처리 함수
# - 입력된 팀 정보를 기반으로 새로운 팀을 추가
# - 최대 팀 수에 도달하지 않은 경우 새로운 입력 필드를 추가
# - 추가된 팀 정보를 화면에 표시
# 
# # 팀 편집 버튼 처리 함수
# - 입력된 내용을 바탕으로 기존 팀 정보를 수정

# %%
def handle_add_button(index):
    if input_texts[index]:  # 입력 필드가 비어있지 않은 경우
        team_number = len(team_info) + 1  # 새 팀 번호 계산
        team_member = input_texts[index]  # 입력된 팀 멤버 정보
        team_info.append({'team_number': team_number, 'team_member': team_member})  # 팀 정보 추가
        
        if len(input_positions) < max_teams:  # 최대 팀 수 미달 시
            add_input_field()  # 새로운 입력 필드 추가
        
        display_edit_button(index)  # 편집 버튼 표시

def handle_edit_button(index):
    if input_texts[index]:  # 입력 필드가 비어있지 않은 경우
        team_info[index]['team_member'] = input_texts[index]  # 기존 팀 멤버 정보 수정

# %% [markdown]
# # 팀 입력 초기화 함수
# - 팀 정보를 초기화하고 모든 입력 필드를 비워줌
# - 입력 필드와 관련된 변수들을 기본 상태로 재설정

# %%
def reset_team_input():
    global team_info, input_texts, input_positions, text_ids, edit_button_ids, active_input
    team_info = []  # 팀 정보 초기화
    input_texts = ["" for _ in range(7)]  # 입력 텍스트 초기화
    input_positions = [100]  # 입력 필드 위치 초기화
    text_ids = [None for _ in range(7)]  # 텍스트 ID 초기화
    edit_button_ids = [None for _ in range(7)]  # 편집 버튼 ID 초기화
    active_input = None  # 활성화된 입력 필드 초기화

# %% [markdown]
# # 팀 입력 페이지 설정 함수
# - 팀 정보를 초기화하고 입력 필드 및 버튼 관련 변수를 설정
# - 기본 입력 필드를 추가하여 사용자 입력을 받을 준비를 함

# %%
def setup_team_input_page():
    global team_info, input_texts, input_positions, text_ids, edit_button_ids
    team_info = []  # 팀 정보 초기화
    input_texts = ["" for _ in range(7)]  # 입력 텍스트 초기화
    input_positions = [100]  # 입력 필드 위치 초기화
    text_ids = [None for _ in range(7)]  # 텍스트 ID 초기화
    edit_button_ids = [None for _ in range(7)]  # 편집 버튼 ID 초기화
    add_input_field()  # 기본 입력 필드 추가

# %% [markdown]
# # 아이템 생성 함수
# - 주어진 아이템 정보를 바탕으로 캔버스에 아이템을 생성
# - 아이템 간의 겹침을 방지하기 위한 내부 함수를 포함
# 
# ## 겹침 방지 함수
# - 기존 아이템과 새로운 아이템의 위치를 비교하여 겹침 여부를 판단

# %%
def create_items(canvas, item_info, images):
    """아이템을 화면에 생성하는 함수"""
    items = []

    def is_overlapping(x, y, item_size):
        """아이템 간 겹침 방지"""
        for item, _ in items:
            existing_x, existing_y = canvas.coords(item)
            min_dist_x, min_dist_y = item_size[0] + 100, item_size[1] + 100
            if (existing_x - min_dist_x < x < existing_x + min_dist_x and
                existing_y - min_dist_y < y < existing_y + min_dist_y):
                return True
        return False

    for item_type, info in item_info.items():
        item_photo = tk.PhotoImage(file=info['path'])
        images.append(item_photo)  # 이미지 리스트에 추가
        item_size = (item_photo.width() // 2, item_photo.height() // 2)  # 아이템 크기 계산

        for _ in range(info["count"]):
            while True:
                x, y = random.randint(100, 928), random.randint(50, 670)  # 랜덤 위치 생성
                if not is_overlapping(x, y, item_size):  # 겹치지 않으면 루프 종료
                    break

            item = canvas.create_image(x, y, image=item_photo)  # 아이템 생성
            if item:
                items.append((item, item_type))  # 생성된 아이템 추가
            else:
                print(f"{item_type} 생성 실패")  # 생성 실패 메시지
    
    return items  # 생성된 아이템 리스트 반환

# %% [markdown]
# # 게임 윈도우 생성 함수
# - 플레이어 및 아이템 정보를 초기화하고 게임 화면을 설정
# - 아이템을 생성하고 플레이어 이미지를 로드하여 캔버스에 배치
# - 시작 버튼을 생성하여 게임 시작 기능을 연결

# %%
def create_game_window():
    global players, start_button, player_speeds, player_stopped, order, team_members, player_names, sound_played

    # 게임 시작 시 변수들 초기화
    player_speeds, player_stopped, players, order, player_names = {}, {}, [], [], []
    sound_played = {}  # 효과음 재생 여부 초기화
    
    # 아이템 정보 설정
    item_info = {
        "chestnut": {"path": "./img/items/chestnut.png", "count": 3},
        "cobweb": {"path": "./img/items/cobweb.png", "count": 3},
        "poison_mushroom": {"path": "./img/items/poison_mushroom.png", "count": 3},
        "balloon": {"path": "./img/items/balloon.png", "count": 3},
        "gold_mushroom": {"path": "./img/items/gold_mushroom.png", "count": 3},
        "hole": {"path": "./img/items/hole.png", "count": 3},
        "random_box": {"path": "./img/items/random_box.png", "count": 3},
    }

    root.images = []  # 이미지 참조를 유지하여 삭제 방지
    items = create_items(canvas, item_info, root.images)  # 아이템 생성
    player_images = [
        tk.PhotoImage(file=f'./img/players/player{i}.png') for i in range(len(team_info))
    ]
    root.images.extend(player_images)  # 플레이어 이미지 추가

    num_players = len(team_info)  # 플레이어 수 확인
    # print('넘 플레이어스 - ', num_players)
    canvas_height = 720  # 캔버스의 높이
    total_spacing = 600  # 플레이어들이 차지할 전체 세로 공간
    
    if num_players > 1:
        spacing = total_spacing / (num_players - 1)  # 플레이어 간 간격 계산
    else:
        spacing = 0  # 플레이어가 1명일 경우 간격은 의미 없음
    
    start_y = (canvas_height - total_spacing) / 2  # 시작 y 좌표 (중앙 정렬)

    #플레이어마다 이름띄울 영역
    click_areas = [
        (1080, 544),  
        (1150, 544),  
        (1215, 544),  
        (1070, 595),  
        (1124, 595),  
        (1179, 595),  
        (1234, 595)  
    ]

    player_name_lst = [0] * len(team_info) #배정된 캐릭터 정보 담기


    #팀전, 개인전 분리
    if not individualGame: #팀전일 경우(캐릭터 생성, 이름표 부여)
        for i, team in enumerate(team_info):
            y_position = start_y + i * spacing
            player = canvas.create_image(24, y_position, image=player_images[i])  # 플레이어 이미지 생성
            players.append([player, team['team_number'], team['team_member']])  # 플레이어 정보 추가

            player_name_lst[i] = 1  #배정된 캐릭터 이미지 정보 업데이트
                
            # 플레이어 이름표에 이름 추가
            name = str(team['team_number']) +'조' # 첫 번째 이름만 사용 
            name_text = canvas.create_text(24, y_position + 30, text=name, fill="black", font=("Arial", 12), tags=f"name_{team['team_number']}")
            player_names.append(name_text)
        
        # 배정받은 캐릭터 정보 화면에 띄우기
        for i,exist in enumerate(player_name_lst):
            if exist:
                x,y = click_areas[i][0], click_areas[i][1] 
                name = str(players[i][1]) + '조'
                canvas.create_text(x,y, text = name, fill="black", font=("Arial", 11))
        
    elif individualGame: #개인전일 경우
        # team_info는 new_team_info 변수로 재선언
        # 참가자 정보 업데이트 : {참가자 이름 : 참가 번호}
        for i, team in enumerate(team_info):
            y_position = start_y + i * spacing 
            player = canvas.create_image(24, y_position, image=player_images[i])
            players.append((player, team['team_number'], team['team_member']))
            player_name_lst[i] = 1  #배정된 캐릭터 이미지 정보 업데이트


            # 플레이어 이름표에 이름 추가
            name = team['team_member'] #참가자 이름 
            name_text = canvas.create_text(24, y_position + 30, text=name, fill="black", font=("Arial", 12), tags=f"name_{team['team_number']}")
            player_names.append(name_text)
                
                # 배정받은 캐릭터 정보 화면에 띄우기
        for i,exist in enumerate(player_name_lst):
            if exist:
                x,y = click_areas[i][0], click_areas[i][1] 
                name = players[i][2] + '님'
                canvas.create_text(x,y, text = name, fill="black", font=("Arial", 11))
            
    

    # 기존 버튼이 있다면 삭제
    if start_button is not None:
        start_button.destroy()

    # 이미지 로드 및 크기 조정
    image = Image.open("./img/icons/start.png")  # 이미지 파일 경로를 지정하세요
    image = image.resize((100, 50))  # 원하는 크기로 조정

    # Tkinter에서 사용할 수 있는 형식으로 변환
    photo = ImageTk.PhotoImage(image)

    # 버튼 생성
    start_button = tk.Button(
        root,
        image=photo,
        command=lambda: start_race(canvas, players, items, start_button),  # 게임 시작 함수 연결
        borderwidth=0,
        highlightthickness=0,
        bg='#9F9898'  # 메인 창의 배경색과 동일하게 설정
    )
    start_button.image = photo  # 참조 유지를 위해 필요
    start_button.place(x=1100, y=630)

     # 배경음악 재생 시작
    try:
        pygame.mixer.music.play(-1)  # -1은 무한 반복
    except pygame.error as e:
        print(f"배경음악 재생 에러: {e}")

    return players, items  # 플레이어와 아이템 리스트 반환

# %% [markdown]
# 

# %% [markdown]
# # 게임 시작 함수
# - 플레이어의 이동을 시작하고, 랭킹을 업데이트
# - 시작 버튼을 비활성화하여 중복 클릭 방지

# %%
def start_race(canvas, players, items, start_button):
    """게임 시작: 플레이어가 이동을 시작"""
    start_button.config(state='disabled')  # 시작 버튼 비활성화
    update_rankings(canvas, players)  # 랭킹 업데이트
    for player in players:
        canvas.after(100, lambda p=player: move_player(canvas, p, items))  # 각 플레이어 이동 시작

# %% [markdown]
# # 플레이어 이동 함수
# - 플레이어의 속도와 정지 상태를 관리하며, 플레이어를 캔버스에서 이동
# - 화면 경계를 넘어가지 않도록 조정하고, 아이템과의 충돌을 처리

# %%
def move_player(canvas, player, items):
    global gold, poison
    """플레이어가 움직이는 함수"""
    # player_speeds.setdefault(player[1], random.choice([4,6,8]))  # 기본 속도 설정
    player_stopped.setdefault(player[1], False)  # 기본 정지 상태 설정

    if not gold and not poison:
        player_speeds[player[1]] = random.choice([4,6,8])

    if player_stopped[player[1]]:  # 플레이어가 정지 상태일 때
        canvas.after(100, lambda: move_player(canvas, player, items))  # 재귀 호출로 이동 계속
        return

    dx, dy = player_speeds[player[1]], random.choice([-2, 0, 2]) * player_speeds[player[1]]  # 이동 거리 계산
    canvas.move(player[0], dx, dy)  # 플레이어 이동
    # 플레이어 이름도 함께 이동
    player_index = players.index(player)
    canvas.move(player_names[player_index], dx, dy)


    player_coords = canvas.coords(player[0])
    # 화면 밖으로 나가는 것 방지
    player_height = 50  # 플레이어 이미지의 대략적인 높이
    if player_coords[1] < 20:
        canvas.move(player[0], 0, 20 - player_coords[1])  # 위쪽 경계 조정
        player_index = players.index(player)
        canvas.move(player_names[player_index], 0, 20 - player_coords[1])

    elif player_coords[1] > 720 - player_height:
        canvas.move(player[0], 0, (720 - player_height) - player_coords[1])  # 아래쪽 경계 조정
        player_index = players.index(player)
        canvas.move(player_names[player_index], 0, (720 - player_height) - player_coords[1])


    # 아이템 충돌 처리
    for item, item_type in items[:]:
        if check_collision(player_coords, canvas.coords(item)):  # 충돌 체크
            handle_item_collision(canvas, player, item_type, item, items)  # 아이템 충돌 처리

    if not check_finish(canvas, player):  # 완주 체크
        canvas.after(100, lambda: move_player(canvas, player, items))  # 재귀 호출로 이동 계속

# %% [markdown]
# # 아이템 충돌 처리 함수
# - 플레이어가 아이템과 충돌했을 때의 행동을 정의
# - 각 아이템 타입에 따라 플레이어의 위치나 속도를 조정

# %%
def handle_item_collision(canvas, player, item_type, item, items):
    global player_speeds, gold, poison  # 기존 속도를 저장하고 복구하기 위해 필요

    """아이템과 충돌 시 아이템 별 행동 처리"""
    if item_type == "chestnut":
        canvas.move(player[0], -100, 0)  # 밤나무 아이템: 왼쪽으로 이동
        # 플레이어 이름도 함께 이동
        player_index = players.index(player)
        canvas.move(player_names[player_index], -100, 0)
        
    
    elif item_type == "cobweb":
        player_stopped[player[1]] = True  # 거미줄 아이템: 플레이어 정지
        canvas.after(3000, lambda: resume_player(player))  # 3초 후 복구
    
    elif item_type == "balloon":
        canvas.move(player[0], 100, 0)  # 풍선 아이템: 오른쪽으로 이동
        # 플레이어 이름도 함께 이동
        player_index = players.index(player)
        canvas.move(player_names[player_index], 100, 0)

    elif item_type == "gold_mushroom":
        gold = True
        original_speed = player_speeds[player[1]]  # 현재 속도 저장
        player_speeds[player[1]] = 10  # 속도 증가
        canvas.after(2000, lambda: restore_speed(player, original_speed))  # 2초 후 원래 속도로 복구
    
    elif item_type == "hole":
        new_coords = -canvas.coords(player[0])[0] 
        canvas.move(player[0], -canvas.coords(player[0])[0] + 24, 0)  # 구멍 아이템: 왼쪽으로 이동
        # 플레이어 이름도 함께 이동
        player_index = players.index(player)
        canvas.move(player_names[player_index], new_coords + 24, 0)

    
    elif item_type == "poison_mushroom":
        poison = True
        original_speed = player_speeds[player[1]]  # 현재 속도 저장
        player_speeds[player[1]] = 2  # 속도 감소
        canvas.after(2000, lambda: restore_speed(player, original_speed))  # 2초 후 원래 속도로 복구
    
    elif item_type == "random_box":
        random_action(canvas)  # 랜덤 박스: 랜덤 행동 수행

    canvas.delete(item)  # 아이템 삭제
    items.remove((item, item_type))  # 아이템 리스트에서 제거

# %% [markdown]
# # 속도 복구 함수
# - 플레이어의 속도를 원래 상태로 되돌리는 기능

# %%
def restore_speed(player, original_speed):
    """플레이어의 속도를 원래대로 복구하는 함수"""
    global  gold, poison
    gold = poison = False
    player_speeds[player[1]] = original_speed  # 원래 속도로 복구

# %% [markdown]
# # 플레이어 재개 함수
# - 정지된 플레이어를 다시 이동 가능하게 설정
# - 플레이어의 정지 상태를 해제하여 이동을 재개

# %%
def resume_player(player):
    """정지된 플레이어 다시 이동 가능하게 설정"""
    global ran
    if not ran:  # 특정 조건에 따라 재개
        player_stopped[player[1]] = False  # 플레이어의 정지 상태 해제

# %% [markdown]
# # 랜덤 행동 처리 함수
# - 게임 중 랜덤한 행동을 수행하여 플레이어의 상태를 변경
# - 팝업 이미지를 표시하고, 2초 후에 해당 행동을 실행

# %%
def random_action(canvas):
    """랜덤 행동 처리"""
    global popup_image, ran
    action = random.choice(["all_to_start", "shuffle_players"])  # 랜덤하게 행동 선택

    # 게임 일시 정지
    global player_stopped, players
    ran = True
    for player in players:
        player_stopped[player[1]] = True  # 모든 플레이어 정지

    # 팝업 이미지 표시
    popup_image = tk.PhotoImage(file=f'./img/icons/{action}.png')  # 팝업 이미지 경로
    popup = canvas.create_image(500, 360, image=popup_image)  # 화면 중앙에 표시
    canvas.tag_raise("popup")  # 팝업을 최상위 레이어로 올림

    def remove_popup_and_resume():
        global players, ran
        ran = False  # 랜덤 행동 완료 상태 설정
        canvas.delete(popup)  # 팝업 제거

        if action == "all_to_start":
            for player in players:
                if canvas.coords(player[0])[0] < 1008:  # 도착선(1008) 이전의 플레이어만 시작 위치로 이동
                    canvas.coords(player[0], 24, canvas.coords(player[0])[1])
                    player_index = players.index(player)
                    canvas.coords(player_names[player_index], 24, canvas.coords(player[0])[1] + 30) #캐릭터 이름표도 이동

        elif action == "shuffle_players":
            active_players = []
            active_positions = []
            
            for player in players:
                if canvas.coords(player[0])[0] < 1008:  # 도착선(1008) 이전의 플레이어만 추출
                    active_players.append(player)
                    active_positions.append(canvas.coords(player[0]))
            
            if active_positions:
                random.shuffle(active_positions)  # 위치 섞기
                
                for i, player in enumerate(active_players):
                    new_position =  active_positions[i]
                    canvas.coords(player[0], *new_position)  # 새로운 위치로 이동
                    player_index = players.index(player)
                    canvas.coords(player_names[player_index], new_position[0], new_position[1] + 30) # 이름표도 따라가게 구현

        # 게임 재개
        for player in players:
            player_stopped[player[1]] = False  # 플레이어 이동 가능 상태로 변경

    # 2초 후 팝업 제거 및 게임 재개
    canvas.after(2000, remove_popup_and_resume)

# %% [markdown]
# # 충돌 확인 함수
# - 플레이어와 아이템 간의 충돌 여부를 확인
# - 두 객체의 중심 좌표를 계산하고, 거리 기반으로 충돌을 판단

# %%
def check_collision(player_coords, item_coords):
    """플레이어와 아이템 간 충돌 여부 확인"""
    player_center_x, player_center_y = player_coords[0] + 25, player_coords[1] + 25  # 플레이어 중심 좌표
    item_center_x, item_center_y = item_coords[0] + 17.5, item_coords[1] + 17.5  # 아이템 중심 좌표
    distance = ((player_center_x - item_center_x) ** 2 + (player_center_y - item_center_y) ** 2) ** 0.5  # 거리 계산
    return distance <= (45 / 2) + (30 / 2)  # 충돌 여부 반환

# %% [markdown]
# # 완주 확인 함수
# - 플레이어가 완주선에 도달했는지 확인
# - 완주한 플레이어를 순서 리스트에 추가하여 기록

# %%
def check_finish(canvas, player):
    global order, individualGame, sound_played
    current_x = canvas.coords(player[0])[0]
    
    # 이미 완주한 상태면 True만 반환
    if not individualGame and player[1] in order:
        return True
    if individualGame and player[2] in order:
        return True
    
    # 완주선 도달 체크
    if current_x >= 1008:
        # 효과음 재생 (아직 재생되지 않은 플레이어인 경우)
        if player[1] not in sound_played:
            try:
                finish_sound.play()
                sound_played[player[1]] = True
            except pygame.error as e:
                print(f"효과음 재생 에러: {e}")
        
        # 순위에 추가
        if not individualGame:
            if player[1] not in order:
                order.append(player[1])
        else:
            if player[2] not in order:
                order.append(player[2])
                
        return True
    
    return False

# %% [markdown]
# # 이미지 로드 함수
# - 주어진 파일 경로에서 이미지를 로드하고, 이미지 객체를 리스트에 추가
# - 로드된 이미지를 반환하여 다른 곳에서 사용할 수 있도록 함

# %%
def load_image(file_path):
    """이미지 로드 함수"""
    img = tk.PhotoImage(file=file_path)  # 이미지 로드
    img_objects.append(img)  # 이미지 객체 리스트에 추가
    return img  # 로드된 이미지 반환

# %% [markdown]
# # 페이지 전환 함수
# - 새로운 페이지로 전환하고, 해당 페이지에 맞는 이미지를 로드하여 캔버스에 표시
# - 이전 이미지를 삭제하여 메모리 관리

# %%
def switch_page(new_page, image_path):
    """페이지 전환을 처리하는 함수"""
    global image_id
    canvas.delete("all")  # 캔버스의 모든 요소 삭제
    img = load_image(image_path)  # 새로운 이미지 로드
    if image_id:  # 이전 이미지가 존재할 경우 삭제
        canvas.delete(image_id)
    image_id = canvas.create_image(640, 360, image=img)  # 새로운 이미지 생성 및 중앙에 배치
    global index
    index = new_page  # 페이지 상태 업데이트

# %% [markdown]
# # 마우스 클릭 영역 확인 함수
# - 주어진 좌표 범위 내에서 마우스 클릭이 발생했는지 확인
# - 클릭이 발생한 경우 `True`, 그렇지 않으면 `False`를 반환

# %%
def handle_click(x1, y1, x2, y2):
    """마우스 클릭 영역을 확인하는 함수"""
    return x1 < mouse_x < x2 and y1 < mouse_y < y2  # 마우스 클릭 여부 반환

# %% [markdown]
# # 랭킹 업데이트 함수
# - 플레이어의 현재 위치를 기반으로 랭킹을 업데이트하고, 완주 여부를 확인
# - 완주한 플레이어와 아직 완주하지 않은 플레이어를 분리하여 정렬 후 표시

# %%
def update_rankings(canvas, players):
    """플레이어들의 현재 위치를 기반으로 랭킹 업데이트"""
    global player_rankings, cnt, order, individualGame 
    player_rankings = []  # 랭킹 리스트 초기화
    finished_count = 0  # 완주한 플레이어 수 초기화
    
    for player in players:
        coords = canvas.coords(player[0])  # 플레이어의 현재 좌표 가져오기
        if coords and len(coords) >= 2:  # x, y 좌표가 모두 있는지 확인
            finish_status = check_finish(canvas, player)  # 완주 여부 확인
            if finish_status:  # 완주 여부 확인
                finished_count += 1  # 완주한 플레이어 수 증가
            player_rankings.append((coords[0], player[1], player[2], finish_status))  # (x좌표, 팀 번호, 팀 멤버, 완주 여부) 튜플 추가
        else:
            print(f"Warning: Invalid coordinates for player {player}")  # 좌표가 유효하지 않은 경우 경고

    unfinisheds = [(pos, p, p2, fin) for pos, p, p2, fin in player_rankings if not fin]  # 완주하지 않은 플레이어 리스트 생성
    unfinisheds.sort(reverse=True)  # x좌표 기준으로 내림차순 정렬

    player_rankings = []  # 랭킹 리스트 초기화

    for p in order:  # 이미 완주한 플레이어 추가
        player_rankings.append(p)
    
    for unfinished in unfinisheds:  # 완주하지 않은 플레이어 추가
        if not individualGame:
            player_rankings.append(unfinished[1])  # 팀 번호 추가
        else:
            player_rankings.append(unfinished[2])  # 팀 멤버 추가

    canvas.delete("ranking")  # 이전 랭킹 텍스트 삭제
    y_offset = 130  # y 좌표 오프셋 초기화
    
    for rank, player_rank in enumerate(player_rankings, 1):  # 랭킹 텍스트 생성 및 표시
        if not individualGame:
            text = f"{rank}등: {player_rank} 조"  # 팀 게임일 경우
        else:
            text = f"{rank}등: {player_rank} 님"  # 개인 게임일 경우
        canvas.create_text(1180, y_offset, text=text, anchor='ne', font=('Arial', 12), tags="ranking")  # 텍스트 생성 및 캔버스에 추가
        y_offset += 25  # 다음 텍스트 위치 조정
    
    cnt = finished_count  # 완료된 플레이어 수 저장

    if cnt == len(players):  # 모든 플레이어가 완료했는지 확인
        handle_all_players_finished(canvas)  # 모든 플레이어 완료 처리 함수 호출
    else:
        canvas.after(100, lambda: update_rankings(canvas, players))  # 랭킹 업데이트 재귀 호출

# %% [markdown]
# # 모든 플레이어 완료 처리 함수
# - 모든 플레이어가 완주했을 때의 처리를 담당
# - 게임 상태를 초기화하고, 최종 순위를 출력
# - 개인 게임과 팀 게임에 따라 다른 페이지로 전환

# %%
def handle_all_players_finished(canvas):
    """모든 플레이어가 완주했을 때 처리하는 함수"""
    global index, image_id, players, items, start_button, order, team_info
    global players_pre, order_pre, team_info_pre  # 1라운드 정보 저장
    
    # 배경음악 정지
    try:
        pygame.mixer.music.stop()
    except pygame.error as e:
        print(f"배경음악 정지 에러: {e}")

    print('마지막 순위는 : ', order)

    if not individualGame:
        players_pre = copy.deepcopy(players)
        order_pre = order[:]
        team_info_pre = copy.deepcopy(team_info)
        switch_page('end_page1', './img/background_pages/end_page1.png')
    else:
        switch_page('end_page2', './img/background_pages/end_page2.png')

# %% [markdown]
# # 랭킹 및 팀 버튼 표시 함수
# - 최종 랭킹과 팀 정보를 화면에 표시하고, 클릭 가능한 영역을 생성하여 팀 게임 시작 기능을 연결
# - 각 팀의 정보를 텍스트로 표시하고, 클릭 이벤트를 설정

# %%
def show_ranking_and_team_buttons():
    global back_button, image_id, start_button, players, order, players_pre, order_pre, individualGame, team_members, index, flag
    
    flag = True  # 상태 플래그 설정

    # 시작 버튼 제거
    if start_button is not None:
        start_button.destroy()
        start_button = None

    # 팀 정보 텍스트 표시 
    team_positions = [
        (460, 190),  # 첫 번째 팀의 좌표
        (460, 252),  # 두 번째 팀의 좌표
        (460, 320),  # 세 번째 팀의 좌표
        (460, 385),  # 네 번째 팀의 좌표
        (460, 450),  # 다섯 번째 팀의 좌표
        (460, 513),  # 여섯 번째 팀의 좌표
        (460, 580)   # 일곱 번째 팀의 좌표
    ]

    for i, (x1, y1) in enumerate(team_positions):
        if i < len(players_pre):
            if individualGame and order_pre[i] == team_members[-1]:
                players_pre[order_pre[i] - 1][2] = ' '.join(order)  # 개인 게임일 경우 멤버 이름 업데이트

            team = players_pre[order_pre[i] - 1]
            team_text = f"{team[1]}조 {team[2][:30]}"  # 멤버 이름 길이 제한

            canvas.create_text(x1, y1, anchor=tk.W, text=team_text, fill="black", font=("Arial", 14))  # 팀 정보 텍스트 생성

    # 클릭 가능한 영역 생성 (7개의 좌표)
    click_areas = [
        (800, 175),  
        (800, 240),  
        (800, 305),  
        (800, 370),  
        (800, 435),  
        (800, 500),  
        (800, 565)  
    ]
        
    def create_click_handler(team):
        global individualGame
        individualGame = True  # 개인 게임 상태 설정
        return lambda event: start_team_game(team)  # 클릭 시 팀 게임 시작 함수 호출

    for i, (x1, y1) in enumerate(click_areas):
        if i < len(players_pre):
            team = players_pre[order_pre[i] - 1]  # player_ranking에 따라 팀 선택
            x2 = x1 + 100  # 클릭 영역의 너비 설정
            y2 = y1 + 50   # 클릭 영역의 높이 설정
            
            canvas.create_rectangle(x1, y1, x2, y2, fill='', outline='', tags=f"clickable_{team[1]}")  # 클릭 영역 생성
            canvas.tag_bind(f"clickable_{team[1]}", '<Button-1>', create_click_handler(team))  # 클릭 이벤트 바인딩

# %% [markdown]
# # 팀 게임 시작 함수
# - 선택된 팀의 멤버 정보를 가져와서 게임 페이지로 전환
# - 팀 정보를 업데이트하고, 게임 창을 재생성하여 팀 게임을 시작

# %%
def start_team_game(team):
    global team_info, team_members
    
        # 사운드 초기화
    try:
        pygame.mixer.music.stop()  # 이전 배경음악 정지
        pygame.mixer.music.play(-1)  # 새로운 게임의 배경음악 시작
    except pygame.error as e:
        print(f"배경음악 재시작 에러: {e}")

    # 팀 멤버 정보 가져오기
    team_members = team[2].split()  # 팀 멤버를 공백으로 분리하여 리스트로 저장
    team_members.append(team[1])  # 팀 번호 추가
    
    switch_page('game_page', './img/background_pages/game_page.png')  # 게임 페이지로 전환
    
    # team_info를 팀 멤버로 업데이트
    team_info = [{'team_member': member, 'team_number': i + 1} for i, member in enumerate(team_members) if type(member) == str]

    # 기존 창에서 게임 재생성
    create_game_window()  # 게임 창 생성 함수 호출

# %% [markdown]
# # 게임 메인 루프 함수
# - 게임의 각 페이지 상태에 따라 적절한 클릭 이벤트를 처리하고 페이지 전환을 관리
# - 마우스 클릭 이벤트와 키 입력을 통해 사용자 인터페이스를 제어

# %%
def game_main():
    global mouse_c, index, image_id, image_ids, cnt, individualGame, team_info, team_info_pre, flag 
    cnt = 0  # 초기화

    if index == 'start_page':
        if mouse_c == 1:
            if handle_click(300, 580, 550, 690):  # 설명 페이지로 이동
                switch_page('description_1', './img/background_pages/description_1.png')
            if handle_click(730, 580, 980, 690):  # 팀 입력 페이지로 이동
                switch_page('team_input', './img/background_pages/team_input.png')
                reset_team_input()  # 팀 입력 초기화
            mouse_c = 0

    elif index == 'description_1':
        if mouse_c == 1:
            if handle_click(1080, 150, 1180, 250):  # 다음 설명 페이지로 이동
                switch_page('description_2', './img/background_pages/description_2.png')
            elif handle_click(100, 150, 200, 250):  # 시작 페이지로 돌아가기
                switch_page('start_page', './img/background_pages/start_page.png')
            mouse_c = 0

    elif index == 'description_2':
        if mouse_c == 1:
            if handle_click(1080, 150, 1180, 250):  # 다음 설명 페이지로 이동
                switch_page('description_3', './img/background_pages/description_3.png')
            elif handle_click(100, 150, 200, 250):  # 이전 설명 페이지로 돌아가기
                switch_page('description_1', './img/background_pages/description_1.png')
            mouse_c = 0

    elif index == 'description_3':
        if mouse_c == 1:
            if handle_click(1080, 150, 1180, 250):  # 아이템 설명 페이지로 이동
                switch_page('description_item', './img/background_pages/description_item.png')
            elif handle_click(100, 150, 200, 250):  # 이전 설명 페이지로 돌아가기
                switch_page('description_2', './img/background_pages/description_2.png')
            mouse_c = 0

    elif index == 'description_item':
        if mouse_c == 1:
            if handle_click(540, 600, 740, 700):  # 시작 페이지로 돌아가기
                switch_page('start_page', './img/background_pages/start_page.png')
                mouse_c = 0

    elif index == 'team_input':
        canvas.bind("<Button-1>", handle_team_input_page)  # 팀 입력 핸들러 바인딩
        root.bind("<Key>", handle_input)  # 키 입력 핸들러 바인딩
        if mouse_c == 1:
            if handle_click(1050, 620, 1210, 700):  
                switch_page('game_page', './img/background_pages/game_page.png')  
                canvas.unbind("<Button-1>")  
                root.unbind("<Key>")  
                create_game_window()  
            mouse_c = 0

    elif index == 'end_page1':
        if not flag:  
            show_ranking_and_team_buttons()  
        else:  
            if mouse_c == 1:
                if handle_click(30, 400, 330, 550):  
                    individualGame = False  
                    flag = False  
                    team_info = team_info_pre  
                    switch_page('game_page', './img/background_pages/game_page.png')  
                    create_game_window()  
                elif handle_click(30,550,330,700):  
                    individualGame = False  
                    flag = False  
                    switch_page('start_page', './img/background_pages/start_page.png')  
                mouse_c = 0

    elif index == 'end_page2':
        if flag:  
            show_ranking_and_team_buttons()  
        if mouse_c == 1:
            if handle_click(30,550,330,700):  
                individualGame = False  
                flag = False  
                switch_page('start_page', './img/background_pages/start_page.png')  
            mouse_c = 0

    root.after(100, game_main)   # 게임 메인 루프 재호출


# 게임 종료 시 사운드 정리를 위한 함수 추가
def cleanup():
    pygame.mixer.quit()
    root.destroy()

# 메인 윈도우에 정리 함수 연결
root.protocol("WM_DELETE_WINDOW", cleanup)

# 게임 시작
game_main()

# Tkinter 메인 루프 실행
root.mainloop()


