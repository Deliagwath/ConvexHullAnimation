from manim import *
import importlib
import math
import random

geo = importlib.import_module("geometry")
mPoint = geo.mPoint
mLine = geo.mLine

points_file = "" # Leave empty for randomized points

rdn = False
seed = 3
num_rand_points = 10

wait = True
animation_speed = 1

class GrahamScan(Scene):
    def construct(self):
        if points_file != "":
            points, min_x, max_x, min_y, max_y = self.load_points(points_file)
            axes_x_min, axes_x_max = min_x - 1, max_x + 1
            axes_y_min, axes_y_max = min_y - 1, max_y + 1
        else:
            if rdn: random.seed()
            else: random.seed(a=seed)
            axes_x_min, axes_x_max = 0, 20
            axes_y_min, axes_y_max = 0, 20
            points = self.randomize_points(axes_x_min, axes_x_max, axes_y_min, axes_y_max, num_rand_points)

        axes = Axes(
                x_range=(axes_x_min, axes_x_max),
                y_range=(axes_y_min, axes_y_max),
                x_length=10,
                y_length=6,
                axis_config={
                    "stroke_color": GREY_A,
                    "stroke_width": 2,
                    },
                )
        points = [mPoint(x, y, axes) for (x, y) in points]

        self.play(Write(axes), run_time=animation_speed)

        self.play(
                LaggedStart(
                    *[Write(p.point) for p in points],
                    lag_ratio=1 / len(points)
                    ),
                    run_time=animation_speed
                )

        random_points = random.choices(points, k=3)
        avg_x = sum([p.x for p in random_points]) / len(random_points)
        avg_y = sum([p.y for p in random_points]) / len(random_points)
        avg_point = mPoint(avg_x, avg_y, axes)
        avg_point.point.set_color(YELLOW)
        
        hull_points = []
        hull_lines = []
        avg_label = Tex(fr"median=({avg_point.x:.2f}, {avg_point.y:.2f})", color=WHITE)
        avg_label.next_to(avg_point.point, UP)
        label_box = Rectangle(
                width=avg_label.width + 0.25,
                height=avg_label.height + 0.25,
                color=WHITE,
                fill_color=WHITE,
                fill_opacity=0.1
                )
        label_box.next_to(avg_label, ORIGIN)
        avg_label = VGroup(avg_label, label_box)
        self.play(
                Write(avg_point.point),
                *[ReplacementTransform(rdn_pt.point, rdn_pt.set_color(BLUE).point) for rdn_pt in random_points],
                FadeIn(avg_label, scale=0.5),
                run_time=animation_speed
                )
        if wait: self.wait()
        self.play(
                FadeOut(avg_label),
                *[ReplacementTransform(rdn_pt.point, rdn_pt.set_color(RED).point) for rdn_pt in random_points],
                run_time=animation_speed
                )
        
        # Construct x_min, perform Jarvis, add two points and first line to hull
        x_min = None
        for point in points:
            if x_min is None:
                x_min = point
                continue
            if x_min.x == point.x and x_min.y < point.y:
                x_min = point
            if x_min.x > point.x:
                x_min = point
        
        hull_points.append(x_min)
        min_label = Tex(fr"min=({x_min.x}, {x_min.y})", color=WHITE)
        min_label.next_to(x_min.point, UP)
        label_box = Rectangle(
                width=min_label.width + 0.25,
                height=min_label.height + 0.25,
                color=WHITE,
                fill_color=WHITE,
                fill_opacity=0.1
                )
        label_box.next_to(min_label, ORIGIN)
        min_label = VGroup(min_label, label_box)
        self.play(
                ReplacementTransform(x_min.point, x_min.point.set_color(BLUE)),
                FadeIn(min_label, scale=0.5),
                run_time=animation_speed
                )
        if wait: self.wait()
        self.play(
                FadeOut(min_label),
                run_time=animation_speed
                )
        
        # Preprocess, sort lines after constructing first hull line
        lines = self.construct_lines_from_point(x_min, points)
        max_slope = self.get_max_slope(lines)
        hull_points.append(max_slope.end)
        hull_lines.append(max_slope)

        self.play(
                LaggedStart(
                    *[Write(l.line) for l in lines],
                    lag_ratio=0.25
                    ),
                run_time=animation_speed
                )

        if wait: self.wait()
        self.play(
                LaggedStart(
                    *[Uncreate(l.line) for l in lines if l not in hull_lines],
                    lag_ratio=0.25
                    ),
                run_time=animation_speed
                )
        new_hull_point = Dot(color=BLUE).move_to(axes.c2p(max_slope.end.x, max_slope.end.y))
        self.play(ReplacementTransform(max_slope.end.point, new_hull_point), run_time=animation_speed)

        lines = self.construct_lines_from_point(avg_point, points)
        start_line = mLine(avg_point, hull_lines[-1].end)
        lines = self.construct_angles_wrt_line(start_line, lines)
        shift = 1
        for i in range(len(lines) - 1):
            if lines[i].end == hull_lines[-1].end:
                break
            shift += 1
        lines = lines[shift:] + lines[:shift]
        
        self.play(Write(lines[0].line), run_time=animation_speed)
        i = 0
        break_next = False
        considering_point = lines[0].end

        # While the point we're considering is not the first point in our hull
        while considering_point != hull_points[0]:
            considering_point = lines[i].end
            if break_next: break
            if considering_point == hull_points[0]: break_next = True

            # Update considering point ray
            if i > 0:
                self.remove(lines[i - 1].line)
                self.play(ReplacementTransform(lines[i - 1].line, lines[i].line), run_time=animation_speed)

            # Update considering hull line
            hull_lines.append(mLine(hull_points[-1], considering_point))
            self.play(Write(hull_lines[-1].line), run_time=animation_speed)

            # If we have a left turn
            while hull_lines[-2].is_left_turn_to(hull_lines[-1]):
                removing_point = hull_points.pop()
                removing_latest_hull = hull_lines.pop()
                removing_prev_hull = hull_lines.pop()
                self.play(
                    LaggedStart(
                        *[
                            ReplacementTransform(
                                removing_point.point,
                                removing_point.point.set_color(RED)
                            ),
                            Unwrite(removing_latest_hull.line),
                            Unwrite(removing_prev_hull.line),
                        ],
                        lag_ratio=1 / 3
                    ),
                    run_time=animation_speed
                )
                hull_lines.append(mLine(hull_points[-1], lines[i].end))
                self.play(Write(hull_lines[-1].line), run_time=animation_speed)
            
            # Change new hull point color to blue
            hull_points.append(lines[i].end)
            self.play(
                ReplacementTransform(
                    lines[i].end.point,
                    lines[i].end.point.set_color(BLUE)
                ),
                run_time=animation_speed
            )
            i += 1
        
        self.play(Unwrite(lines[i - 1].line), run_time=animation_speed)
        self.play(
            LaggedStart(
                *[
                    ReplacementTransform(
                        hull.line,
                        hull.set_color(BLUE).line
                    ) for hull in hull_lines
                ],
                lag_ratio = 1 / len(hull_lines)
            ),
            run_time=animation_speed
        )

    def get_bounds(self, points):
        x_min = None
        x_max = None
        y_min = None
        y_max = None
        for point in points:
            x, y = point[0], point[1]
            if x_min is None:
                x_min = x
                x_max = x
            if y_min is None:
                y_min = y
                y_max = y
            if x_min > x: x_min = x
            if x_max < x: x_max = x
            if y_min > y: y_min = y
            if y_max < y: y_max = y
        return x_min, x_max, y_min, y_max

    def parse_args(self, axes, pairs):
        points = {}
        for pair in pairs:
            x, y = [int(z) for z in pair.split(',')]
            coords = f"{x}-{y}"
            if coords in points: continue
            points[coords] = mPoint(x, y, axes)
            return list(points.values())

    def randomize_points(self, min_x:int, max_x:int, min_y:int, max_y:int, num:int) -> List[mPoint]:
        points = {}
        while len(points) < num:
            (x, y) = random.randint(min_x + 1, max_x - 1), random.randint(min_y + 1, max_y - 1)
            coords = f"{x}-{y}"
            if coords in points: continue
            points[coords] = (x, y)
        return list(points.values())

    def construct_lines_from_point(self, origin:mPoint, points:List[mPoint]) -> List[mLine]:
        lines = []
        for point in points:
            if point is origin: continue
            dx = point.x - origin.x
            dy = point.y - origin.y
            # slope = dy/dx
            if dx == 0:
                # Handle vertical slopes    
                slope = 999999 if dy > 0 else -999999
            else:
                slope = dy / dx
            # magnitude = sqrt(dx^2 + dy^2)
            magnitude = math.sqrt((dx * dx) + (dy * dy))
            line = mLine(origin, point)
            line.line.set_color(BLUE)
            line.set_slope(slope)
            line.set_mag(magnitude)
            lines.append(line)

        lines = sorted(lines, key=lambda l: l.get_slope(), reverse=True)
        return lines
    
    def construct_angles_wrt_line(self, wrt:mLine, lines:List[mLine]) -> List[mLine]:
        for line in lines:
            line.set_angle(wrt.get_angle_to(line))
        
        lines = sorted(lines, key=lambda l: l.get_angle(), reverse=True)
        return lines

    def get_max_slope(self, lines:List[mLine]) -> mLine:
        max_slope = None
        for line in lines:
            if max_slope is None:
                max_slope = line
                continue
            if max_slope.get_slope() < line.get_slope():
                max_slope = line
                continue

            # Case for co-linearity, we would pick the slope with largest magnitude.
            if max_slope.get_slope() == line.get_slope() and max_slope.get_mag() < line.get_mag():
                max_slope = line
                continue

        return max_slope

    def load_points(self, filename:str):
        points = []
        with open(filename) as f:
            raw = f.readlines()
            for line in raw:
                if line == "": continue
                [x, y] = line.split(" ")
                points.append((int(x), int(y)))
        min_x, max_x, min_y, max_y = self.get_bounds(points)
        return points, min_x, max_x, min_y, max_y
    
    def debug(self, obj, color) -> None:
        self.play(Write(obj.set_color(color)))
    
    def debug_lines(self, lines:List[mLine]) -> None:
        line_colors = color_gradient([RED, BLUE], len(lines))
        for i, line in enumerate(lines):
            line.line.set_color(line_colors[i])
        self.play(LaggedStart(*[Write(l.line) for l in lines]))