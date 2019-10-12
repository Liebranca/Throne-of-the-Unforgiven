from colorsys import rgb_to_hls, hls_to_rgb

def hexToRGB(key):
	h = key.lstrip('#')
	return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def adjust_color_lightness(r, g, b, factor):

	factor = min(max(-1.0, factor), 1.0)

	h, l, s = rgb_to_hls(r, g, b)
	l += factor
	r, g, b = hls_to_rgb(h, l, s)

	return [min(max(0.01, r), 0.8), min(max(0.01, g), 0.8), min(max(0.01, b), 0.8)]

def lighten(r, g, b, factor=0.1):
    return adjust_color_lightness(r, g, b, factor)

def darken(r, g, b, factor=0.1):
    return adjust_color_lightness(r, g, b, -factor)

color_ops_dict = {0:darken, 1:lighten}