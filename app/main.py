import math
import cv2
import numpy as np
from circleController import CircleController
from circle import Circle

core_size = 3
smooth_value = 0.5

delta_thres = 60

required_contour_area = 100
spawnrate = 60
hard_mode = True

hue_range = 30
saturation_range = 80
value_range = 80


def start():
    video = cv2.VideoCapture(0)
    w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cv2.namedWindow('Window', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Window', w, h)

    cv2.namedWindow('FirstFrame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('FirstFrame', w, h)

    '''
    cv2.namedWindow('Source', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Source', w, h)
    cv2.namedWindow('ControllerColor', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('ControllerColor', 200, 50)
    cv2.namedWindow('Moving', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Moving', w, h)
    cv2.namedWindow('ColorAndMoving', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('ColorAndMoving', w, h)
    cv2.namedWindow('Color', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Color', w, h)
    '''

    fps = int(video.get(cv2.CAP_PROP_FPS))
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # video_writer = cv2.VideoWriter(name, fourcc, 144, (w, h))

    ok, frame = video.read()

    if (ok):
        circle_controller = CircleController(spawnrate, w, h, hard_mode, 30, required_contour_area)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gauss_frame = cv2.GaussianBlur(gray_frame, (core_size, core_size), sigmaX=smooth_value, sigmaY=smooth_value)
        new_frame = gauss_frame

        cv2.imshow('FirstFrame', frame)
        controller_color = get_color_in_point(frame, gauss_frame)

        color_frame = frame.copy()
        for i in range(len(frame)):
            for j in range(len(frame[i])):
                color_frame[i][j] = controller_color
        color_frame = cv2.cvtColor(color_frame, cv2.COLOR_HSV2BGR)
        cv2.imshow('ControllerColor', color_frame)
        print(controller_color)

        while True:
            prev_frame = new_frame.copy()
            ok, frame = video.read()
            if not ok:
                break

            display_frame = frame.copy()
            color_mask = threshold_mask_to_color(frame, controller_color)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gauss_frame = cv2.GaussianBlur(gray_frame, (core_size, core_size), sigmaX=smooth_value, sigmaY=smooth_value)
            new_frame = gauss_frame
            diff_frame = cv2.absdiff(prev_frame, new_frame)
            thres_frame = cv2.threshold(diff_frame, delta_thres, 255, cv2.THRESH_BINARY)[1]
            color_thres = cv2.bitwise_and(thres_frame, color_mask)
            (contours, hierarchy) = cv2.findContours(color_thres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contr in contours:
                area = cv2.contourArea(contr)
                if (area > required_contour_area):
                    cv2.imshow('Moving', thres_frame)
                    cv2.imshow('Color', color_mask)
            circle_controller.check_frame(contours)

            cv2.imshow('ColorAndMoving', color_thres)

            for circle in circle_controller.circleList:
                cv2.circle(display_frame, (circle.centerX, circle.centerY), circle.radius, circle.color, thickness=-1)
            cv2.putText(display_frame, f"Score: {circle_controller.score}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)
            cv2.putText(display_frame, f"Lost: {circle_controller.lost}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)

            '''
            cv2.imshow('Source', frame)
            '''
            cv2.imshow('Window', display_frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
            circle_controller.start_next_iteration()

    video.release()
    cv2.destroyAllWindows()


def get_average_color_from_region(src_frame, gauss_frame):
    hsv_frame = cv2.cvtColor(src_frame, cv2.COLOR_BGR2HSV_FULL)
    color_box_region = cv2.selectROI('FirstFrame', src_frame)
    controller_hsv_color = [0, 0, 0]

    totalPixelCount = (color_box_region[2]) * (color_box_region[3])
    for y in range(color_box_region[1], color_box_region[1] + color_box_region[3]):
        for x in range(color_box_region[0], color_box_region[0] + color_box_region[2]):
            cur_pixel = hsv_frame[x, y]
            controller_hsv_color += cur_pixel
    controller_hsv_color[0] = controller_hsv_color[0] / totalPixelCount
    controller_hsv_color[1] = controller_hsv_color[1] / totalPixelCount
    controller_hsv_color[2] = controller_hsv_color[2] / totalPixelCount

    return controller_hsv_color


def get_color_in_point(src_frame, gauss_frame):
    hsv_frame = cv2.cvtColor(src_frame, cv2.COLOR_BGR2HSV)
    color_box_region = cv2.selectROI('FirstFrame', src_frame)
    cropped = hsv_frame[color_box_region[1]:color_box_region[1] + color_box_region[3], color_box_region[0]:color_box_region[0] + color_box_region[2]]

    '''
    controller_hsv_color = hsv_frame[
        color_box_region[1] + color_box_region[3] // 2, color_box_region[0] + color_box_region[2] // 2]
    '''
    controller_hsv_color = cropped[cropped.shape[0]//2, cropped.shape[1]//2]

    return controller_hsv_color


def threshold_mask_to_color(frame, color):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    down_color = color.copy()
    down_color[0] = max(int(down_color[0]) - hue_range, 0)
    down_color[1] = max(int(down_color[1]) - saturation_range, 0)
    down_color[2] = max(int(down_color[2]) - value_range, 0)
    high_color = color.copy()
    high_color[0] = min(int(high_color[0]) + hue_range, 255)
    high_color[1] = min(int(high_color[1]) + saturation_range, 255)
    high_color[2] = min(int(high_color[2]) + value_range, 255)

    if (color[1]>200) or (color[2]>200):
        down_color[0] = 0
        high_color[0] = 255

    mask = cv2.inRange(hsv_frame, down_color, high_color)
    return mask


start()