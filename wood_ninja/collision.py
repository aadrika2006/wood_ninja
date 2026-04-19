def is_collision(px, py, ox, oy, ow, oh):
    return ox < px < ox + ow and oy < py < oy + oh