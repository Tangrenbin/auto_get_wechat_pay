import cv2
import pyautogui
import pyscreeze
import numpy as np
import time

def capture_screenshot(filename, region=(0, 0, 1920, 1080)):
    # 截取屏幕截图并保存为灰度图像
    screenshot = pyscreeze.screenshot(region=region)  # 截取指定区域的屏幕截图
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)  # 将截图转换为灰度图像
    cv2.imwrite(filename, screenshot)  # 保存截图为文件
    return screenshot

def load_image(filename):
    # 读取图片并将其转换为灰度图像
    return cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

def click_button(target_image, screenshot_image, threshold=0.9):
    # 在屏幕截图中查找目标图像
    res = cv2.matchTemplate(screenshot_image, target_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= threshold:
        # 找到目标，计算中心点坐标并点击
        twidth, theight = target_image.shape[::-1]
        top_left = max_loc
        tagCenterX = top_left[0] + twidth // 2
        tagCenterY = top_left[1] + theight // 2
        pyautogui.click(tagCenterX, tagCenterY, button='left')  # 点击目标图像的中心点
    else:
        print("未找到目标")

def find_all_matches_with_color_depth(target_image, screenshot_image, threshold=0.9):
    # 在屏幕截图中查找目标图像，并计算颜色深度
    res = cv2.matchTemplate(screenshot_image, target_image, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    matches = []
    for pt in zip(*loc[::-1]):
        x, y = pt
        twidth, theight = target_image.shape[::-1]
        tagCenterX = x + twidth // 2
        tagCenterY = y + theight // 2
        color_depth = np.mean(screenshot_image[y:y+theight, x:x+twidth])  # 计算平均颜色深度
        matches.append((tagCenterX, tagCenterY, color_depth))

    return matches, len(matches)

def click_button_and_capture(target_image_filename, screenshot_filename, screen_scale=1, threshold=0.9):
    # 事先读取按钮截图
    target_image = load_image(target_image_filename)

    # 先截取屏幕截图并保存为灰度图像
    screenshot_image = capture_screenshot(screenshot_filename)

    # 缩放截图
    screenshot_image = cv2.resize(screenshot_image, (int(screenshot_image.shape[1] / screen_scale), int(screenshot_image.shape[0] / screen_scale)))

    if target_image_filename == "pay_button.png":
        # 如果目标图像是 "pay_button.png"，则获取颜色深度并过滤按钮
        matches, num_matches = find_all_matches_with_color_depth(target_image, screenshot_image, threshold)
        
        found_button = False  # 用于标记是否找到了合适的按钮

        if num_matches > 0:
            # 遍历匹配的按钮
            for match in matches:
                x, y, color_depth = match
                if color_depth < 188:
                    # 找到颜色深度小于188的按钮并点击
                    button_center_x = x 
                    button_center_y = y 
                    print(f"找到颜色深度{color_depth}的按钮，原始坐标：({x}, {y})，实际点击坐标：({button_center_x}, {button_center_y})")
                    pyautogui.click(button_center_x, button_center_y, button='left')
                    found_button = True  # 找到按钮后标记为 True

        if not found_button:
            print(f"未找到合适的按钮")
            return False
    else:
        # 目标图像不是 "pay_button.png"，按照原方式执行点击操作
        click_button(target_image, screenshot_image, threshold)
    return True

def simulate_mouse_scroll(amount, direction='vertical'):
    """
    模拟鼠标滚轮滚动。

    参数：
    - amount: 滚动的步数，正数表示向上滚动，负数表示向下滚动。
    - direction: 滚动方向，可以是 'vertical'（垂直滚动）或 'horizontal'（水平滚动）。

    示例：
    - simulate_mouse_scroll(3)  # 向上滚动3步
    - simulate_mouse_scroll(-2)  # 向下滚动2步
    - simulate_mouse_scroll(5, 'horizontal')  # 向右滚动5步（水平滚动）
    """
    if direction == 'vertical':
        pyautogui.scroll(amount)
    elif direction == 'horizontal':
        pyautogui.hscroll(amount)
    else:
        raise ValueError("无效的滚动方向。请使用 'vertical' 或 'horizontal'。")

def main():
    screen_scale = 1

    while True:
        result = click_button_and_capture("pay_button.png", "pay_screenshot.png", screen_scale)
        if result:
            print("点击转账界面")
            time.sleep(0.8)
        else:
            print("下移屏幕")
            simulate_mouse_scroll(-2)
            continue 
            

        result = click_button_and_capture("get_pay_button.png", "get_pay_screenshot.png", screen_scale)
        if result:
            print("点击收款按钮")
            time.sleep(1.5)

            result = click_button_and_capture("return_button.png", "return_screenshot.png", screen_scale)
            if result:
                print("点击返回按钮")
                time.sleep(0.2)
                simulate_mouse_scroll(-1)
                continue

if __name__ == "__main__":
    main()
