#include "seattle.h"
#include "square.h"
#include "reid.h"
#include <math.h>

#define DAC_RES 4096

void setup() {
  analogWriteResolution(12);
}

void loop() {
  static int theta = 0;

  draw_screen_bounds();
  render_scene(theta, reid__x_coords, reid__y_coords, reid__num_points);

  theta += 3;
  theta %= 360;

  //delay(10);
}

void render_scene(int theta, uint16_t* x_coords, uint16_t* y_coords, int num_points) {
  static int lx = 0;
  static int ly = 0;
  double xmod = cos(theta * 3.14 / 180.0);
  double zmod = sin(theta * 3.14 / 180.0);

  for (int i = 0; i < num_points; i++) {

    // center over origin
    int x = x_coords[i] - (DAC_RES / 2);
    int y = y_coords[i] - (DAC_RES / 2);


    /* we rotate around z axis giving us a modulated x
       value and we calculate a z
     */

    int z = x * zmod;
    x *= xmod;

    int f = DAC_RES/2;

    /* dist from camera */
    int z_dist = 2*f - z;

    int px = (float)x * f / z_dist;
    int py = (float)y * f / z_dist;

    px += (DAC_RES / 2);
    py += (DAC_RES / 2);

    ramp(lx, ly, px, py);

    lx = px;
    ly = py;
  }
}

void draw_screen_bounds() {
  int r = DAC_RES - 1;
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

  if (out(sx) and out(sy) and out(ex) and out(ey)) {
    return;
  }

  sx = limit(sx);
  sy = limit(sy);
  ex = limit(ex);
  ey = limit(ey);

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


bool out(int val) {
  if (val < 0) return true;
  else if (val >= DAC_RES) return true;
  return false;
}

int limit(int val) {
  if (val < 0) val = 0;
  else if (val >= DAC_RES) val = DAC_RES - 1;
  return val;
}

void write_dac(int dac, int val) {
  if (val < 0) val = 0;
  else if (val >= DAC_RES) val = DAC_RES - 1;
  analogWrite(dac, val);
}
