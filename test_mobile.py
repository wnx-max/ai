"""移动端响应式测试 - 独立脚本"""
from playwright.sync_api import sync_playwright
import os

HTML_PATH = r"c:\Users\a1812\Desktop\web\index.html"
URL = "file:///" + HTML_PATH.replace("\\", "/")
SCREENSHOT_DIR = r"c:\Users\a1812\Desktop\web\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

errors = []

def log(msg):
    print(f"[MOBILE TEST] {msg}")

def assert_true(cond, msg):
    if cond:
        log(f"PASS: {msg}")
    else:
        log(f"FAIL: {msg}")
        errors.append(msg)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # iPhone 12 Pro 尺寸
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    )
    page = context.new_page()

    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"{msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: console_msgs.append(f"pageerror: {err}"))

    log("===== 1. 移动端首页 =====")
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_true(page.locator("#start-screen.active").is_visible(), "移动端首页可见")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_mobile_start.png"), full_page=True)

    # 验证统计数字正确
    assert_true(page.locator("#stat-single").text_content() == "210", "单选题数量=210")
    assert_true(page.locator("#stat-judge").text_content() == "90", "判断题数量=90")
    assert_true(page.locator("#stat-total").text_content() == "300", "总题数=300")

    log("===== 2. 移动端开始答题 =====")
    page.locator(".filter-btn[data-type='single']").click()
    page.locator("#start-btn").click()
    page.wait_for_timeout(300)
    assert_true(page.locator("#quiz-screen.active").is_visible(), "移动端答题页可见")
    assert_true(page.locator("#quiz-counter").text_content() == "1 / 210", "计数器=1/210")

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_mobile_quiz.png"), full_page=True)

    log("===== 3. 移动端选项点击 =====")
    page.locator(".option-item[data-letter='A']").click()
    page.wait_for_timeout(200)
    assert_true(page.locator(".option-item.selected").count() == 1, "选项可点击选中")

    log("===== 4. 移动端导航 =====")
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    assert_true(page.locator("#quiz-counter").text_content() == "2 / 210", "下一题计数器=2/210")
    page.locator("#prev-btn").click()
    page.wait_for_timeout(200)
    assert_true(page.locator("#quiz-counter").text_content() == "1 / 210", "返回第1题")

    log("===== 5. 移动端交卷 =====")
    # 注册一次 dialog 处理
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#submit-top-btn").click()
    page.wait_for_timeout(500)
    assert_true(page.locator("#result-screen.active").is_visible(), "移动端结果页可见")

    score = page.locator("#score-text").text_content()
    total = page.locator("#score-total").text_content()
    log(f"移动端得分: {score} / {total}")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "11_mobile_result.png"), full_page=True)

    log("===== 6. 移动端解析 =====")
    page.locator("#review-btn").click()
    page.wait_for_timeout(500)
    assert_true(page.locator(".review-item").count() == 210, "解析条目=210")
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "12_mobile_review.png"), full_page=True)

    browser.close()

print("\n" + "=" * 50)
if errors:
    print(f"移动端测试失败 {len(errors)} 项:")
    for e in errors:
        print(f"  - FAIL: {e}")
else:
    print("移动端所有测试通过！")
print("=" * 50)

if console_msgs:
    print("\nConsole 消息:")
    for m in console_msgs:
        print(f"  {m}")
