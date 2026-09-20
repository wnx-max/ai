"""测试 Web 前端刷题应用 - 静态 HTML 文件，直接用 file:// URL"""
from playwright.sync_api import sync_playwright
import os
import sys

HTML_PATH = r"c:\Users\a1812\Desktop\web\index.html"
URL = "file:///" + HTML_PATH.replace("\\", "/")
SCREENSHOT_DIR = r"c:\Users\a1812\Desktop\web\screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

errors = []


def log(msg):
    print(f"[TEST] {msg}")


def shot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    log(f"截图保存: {path}")


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

    # 收集 console 错误
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(f"{msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: console_msgs.append(f"pageerror: {err}"))

    log("===== 1. 打开首页 =====")
    page.goto(URL)
    page.wait_for_load_state("networkidle")

    # 验证开始页显示
    assert_true(page.locator("#start-screen.active").is_visible(), "开始页可见")
    assert_true(page.locator(".app-title").is_visible(), "标题可见")

    # 验证题目数量统计
    single_count = page.locator("#stat-single").text_content()
    judge_count = page.locator("#stat-judge").text_content()
    total_count = page.locator("#stat-total").text_content()
    assert_true(single_count == "210", f"单选题数量=210 (实际={single_count})")
    assert_true(judge_count == "90", f"判断题数量=90 (实际={judge_count})")
    assert_true(total_count == "300", f"总题数=300 (实际={total_count})")

    # 验证筛选按钮
    filter_btns = page.locator(".filter-btn").all()
    assert_true(len(filter_btns) == 3, f"3个筛选按钮 (实际={len(filter_btns)})")
    shot(page, "01_start_screen")

    log("===== 2. 选择单选题库并开始 =====")
    page.locator(".filter-btn[data-type='single']").click()
    page.locator("#start-btn").click()
    page.wait_for_timeout(300)

    assert_true(page.locator("#quiz-screen.active").is_visible(), "答题页可见")

    # 验证第一题
    q_text = page.locator("#question-text").text_content()
    assert_true("相关性分析" in q_text, f"第1题内容正确 (实际={q_text[:30]})")

    counter = page.locator("#quiz-counter").text_content()
    assert_true(counter == "1 / 210", f"计数器=1/210 (实际={counter})")

    type_label = page.locator("#quiz-type-label").text_content()
    assert_true(type_label == "单选题", f"题型标签=单选题 (实际={type_label})")

    # 验证选项数量
    options = page.locator(".option-item")
    assert_true(options.count() == 4, f"4个选项 (实际={options.count()})")

    # 验证上一题按钮禁用
    assert_true(page.locator("#prev-btn").is_disabled(), "第一题时上一题按钮禁用")
    shot(page, "02_quiz_first_question")

    log("===== 3. 作答第1题 (选D) =====")
    page.locator(".option-item[data-letter='D']").click()
    page.wait_for_timeout(200)
    selected = page.locator(".option-item.selected").count()
    assert_true(selected == 1, f"选中1个选项 (实际={selected})")
    assert_true(page.locator(".option-item[data-letter='D']").evaluate("el => el.classList.contains('selected')"), "D选项已选中")

    log("===== 4. 切换到下一题 =====")
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    counter = page.locator("#quiz-counter").text_content()
    assert_true(counter == "2 / 210", f"计数器=2/210 (实际={counter})")
    # 验证第1题答案被保留（回到第1题检查）
    page.locator("#prev-btn").click()
    page.wait_for_timeout(200)
    selected = page.locator(".option-item.selected").count()
    assert_true(selected == 1, f"返回第1题答案保留 (选中={selected})")
    # 再回到第2题
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)

    log("===== 5. 返回开始页 =====")
    page.locator("#back-btn").click()
    page.wait_for_timeout(300)
    # 确认返回对话框
    page.on("dialog", lambda dialog: dialog.accept())
    page.locator("#back-btn").click()
    page.wait_for_timeout(300)
    assert_true(page.locator("#start-screen.active").is_visible(), "返回开始页")

    log("===== 6. 测试判断题 - 切换到判断题库 =====")
    page.locator(".filter-btn[data-type='judge']").click()
    page.locator("#start-btn").click()
    page.wait_for_timeout(300)

    type_label = page.locator("#quiz-type-label").text_content()
    assert_true(type_label == "判断题", f"判断题标签 (实际={type_label})")

    counter = page.locator("#quiz-counter").text_content()
    assert_true(counter == "1 / 90", f"判断题计数器=1/90 (实际={counter})")

    options = page.locator(".option-item")
    assert_true(options.count() == 2, f"判断题2个选项 (实际={options.count()})")
    shot(page, "04_judge_question")

    # 判断题第1题答案为B(×)
    page.locator(".option-item[data-letter='B']").click()
    page.wait_for_timeout(200)
    selected = page.locator(".option-item.selected").count()
    assert_true(selected == 1, f"判断题选中1个 (实际={selected})")

    log("===== 7. 完整答题并交卷（判断题，前5题作答）=====")
    # 第1题已答B
    # 进入第2题答A
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    page.locator(".option-item[data-letter='A']").click()
    page.wait_for_timeout(200)

    # 第3题答A
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    page.locator(".option-item[data-letter='A']").click()
    page.wait_for_timeout(200)

    # 第4题答B
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    page.locator(".option-item[data-letter='B']").click()
    page.wait_for_timeout(200)

    # 第5题答A
    page.locator("#next-btn").click()
    page.wait_for_timeout(200)
    page.locator(".option-item[data-letter='A']").click()
    page.wait_for_timeout(200)
    shot(page, "05_judge_q5_answered")

    log("===== 8. 测试交卷（带未答题确认）=====")
    # 跳到最后一题
    page.locator("#next-btn").click()  # 第6题
    page.wait_for_timeout(100)
    # 直接点交卷按钮
    dialogs_handled = []
    def handle_dialog(dialog):
        dialogs_handled.append(dialog.message)
        dialog.accept()
    page.on("dialog", handle_dialog)
    page.locator("#submit-top-btn").click()
    page.wait_for_timeout(500)

    assert_true(len(dialogs_handled) >= 1, f"出现交卷确认对话框 (共{len(dialogs_handled)}个)")
    if dialogs_handled:
        assert_true("未作答" in dialogs_handled[0], f"对话框提示未作答 (实际={dialogs_handled[0][:30]})")

    log("===== 9. 验证结果页 =====")
    assert_true(page.locator("#result-screen.active").is_visible(), "结果页可见")
    score = page.locator("#score-text").text_content()
    total = page.locator("#score-total").text_content()
    log(f"得分: {score} / {total}")
    assert_true(total == "90", f"总分=90 (实际={total})")
    shot(page, "06_result_page")

    log("===== 10. 查看解析 =====")
    page.locator("#review-btn").click()
    page.wait_for_timeout(500)
    review_items = page.locator(".review-item").count()
    assert_true(review_items == 90, f"解析条目=90 (实际={review_items})")
    # 验证有正确和错误标记
    correct_items = page.locator(".review-item.correct").count()
    wrong_items = page.locator(".review-item.wrong").count()
    skipped_items = page.locator(".review-item.skipped").count()
    log(f"正确:{correct_items} 错误:{wrong_items} 未答:{skipped_items}")
    assert_true(correct_items + wrong_items + skipped_items == 90, "解析分类完整")
    shot(page, "07_review_list")

    log("===== 11. 再来一次 =====")
    page.locator("#restart-btn").click()
    page.wait_for_timeout(300)
    assert_true(page.locator("#start-screen.active").is_visible(), "返回开始页")

    log("===== 12. 测试全部题库 =====")
    page.locator(".filter-btn[data-type='all']").click()
    page.locator("#start-btn").click()
    page.wait_for_timeout(300)
    counter = page.locator("#quiz-counter").text_content()
    assert_true(counter == "1 / 300", f"全部题目计数器=1/300 (实际={counter})")
    shot(page, "08_all_questions")

    log("===== 13. PC端进度条验证 =====")
    progress_width = page.locator("#progress-bar").evaluate("el => el.style.width")
    assert_true(progress_width.endswith("%") and float(progress_width[:-1]) > 0, f"进度条有宽度 (实际={progress_width})")

    browser.close()

    # 注：移动端响应式测试由独立的 test_mobile.py 覆盖

# 报告
print("\n" + "=" * 60)
if errors:
    print(f"测试完成，发现 {len(errors)} 个失败：")
    for e in errors:
        print(f"  - FAIL: {e}")
else:
    print("所有测试通过！")
print("=" * 60)

# 报告 console 错误
if console_msgs:
    print("\nConsole 消息:")
    for m in console_msgs:
        print(f"  {m}")

sys.exit(1 if errors else 0)
