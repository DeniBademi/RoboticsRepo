class Entity:
    lower_color = None
    upper_color = None
    name = None

    def __init__(self, lower_color, upper_color, name):
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.name = name


TRASH = Entity([0, 50, 80], [70, 94, 143], "TRASH")
TRASH_2 = Entity([0, 30, 100], [70, 50, 140], "TRASH_2")
PLANT_COLLECTOR = Entity([134, 104, 0], [154, 154, 12], "PLANT_COLLECTOR")
TRASH_COLLECTOR = Entity([0, 0, 70], [0, 0, 255], "TRASH_COLLECTOR")
CHARGER = Entity([0, 150, 150], [100, 255, 255], "CHARGER")
PLANT = Entity([0, 70, 0], [50, 255, 50], "PLANT")
COMPRESSED = Entity([0, 0, 0], [30,30,30], "COMPRESSED")