# ConvexHullAnimation
A collection of convex hull scripts animated by manimce.

Requirements:
  - Manim Community v0.13.1
  - Python 3.9.7

Usage:
manim [file.py]

Output:
./media/videos/{graham_scan,jarvis_march}/[Scene Name].mp4

We have four files.
  - geometry.py
  - graham_scan.py
  - jarvis_march.py
  - points

geometry.py is a supporting file to help the construction and management of Dot and Line objects.
graham_scan.py produces a manim Scene that renders a Graham's Scan algorithm on a set of points.
jarvis_march.py produces a manim Scene that renders a Jarvis' March algorithm on a set of points.
points is an example file of a predetermined set of points to be rendered in the algorithm.

There are several parameters that can be tweaked in each file for customization.
  - points_file     : Leave empty for randomized points, otherwise provide a filename containing the points to be rendered.
  - rdn             : Set in case you want a randomized set of points, otherwise, the program will use the seed set in "seed".
  - seed            : The seed used for the generation of random points.
  - num_rand_points : The number of points to be generated.
  - wait            : Introduces short pauses in the animation for viewing clarity.
  - animation_speed : The animation speed scaling. Set to 0.5 for half the speed, 2 for twice.
