from playwright.sync_api import sync_playwright
from getpass import getpass

BASE_URL = "https://weverse.io/"

def click_first(page, selectors):
    for sel in selectors:
        try:
            page.locator(sel).first.click(timeout=8000)
            return True
        except:
            continue
    return False

def fill_first(page, selectors, value):
    for sel in selectors:
        try:
            page.locator(sel).first.fill(value, timeout=8000)
            return True
        except:
            continue
    return False

def main():
    email = input("회원가입 이메일: ").strip()
    password = getpass("설정할 비밀번호: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        # 홈 진입
        page.goto(BASE_URL)

        # 회원가입 또는 로그인 버튼 클릭
        if not click_first(page, ["text=회원가입", "text=Sign up", "text=로그인", "text=Log in"]):
            print("회원가입 버튼을 직접 눌러주세요.")
            page.pause()

        # 이메일/비밀번호 입력
        fill_first(page, ["input[type='email']"], email)
        fill_first(page, ["input[type='password']"], password)

        # 제출 버튼 클릭
        click_first(page, [
            "button[type='submit']",
            "button:has-text('회원가입')",
            "button:has-text('Sign up')",
            "button:has-text('Continue')",
            "button:has-text('Next')"
        ])

        print("\n[안내] 이메일로 전송된 인증 메일을 확인하고 인증을 완료하세요.\n")
        print("인증 완료 후 login_and_wid.py로 로그인 + WID 추출을 진행합니다.")
        page.pause()

if __name__ == "__main__":
    main()
