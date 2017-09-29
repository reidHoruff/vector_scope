#include "seattle.h"
#include "square.h"
#include <math.h>

void setup() {
  analogWriteResolution(12);
}

void loop() {
  static int lx = 0;
  static int ly = 0;
  static int theta = 0;
  double xmod = cos(theta * 3.14 / 180.0);
  double zmod = sin(theta * 3.14 / 180.0);
  draw_screen_bounds();

  for (int i = 0; i < seattle__num_points; i++) {

    // center over origin
    int x = seattle__x_coords[i] - 2048;
    int y = seattle__y_coords[i] - 2048;


    /* we rotate around z axis giving us a modulated x
       value and we calculate a z
     */

    int z = x * zmod;
    x *= xmod;

    int f = 4096/3;

    /* dist from camera */
    int z_dist = f + (f) - z;

    int px = (float)x * f / z_dist;
    int py = (float)y * f / z_dist;

    px += 2048;
    py += 2048;

    ramp(lx, ly, px, py);

    lx = px;
    ly = py;
  }

  theta += 3;
  theta %= 360;
  delay(10);
}

void draw_screen_bounds() {
  int r = 4095;
  ramp(0, 0, 0, r);
  ramp(0, r, r, r);
  ramp(r, r, r, 0);
  ramp(r, 0, 0, 0);
}


/*
   Interpolation between begin and end coords.
   For better rendering use a double buffered DAC
   or some way to update the value of both DAC's at once.
*/
void ramp(int sx, int sy, int ex, int ey) {

  static int step_size = 30;

  int dx = ex - sx;
  int dy = ey - sy;

  float dist = sqrt(dx * dx + dy * dy);
  int num_steps = max(dist / step_size, 1);
  float stepx = ((float) dx / num_steps);
  float stepy = ((float) dy / num_steps);

  float x = sx;
  float y = sy;

  for (int i = 0; i < num_steps; i++) {
    write_dac(DAC1, (int)y);
    write_dac(DAC0, (int)x);
    x += stepx;
    y += stepy;
  }
}


void write_dac(int dac, int val) {
  if (val < 0) val = 0;
  else if (val >= 4096) val = 4095;
  analogWrite(dac, val);
}
