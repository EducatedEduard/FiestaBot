class Object:
    position = (0, 0)
    angle = 0
    type = ""

    def __init__(self, position, type, angle = 0):
        self.position = position
        self.angle = angle
        self.type = type

    def get_offset(self, x, y):
        return Object((self.position + (x,y)), self.type, self.angle)