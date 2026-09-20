"""验证含特殊字符（英文撇号、上标²、感叹号等）的题目选项在答题页与解析页能正常显示"""
from playwright.sync_api import sync_playwright
import os
import sys

# Windows GBK 控制台兼容（题目含 R² 等字符）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HTML_PATH = r"c:\Users\a1812\Desktop\web\index.html"
URL = "file:///" + HTML_PATH.replace("\\", "/")
SCREENSHOT_DIR = r"c:\Users\a1812\Desktop\web\screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

errors = []

def log(msg):
    print(f"[FIX TEST] {msg}")

def assert_true(cond, msg):
    if cond:
        log(f"PASS: {msg}")
    else:
        log(f"FAIL: {msg}")
        errors.append(msg)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()

    page.on("pageerror", lambda err: print(f"[JS ERROR] {err}"))

    page.goto(URL)
    page.wait_for_load_state("networkidle")

    # 选单选题开始
    page.locator(".filter-btn[data-type='single']").click()
    page.locator("#start-btn").click()
    page.wait_for_timeout(300)

    log("===== 验证第 114 题答题页选项显示（含 Amdahl's Law 撇号） =====")
    # 跳到第 114 题（单选题，0-indexed 为 113）
    page.evaluate("state.currentIndex = 113; state.userAnswers = state.pool.map(()=>null);")
    page.evaluate("renderQuestion();")
    page.wait_for_timeout(200)

    counter = page.locator("#quiz-counter").text_content()
    assert_true("114" in counter, f"跳到第114题 (实际={counter})")

    q_text = page.locator("#question-text").text_content()
    assert_true("阿姆达尔定律" in q_text, f"第114题题干含阿姆达尔定律 (实际={q_text[:30]})")

    # 验证 4 个选项都有文字内容
    options = page.locator(".option-item .option-text")
    assert_true(options.count() == 4, f"4个选项 (实际={options.count()})")

    all_have_text = True
    for i in range(options.count()):
        txt = options.nth(i).text_content()
        if not txt or len(txt.strip()) == 0:
            all_have_text = False
            log(f"  选项 {i+1} 文字为空！")
        else:
            log(f"  选项 {i+1}: {txt[:50]}{'...' if len(txt)>50 else ''}")
    assert_true(all_have_text, "第114题所有选项都有文字内容")

    # 验证题干含撇号选项不破坏渲染
    assert_true("Amdahl" in q_text, "题干中含 Amdahl's Law（撇号正常显示）")

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "13_q114_options.png"), full_page=True)

    log("===== 验证第 140 题选项显示（含 R² 上标字符） =====")
    page.evaluate("state.currentIndex = 139; renderQuestion();")
    page.wait_for_timeout(200)

    q140_text = page.locator("#question-text").text_content()
    assert_true("离群值" in q140_text, f"第140题题干正确 (实际={q140_text[:30]})")

    q140_opts = page.locator(".option-item .option-text")
    q140_texts = [q140_opts.nth(i).text_content() for i in range(q140_opts.count())]
    has_r2 = any("R²" in t for t in q140_texts)
    assert_true(has_r2, f"第140题选项含 R² 上标字符 (实际={q140_texts})")

    log("===== 验证交卷后解析页选项显示 =====")
    # 回到第114题选答案 D
    page.evaluate("state.currentIndex = 113; renderQuestion();")
    page.wait_for_timeout(200)
    page.locator(".option-item[data-letter='D']").click()
    page.wait_for_timeout(200)

    # 交卷
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("#submit-top-btn").click()
    page.wait_for_timeout(500)

    assert_true(page.locator("#result-screen.active").is_visible(), "结果页可见")

    # 查看解析
    page.locator("#review-btn").click()
    page.wait_for_timeout(500)

    review_items = page.locator(".review-item")
    assert_true(review_items.count() == 210, f"解析条目=210 (实际={review_items.count()})")

    # 第114题是第114个解析项
    q114_review = review_items.nth(113)  # 0-indexed
    q114_num = q114_review.locator(".review-num").text_content()
    assert_true("114" in q114_num, f"第114个解析项是第114题 (实际={q114_num})")

    # 验证第114题解析项的选项都有文字
    q114_opts = q114_review.locator(".review-option .review-option-text")
    assert_true(q114_opts.count() == 4, f"第114题解析4个选项 (实际={q114_opts.count()})")

    review_all_have_text = True
    for i in range(q114_opts.count()):
        txt = q114_opts.nth(i).text_content()
        if not txt or len(txt.strip()) == 0:
            review_all_have_text = False
            log(f"  解析第114题选项 {i+1} 文字为空！")
        else:
            log(f"  解析第114题选项 {i+1}: {txt[:50]}{'...' if len(txt)>50 else ''}")
    assert_true(review_all_have_text, "第114题解析页所有选项都有文字内容")

    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "14_q114_review.png"), full_page=True)

    browser.close()

print("\n" + "=" * 50)
if errors:
    print(f"修复验证失败 {len(errors)} 项:")
    for e in errors:
        print(f"  - FAIL: {e}")
else:
    print("验证通过！含特殊字符的选项在答题页和解析页均正常显示。")
print("=" * 50)
