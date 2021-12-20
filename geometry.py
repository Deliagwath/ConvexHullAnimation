from manim import *

class mPoint:
    x: int
    y: int
    npp: np.array
    point: Dot

    def __init__(self, x:int, y:int, axes:Axes=None) -> None:
        self.x = x
        self.y = y
        self.npp = np.array([x, y, 0])
        self.point = self.construct_point(x, y, axes)
    
    def construct_point(self, x:int, y:int, axes:Axes=None) -> Dot:
        if axes is not None:
            dot = Dot(color=RED)
            dot.move_to(axes.c2p(x, y))
        else:
            dot = Dot(point=np.array([x, y, 0]), color=RED)
        return dot
    
    def get_coords(self):
        return (self.x, self.y)
    
    def get_np(self) -> np.array:
        return self.npp

    def get_point(self) -> "mPoint":
        return self.point
    
    def set_color(self, color) -> "mPoint":
        self.point.set_color(color)
        return self

    def move_to(self, coords) -> None:
        self.point.move_to(coords)

class mLine:
    start: mPoint
    end: mPoint
    line: "mLine"
    slope: float
    angle: float
    mag: float

    def __init__(self, start:mPoint, end:mPoint) -> None:
        self.start = start
        self.end = end
        self.line = self.construct_line(start, end)

    def construct_line(self, start:mPoint, end:mPoint) -> Line:
        line = Line(
                start.point.get_center(),
                end.point.get_center()
                )
        return line
    
    def get_start(self) -> mPoint:
        return self.start
    
    def get_end(self) -> mPoint:
        return self.end

    def get_line(self) -> Line:
        return self.line

    def to_vector(self) -> np.array:
        return np.array([
            self.end.x - self.start.x,
            self.end.y - self.start.y
        ])

    def unit_vector(self, vector:np.array) -> np.array:
        return vector / np.linalg.norm(vector)

    def get_angle_to(self, line="mLine") -> float:
        vec_from = self.to_vector()
        vec_to = line.to_vector()
        r = np.rad2deg(np.arctan2(
            vec_from[0] * vec_to[1] - vec_from[1] * vec_to[0],
            vec_from[0] * vec_to[0] + vec_from[1] * vec_to[1]
        )) + 180
        return r

    def set_slope(self, slope:float) -> None:
        self.slope = slope
    
    def get_slope(self) -> float:
        return self.slope
    
    def set_angle(self, angle:float) -> None:
        self.angle = angle
    
    def get_angle(self) -> float:
        return self.angle

    def set_mag(self, mag:float) -> None:
        self.mag = mag
    
    def get_mag(self) -> float:
        return self.mag
    
    def set_color(self, color) -> "mLine":
        self.line.set_color(color)
        return self
    
    def is_left_turn_to(self, dest="mLine") -> bool:
        # line1 A -> B (self)
        # line2 B -> C
        # Must reconstruct to B -> A & B -> C
        rev_line = mLine(self.end, self.start)
        angle = dest.get_angle_to(rev_line)
        # print(f"LEFT TURN TEST ANGLE {angle} : {angle > 180}")
        return angle > 180

class mPolygon:
    points: List[np.array]
    mpoints: List[mPoint]
    lines: List[mLine]
    polygon: Polygon

    def __init__(self, points:List[mPoint]) -> None:
        self.points = []
        for point in points:
            self.points.append(point.get_np())

        self.mpoints = points

        self.lines = []
        for i in range(1, len(points)):
            self.lines.append(mLine(points[i - 1], points[i]))
        self.lines.append(mLine(points[-1], points[0]))

        self.polygon = Polygon(*self.points)
