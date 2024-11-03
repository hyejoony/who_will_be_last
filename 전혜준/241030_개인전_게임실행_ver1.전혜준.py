import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def show_ranking_and_team_buttons(canvas, team_info, player_rankings):
    global back_button 
    # 캔버스 초기화
    canvas.delete("all")

    # 랭킹창 이미지 로드 및 표시
    ranking_img = Image.open("../img/background_pages/end_page1.png")  # 실제 이미지 경로로 변경해주세요
    ranking_photo = ImageTk.PhotoImage(ranking_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=ranking_photo)
    canvas.image = ranking_photo  # 참조 유지


    # 시작 버튼 삭제 (랭킹 화면에서는 필요 없음)
    if 'start_button' in globals() and start_button:
        start_button.destroy()


    # 뒤로 가기 버튼 삭제 (랭킹 화면에서는 필요 없음)
    if 'back_button' in globals() and back_button:
        back_button.destroy()

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
        return lambda event: start_team_game(team)

    for i, (x1, y1) in enumerate(click_areas):
        if i < len(team_info):
            team = team_info[player_rankings[i] - 1]  # player_ranking에 따라 팀 선택
            x2 = x1 + 100  # 클릭 영역의 너비 설정
            y2 = y1 + 50   # 클릭 영역의 높이 설정
            
            canvas.create_rectangle(x1, y1, x2, y2, fill='', outline='', tags=f"clickable_{team['team_number']}")
            canvas.tag_bind(f"clickable_{team['team_number']}", '<Button-1>', create_click_handler(team))

    # 팀 정보 텍스트 표시 
    team_positions = [
        (460, 190),  # 첫 번째 팀의 좌표
        # 나머지 6팀의 좌표를 여기에 입력하세요
        (460, 252),
        (460, 320),
        (460, 385),
        (460, 450),
        (460, 513),
        (460, 580)
    ]
    for i, rank in enumerate(player_rankings):
        if i < len(team_positions):
            team = next(team for team in team_info if team['team_number'] == rank)
            x_position, y_position = team_positions[i]
            
            team_text = f"{team['team_number']}조 {team['team_member'][:30]}"  # 멤버 이름 길이 제한

            canvas.create_text(x_position, y_position, anchor=tk.W, text=team_text, 
                               
                               
                               fill="black", font=("Arial", 14))

def move_player(canvas, player, items):
    global player_names
    # 플레이어 이동 로직 구현
    # 예: 랜덤 이동
    import random
    move_x = random.randint(1, 5)
    canvas.move(player, move_x, 0)
    
    # 플레이어 이름도 함께 이동
    player_index = players.index(player)
    canvas.move(player_names[player_index], move_x, 0)
    
    # 게임이 끝나지 않았다면 계속 이동
    if canvas.coords(player)[0] < 1100:  # 예: 1100px에 도달하면 게임 종료
        canvas.after(100, lambda: move_player(canvas, player, items))


def start_race(canvas, players, items, start_button):
    global player_names
    """게임 시작: 플레이어가 이동을 시작"""
    print(f"Starting race with {len(players)} players")
    start_button.config(state='disabled')
    for player in players:
        canvas.after(100, lambda p=player: move_player(canvas, p, items))

def start_team_game(team):
    global canvas, players, items, start_button,back_button
    
    # 팀 멤버 정보 가져오기
    team_members = team['team_member'].split()
    
    # 캔버스 초기화
    canvas.delete("all")
    
    # team_info를 팀 멤버로 업데이트
    new_team_info = [{'team_member': member, 'team_number': i+1} for i, member in enumerate(team_members)]
    
    # 기존 창에서 게임 재생성
    players, items = create_game_window(canvas, new_team_info)
    
    # 시작 버튼 재생성
    if 'start_button' in globals() and start_button:
        start_button.destroy()
    start_button = ttk.Button(root, text="Start", 
                              command=lambda: start_race(canvas, players, items, start_button))
    start_button.place(x=1100, y=600)

    # 뒤로 가기 버튼 생성
    back_button = ttk.Button(root, text="뒤로 가기", command=lambda: show_ranking_and_team_buttons(canvas, team_info, player_rankings))
    back_button.place(x=20, y=20)

def create_game_window(canvas, team_info):
    global players, player_names
    players = []
    player_names = []  # 플레이어 이름을 저장할 리스트
    
    # 아이템 생성 로직 (실제 구현 필요)
    items = []  # 임시로 빈 리스트 반환

    player_images = [
        tk.PhotoImage(file=f'../img/players/player{i}.png') for i in range(len(team_info))
    ]
    root.images = player_images  # 이미지 참조 유지

    num_players = len(team_info)
    canvas_height = 720
    total_spacing = 600
    
    if num_players > 1:
        spacing = total_spacing / (num_players - 1)
    else:
        spacing = 0
    
    start_y = (canvas_height - total_spacing) / 2

    for i, team in enumerate(team_info):
        y_position = start_y + i * spacing
        player = canvas.create_image(24, y_position, image=player_images[i], tags=f"player_{team['team_number']}")
        players.append(player)
        
        # 플레이어 이름 추가
        name = team['team_member'].split()[0]  # 첫 번째 이름만 사용
        name_text = canvas.create_text(24, y_position + 30, text=name, fill="black", font=("Arial", 10), tags=f"name_{team['team_number']}")
        player_names.append(name_text)

    return players, items

# 임의의 team_info 데이터
team_info = [
    {'team_member': '최현정 정유진 김동환 전동환 전혜준', 'team_number': 1},
    {'team_member': '고양이 다람쥐 박민재', 'team_number': 2},
    {'team_member': '이지은 박지성 손흥민 김연아 류현진', 'team_number': 3},
    {'team_member': '강호동 유재석 이수근 김종국 하하', 'team_number': 4},
    {'team_member': '김태희 송중기 이민호', 'team_number': 5},  # 새로운 팀 5
    {'team_member': '이효리 비욘세 제이슨', 'team_number': 6},   # 새로운 팀 6
    {'team_member': '마이클 조던 르브론 제임스 코비', 'team_number': 7}  # 새로운 팀 7
]

# 임의의 player_rankings 데이터
player_rankings = [2, 4, 1, 3, 5, 6, 7]  # 팀 번호 순서대로 순위 표시  # 팀 번호 순서대로 순위 표시

# 메인 창 생성
root = tk.Tk()
root.title("팀 게임전")
root.geometry("1280x720")

# 캔버스 생성
canvas = tk.Canvas(root, width=1280, height=720)
canvas.pack()


# 랭킹 및 팀 버튼 표시
show_ranking_and_team_buttons(canvas, team_info, player_rankings)

root.mainloop()