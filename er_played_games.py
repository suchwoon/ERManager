from playwright.sync_api import sync_playwright

# 사용자 입력 처리
nickname_input = input("닉네임을 입력하세요 (여러 개일 경우 쉼표로 구분): ")
subject_input = input("실험체를 입력하세요: ")

# 시즌 입력 검증
while True:
    try:
        end_season = int(input("현재 시즌 번호를 입력하세요: ")) + 9
        if end_season < 10:
            print("1 이상의 숫자를 입력해주세요.")
            continue
        break
    except ValueError:
        print("유효한 숫자를 입력해주세요.")

# 조회할 시즌 목록 생성
# 정출 이후만 검색하고 싶을 경우 range(10, end_season + 1)
seasons = [f"SEASON_{s}" for s in range(1, end_season + 1)] + ["NORMAL"]
nicknames = [name.strip() for name in nickname_input.split(",")]
total_games = 0

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    
    for idx, nickname in enumerate(nicknames, 1):
        page = browser.new_page()
        total_per_nick = 0  # 개별 닉네임 총합
        season_count = len(seasons)
        
        print(f"\n[{idx}/{len(nicknames)}] {nickname} 처리 시작 (총 {season_count - 1}개 시즌 검색)")
        
        for season_idx, season in enumerate(seasons, 1):
            # season_label 계산
            if season == "NORMAL":
                season_label = season
            else:
                season_num = int(season.split('_')[1])
                raw_label = season_num - 9
                if raw_label <= 0:
                    season_label = f"EA{season_num}"
                else:
                    season_label = f"S{raw_label}"
                    
            try:
                url = f"https://dak.gg/er/players/{nickname}?season={season}"
                page.goto(url, timeout=50000)
                page.wait_for_selector("table", timeout=20000)
                
                # 실험체 행 동적 검색
                row_xpath = f"//div[@class='character-name' and text()='{subject_input}']/ancestor::tr"
                row = page.locator(row_xpath)
                
                if not row.count():
                    print(f"  ⚠️ [{season_idx}/{season_count}] {season_label}: 기록 없음")
                    continue
                     
                # 플레이 횟수 추출
                plays_text = row.locator(".plays").first.inner_text()
                games = int(plays_text.split()[0])
                total_per_nick += games
                print(f"  ✅ [{season_idx}/{season_count}] {season_label}: {games} 게임")
                
            except Exception as e:
                print(f"  ❌ [{season_idx}/{season_count}] {season_label} 처리 실패: {str(e)[:100]}")
        
        # 현재 닉네임 총합 누적
        total_games += total_per_nick
        print(f"\n▶ {nickname} 총 플레이 횟수: {total_per_nick} 게임")
        page.close()

    browser.close()

# 최종 결과 출력
print("\n" + "=" * 50)
print(f"▶ 총 {subject_input} 플레이 횟수: {total_games} 게임")
print("=" * 50)