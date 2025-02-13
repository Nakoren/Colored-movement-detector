import random
import cv2

from circle import Circle

class CircleController:
    def __init__(self, max_frame_count, x_lim, y_lim, hard_mode, max_circles, required_contour_area):
        self.circleList = []
        self.frameCount = 0
        self.spawnInterval = max_frame_count
        self.hardMode = hard_mode
        self.maxCircles = max_circles
        self.maxX = x_lim
        self.maxY = y_lim
        self.score = 0
        self.lost = 0

        self.reqContourArea = required_contour_area

    def start_next_iteration(self):
        for circle in self.circleList:
            circle.move()
        self.frameCount += 1
        if(self.frameCount==self.spawnInterval):
            if not self.hardMode:
                self.init_random_simple_circle()
            else:
                self.init_random_complex_circle()
            if (len(self.circleList) > self.maxCircles):
                self.delete_circle(self.circleList[0])
            self.frameCount = 0


    def delete_circle(self, circle):
        self.circleList.remove(circle)

    def init_random_simple_circle(self):
        x_spawn = random.randint(0, self.maxX)
        y_spawn = 0
        direction = (0, 1)
        radius = 20
        circle = Circle(radius, x_spawn, y_spawn, direction, (0, 255, 0))
        self.circleList.append(circle)

    def init_random_complex_circle(self):
        x_spawn = random.randint(0, self.maxX)
        y_spawn = random.randint(0, self.maxY)
        direction = (random.randint(-1,1), random.randint(-1,1))
        speed = random.randint(1, 3)
        radius = random.randint(10, 30)
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]
        rand_color = colors[random.randint(0, len(colors) - 1)]
        circle = Circle(radius, x_spawn, y_spawn, direction, rand_color, motion_speed=speed)
        self.circleList.append(circle)

    def check_frame(self, contours):
        for circle in self.circleList:
            deleted = False
            if deleted:
                continue
            if (circle.centerX > self.maxX) or (circle.centerY > self.maxY):
                self.delete_circle(circle)
                deleted = True
                self.lost += 1
                continue
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < self.reqContourArea:
                    continue
                dist = cv2.pointPolygonTest(contour, (circle.centerX, circle.centerY), True)
                if dist + circle.radius > 0:
                    self.score += 1
                    self.delete_circle(circle)
                    deleted = True
                    break