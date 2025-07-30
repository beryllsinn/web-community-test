from playwright.sync_api import sync_playwright
from getpass import getpass
import re, time

BASE_URL = "https://weverse.io/"
SLOW = 120

def click_candidates(page, selectors, timeout=8000):
    for sel in selectors:
        try:
            page.locator(sel).first.click(timeout=timeout)
            return True
        except:
            continue
    return False

def fill_candidates(page, selectors, value, timeout=8000):
    for sel in selectors:
        try:
            page.locator(sel).first.fill(value, timeout=timeout)
            return True
        except:
            continue
    return False

def get_wid(page, context):
    # 1) 쿠키에서 찾기
    for c in context.cookies():
        if "wid" in c.get("name", "").lower():
            return c.get("value")

    # 2) localStorage / sessionStorage 스캔
    def scan(js):
        items = page.evaluate(js)
        for k, v in items:
            if "wid" in (k or "").lower():
                return v
            m = re.search(r'"?wid"?\s*:\s*"([^"]+)"', v or "", re.I)
            if m:
                return m.group(1)
        return ""

    wid = scan("""
        const out = [];
        for (let i=0; i<localStorage.length; i++){
            out.push([localStorage.key(i), localStorage.getItem(localStorage.key(i))]);
        }
        return out;
    """) or scan("""
        const out = [];
        for (let i=0; i<sessionStorage.length; i++){
            out.push([sessionStorage.key(i), sessionStorage.getItem(sessionStorage.key(i))]);
        }
        return out;
    """)
    if wid:
        return wid

    # 3) document.cookie 파싱
    cookies = page.evaluate("() => document.cookie") or ""
    match = re.search(r"wid=([^;]+)", cookies, re.I)
    return match.group(1) if match else ""

def main():
    email = input("로그인 이메일: ").strip()
    pw = getpass("로그인 비밀번호: ").strip()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=SLOW)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(12000)

        page.goto(BASE_URL)

        # 로그인 버튼 클릭
        if not click_candidates(page, [
            "role=button[name=/^Sign in$/i]",
            "role=link[name=/^Sign in$/i]",
            "text=/로그인/i",
            "text=/Sign in/i"
        ]):
            print("로그인 버튼을 찾지 못했습니다. 직접 눌러 주세요.")
            page.pause()

        # 이메일/비밀번호 입력
        fill_candidates(page, ["input[type='email']"], email)
        fill_candidates(page, ["input[type='password']"], pw)

        # 제출
        click_candidates(page, [
            "button:has-text('로그인')",
            "button:has-text('Sign in')",
            "button[type='submit']"
        ])

        time.sleep(2)
        page.goto(BASE_URL)

        wid = get_wid(page, context)
        print("\n=== 로그인 + WID 추출 결과 ===")
        print(f"ID: {email}")
        print(f"WID: {wid if wid else 'WID를 찾지 못했습니다.'}")
        print("=============================\n")

        page.pause()

if __name__ == "__main__":
    main()
