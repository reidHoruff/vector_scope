"""
Reid Horuff

This script finds all <path> elements in an SVG file, calculates all the
path coordinates and generates c arrays of these coordinates for use in other software.

The user can provide scaling and offset information.

The canvas size is calculated only from the span of the path coordinates which are rendered.


Only lines are supported, not curves. Inkscape allows you to convert a path containing
curves into a path of only lines.
"""

from xml.dom import minidom
import argparse
import sys

# supported data types
data_types = {
    'uint8_t': 8,
    'uint16_t': 16,
    'uint32_t': 32,
}


# parses <path> gcode like syntax to list of x,y coords
def parse_path_str(path_str):
    mode = None
    x_coords = []
    y_coords = []
    cx, cy = None, None
    tokens = path_str.split(' ')

    for tok in tokens:
        if tok in 'mMlvhH':
            mode = tok
            continue

        if tok in 'zZ':
            # ignore fill
            continue

        if tok in 'cCsS':
            print 'Bezier curves not supported.'
            sys.exit(1)

        # move to, subsequent args are treated as 'line to'
        if mode == 'M' or (mode == 'm' and cx is None):
            cx, cy = map(float, tok.split(','))
            mode = 'l'

        if mode == 'm':
            x, y = map(float, tok.split(','))
            mode = 'l'
            cx += x
            cy += y

        # relative line to
        elif mode == 'l':
            x, y = map(float, tok.split(','))
            cx += x
            cy += y

        # relative vertical line
        elif mode == 'v':
            y = float(tok)
            cy += y

        # relative horizontal line
        elif mode == 'h':
            x = float(tok)
            cx += x

        # absolute horizontal line
        elif mode == 'H':
            x = float(tok)
            cx = x

        x_coords.append(cx)
        y_coords.append(cy)

    return x_coords, y_coords


# parses simple svg file expected to contain a single <path> element
def parse_svg(args):
    xmldoc = minidom.parse(args.svg)
    paths = xmldoc.getElementsByTagName('path')

    if not args.code_only:
        print 'Paths found:', len(paths)

    # all path coordinates are packed into on array per component.
    # we provide an array containing the lengths of each path
    # so the start/end of each path can be determined at runtime
    path_x_coords = []
    path_y_coords = []
    path_lengths = []

    for path in paths:
        path_str = path.attributes['d'].value
        x_coords, y_coords = parse_path_str(path_str)

        assert len(x_coords) == len(y_coords)

        path_lengths.append(len(x_coords))

        path_x_coords += x_coords
        path_y_coords += y_coords

    minx = min(path_x_coords)
    miny = min(path_y_coords)
    maxx = max(path_x_coords)
    maxy = max(path_y_coords)

    width = maxx - minx
    height = maxy - miny

    if not args.code_only:
        print 'Canvas size:', width, height

    resolution = args.resolution
    scale_x = lambda x: int((x - minx) / float(width) * resolution) + args.x
    scale_y = lambda y: resolution - int((y - miny) / float(height) * resolution) + args.y

    xout = map(scale_x, path_x_coords)
    yout = map(scale_y, path_y_coords)

    if not args.code_only:
        print 'Min x', min(xout)
        print 'Max x', max(xout)
        print 'Min y', min(yout)
        print 'Max y', max(yout)
        print 'Bytes used:', len(xout) * 2 * (data_types[args.data_type]/8)
        print
        print 'OUTPUT:'

    print '/* auto generated with svg_to_arr.py */'
    print 'static uint16_t %s__num_paths = %d;' % (args.prefix, len(paths))
    print 'static uint32_t %s__num_points = %d;' % (args.prefix, len(path_x_coords))
    print 'static uint16_t %s__path_lengths[%d] = {%s};' % (args.prefix, len(path_lengths), ','.join(map(str, path_lengths)))
    print 'static %s %s__x_coords[%d] = {%s};' % (args.data_type, args.prefix, len(xout), ','.join(map(str, xout)))
    print 'static %s %s__y_coords[%d] = {%s};' % (args.data_type, args.prefix, len(yout), ','.join(map(str, yout)))


def main():
    parser = argparse.ArgumentParser(description='Convert svg path to c coordinates array.')
    parser.add_argument('--svg', type=str, required=True, help='Path to SVG file')
    parser.add_argument('--data_type', type=str, default='uint16_t', help='Data type for array.')
    parser.add_argument('--resolution', type=int, default=4096, help='DAC resolution')
    parser.add_argument('--path_num', type=int, default=0, help='Path element to convert.')
    parser.add_argument('--x', type=int, default=0, help='x offset.')
    parser.add_argument('--y', type=int, default=0, help='y offset.')
    parser.add_argument('--code', dest='code_only', action='store_true', help='Print code only.')
    parser.add_argument('--prefix', type=str, default='image', help='Prefix for generated data structures.')

    args = parser.parse_args()

    if args.data_type not in data_types:
        print 'Invalid data type'
        sys.exit(1)

    if args.resolution >= 2**data_types[args.data_type]:
        print 'Resolution greater than selected data type'
        sys.exit(1)

    parse_svg(args)

if __name__ == '__main__':
    main()
