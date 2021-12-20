from manim import *
import math
import random
import importlib
import operator as op

geo = importlib.import_module("geometry")
mPoint = geo.mPoint
mLine = geo.mLine

points_file = "points" # Leave empty for randomized points

rdn = False
seed = 3
num_rand_points = 10

wait = True
animation_speed = 1

class JarvisMarch(Scene):
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
                    )
                )

        x_min, x_max = None, None
        for point in points:
            if x_min is None or x_max is None:
                x_min = point
                x_max = point
                continue
            if x_min.x == point.x and x_min.y < point.y:
                x_min = point
            if x_min.x > point.x:
                x_min = point
            if x_max.x == point.x and x_max.y > point.y:
                x_max = point
            if x_max.x < point.x:
                x_max = point

        hull_points = [x_min]
        hull_lines = []
        min_dot = Dot(color=BLUE).move_to(axes.c2p(x_min.x, x_min.y))
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

        max_dot = Dot(color=BLUE).move_to(axes.c2p(x_max.x, x_max.y))
        max_label = Tex(fr"max=({x_max.x}, {x_max.y})", color=WHITE)
        max_label.next_to(x_max.point, UP)
        label_box = Rectangle(
                width=max_label.width + 0.25,
                height=max_label.height + 0.25,
                color=WHITE,
                fill_color=WHITE,
                fill_opacity=0.1
                )
        label_box.next_to(max_label, ORIGIN)
        max_label = VGroup(max_label, label_box)
        self.play(
                Transform(x_min.point, min_dot),
                Transform(x_max.point, max_dot),
                FadeIn(min_label, scale=0.5),
                FadeIn(max_label, scale=0.5),
                run_time=animation_speed
                )
        if wait: self.wait()
        self.play(
                FadeOut(min_label),
                FadeOut(max_label),
                run_time=animation_speed
                )

        sweep_bot = mPoint(x_min.x, axes_x_min, axes)
        sweep_top = mPoint(x_min.x, axes_y_max, axes)
        prev_sweep_line = mLine(sweep_bot, sweep_top)
        self.play(Write(prev_sweep_line.line), run_time=animation_speed)

        lines = self.construct_lines_from_point(x_min, op.ge, points)
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
        self.play(Transform(max_slope.end.point, new_hull_point), run_time=animation_speed)

        sweep_bot.move_to(axes.c2p(hull_points[-1].x, axes_y_min))
        sweep_top.move_to(axes.c2p(hull_points[-1].x, axes_y_max))
        sweep_line = mLine(sweep_bot, sweep_top)
        self.play(Transform(prev_sweep_line.line, sweep_line.line), run_time=animation_speed)

        previous = None
        considering = hull_points[-1]
        while considering is not x_max:
            print(f'UPPER HULL CONSIDERING ({considering.x}, {considering.y})')
            del lines
            del max_slope
            lines = self.construct_lines_from_point(considering, op.ge, [p for p in points if p is not previous])
            max_slope = self.get_max_slope(lines)
            hull_points.append(max_slope.end)
            hull_lines.append(max_slope)
            right_lines = [l for l in lines if l.end.x >= considering.x]
            for l in right_lines:
                if max_slope.start is l.start and max_slope.end is l.end:
                    l.line.set_color(BLUE)

            self.play(
                    LaggedStart(
                        *[Write(l.line) for l in right_lines],
                        lag_ratio=0.25
                        ),
                    run_time=animation_speed
                    )

            if wait: self.wait()
            self.play(
                    LaggedStart(
                        *[Uncreate(l.line) for l in right_lines if l not in hull_lines],
                        lag_ratio=0.25
                        ),
                    run_time=animation_speed
                    )
            previous = considering
            considering = hull_points[-1]
            new_hull_point = Dot(color=BLUE).move_to(axes.c2p(considering.x, considering.y))
            self.play(Transform(considering.point, new_hull_point), run_time=animation_speed)

            sweep_bot.move_to(axes.c2p(hull_points[-1].x, axes_y_min))
            sweep_top.move_to(axes.c2p(hull_points[-1].x, axes_y_max))
            sweep_line = mLine(sweep_bot, sweep_top)
            self.play(Transform(prev_sweep_line.line, sweep_line.line), run_time=animation_speed)

        while considering is not x_min:
            print(f'LOWER HULL CONSIDERING ({considering.x}, {considering.y})')
            del lines
            del max_slope
            lines = self.construct_lines_from_point(considering, op.le, [p for p in points if p is not previous])
            for l in lines:
                if l.slope == 999999: l.slope = -999999
            max_slope = self.get_max_slope(lines)
            hull_points.append(max_slope.end)
            hull_lines.append(max_slope)
            left_lines = [l for l in lines if l.end.x <= considering.x]
            for l in left_lines:
                if max_slope.start is l.start and max_slope.end is l.end:
                    l.line.set_color(BLUE)
            self.play(
                    LaggedStart(
                        *[Write(l.line) for l in left_lines],
                        lag_ratio=0.25
                        ),
                    run_time=animation_speed
                    )

            if wait: self.wait()
            self.play(
                    LaggedStart(
                        *[Uncreate(l.line) for l in left_lines if l not in hull_lines],
                        lag_ratio=0.25
                        ),
                    run_time=animation_speed
                    )
            previous = considering
            considering = hull_points[-1]
            new_hull_point = Dot(color=BLUE).move_to(axes.c2p(considering.x, considering.y))
            self.play(Transform(considering.point, new_hull_point), run_time=animation_speed)

            sweep_bot.move_to(axes.c2p(hull_points[-1].x, axes_x_min))
            sweep_top.move_to(axes.c2p(hull_points[-1].x, axes_x_max))
            sweep_line = mLine(sweep_bot, sweep_top)
            self.play(Transform(prev_sweep_line.line, sweep_line.line), run_time=animation_speed)
        
        self.play(Uncreate(prev_sweep_line.line), run_time=animation_speed)

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

    def construct_lines_from_point(self, origin:mPoint, relate:op, points:List[mPoint]) -> List[mLine]:
        lines = []
        for i, point in enumerate(points):
            if point is origin: continue
            if relate(point.x, origin.x):
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
                line.set_slope(slope)
                line.set_mag(magnitude)
                lines.append(line)
            else: continue

        lines = sorted(lines, key=lambda l: l.get_slope())
        line_colors = color_gradient([RED, BLUE], len(lines))
        for i, line in enumerate(lines):
            line.line.set_color(line_colors[i])

        return lines

    def get_max_slope(self, lines):
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