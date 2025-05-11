
def svg_path_to_build123d(svg_path: str):
    """
    Translates an SVG path string to build123d Python code.
# 
    Args:
        svg_path (str): The SVG path string.
# 
    Returns:
        BuildSketch: A build123d sketch object representing the path.
    """
    with BuildSketch() as sketch:
        for svg_path_line in svg_path.splitlines():
            commands = svg_path_line.split()
            i = 0
            while i < len(commands):
                command = commands[i]
                if command == 'm':  # Move to
                    x, y = map(float, commands[i + 1].split(','))
                    #sketch.move_to(Vector(x, y))
                    sketch.current_position = Vector(x,y)
                    i += 2
                elif command == 'c':  # Cubic Bezier curve
                    control1 = tuple(map(float, commands[i + 1].split(',')))
                    control2 = tuple(map(float, commands[i + 2].split(',')))
                    end_point = tuple(map(float, commands[i + 3].split(',')))
                    Bezier(sketch.current_position, Vector(*control1), Vector(*control2), Vector(*end_point))
                    i += 4
                elif command == 'V':  # Vertical line
                    y = float(commands[i + 1])
                    Line(sketch.current_position, Vector(sketch.current_position.X, y))
                    i += 2
                elif command == 'H':  # Horizontal line
                    x = float(commands[i + 1])
                    Line(sketch.current_position, Vector(x, sketch.current_position.Y))
                    i += 2
                elif command == 'z':  # Close path
                    # sketch.close()  # TODO
                    i += 1
                else:
                    i += 1  # Skip unrecognized commands
    return sketch