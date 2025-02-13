
class Circle:
    def __init__(self, radius, center_x, center_y, direction, color, motion_speed=1):
        self.radius = radius if radius > 0 else 1
        self.centerX = center_x
        self.centerY = center_y
        self.motionSpeed = motion_speed
        self.direction = direction
        self.color = color


    def move(self):
        dx = self.motionSpeed * self.direction[0]
        dy = self.motionSpeed * self.direction[1]
        self.centerX += dx
        self.centerY += dy

    def simple_move(self):
        dy = self.motionSpeed
        self.centerY += dy