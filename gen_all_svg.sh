# Reid Horuff
#
# Helper script to convert all svgs into headers in the arduino folder

set -e
set -x

out=scope_draw/

# generates at half resolution and centers on a full resolution canvas for testing purposes
python svg_to_arr.py --svg=svg/square.svg --resolution=2048 --x=1024 --y=1024 --code --prefix=square > $out/square.h

# generates at regular 4096 resolution
python svg_to_arr.py --svg=svg/seattle.svg --resolution=4096 --prefix=seattle --code > $out/seattle.h

cat $out/*.h
