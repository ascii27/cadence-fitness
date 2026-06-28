"""Generate consistent minimalist exercise figure SVGs.

Each pose is a set of joints; the renderer draws the head, spine, arms, legs,
a ground shadow, and an optional motion arc — all in a consistent style.
Output: frontend/public/exercises/<slug>.svg
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "exercises")

W, H = 240, 180
EMBER = "#ff6a45"
MUTED = "#3a3a44"
SHADOW = "#000000"

# Each pose: joints dict with required head, neck, hip and limb points.
# Optional second arm/leg via *2 keys. Optional "ground" y, "arc" [x,y,r,a0,a1].
# Coordinates: x right, y down, viewBox 240x180.

P = {}

# ---------- PLANKS / PUSH (horizontal, head left) ----------
P["plank"] = dict(head=(48,96), neck=(66,100), hip=(150,104), knee=(180,106), foot=(206,110),
                  elbow=(70,124), hand=(74,138), ground=140)
P["side-plank"] = dict(head=(56,68), neck=(72,80), hip=(146,116), knee=(174,128), foot=(202,140),
                       elbow=(70,118), hand=(74,138), elbow2=(80,58), hand2=(86,38), ground=142)
P["push-up"] = dict(head=(52,92), neck=(70,98), hip=(152,106), knee=(182,108), foot=(208,112),
                    elbow=(66,120), hand=(72,138), ground=140, arc=(118,150,0,0,0))
P["knee-push-up"] = dict(head=(54,92), neck=(72,98), hip=(148,114), knee=(176,128), foot=(150,132),
                         elbow=(68,120), hand=(74,138), ground=140)
P["incline-push-up"] = dict(head=(70,72), neck=(86,80), hip=(156,116), knee=(184,128), foot=(208,136),
                            elbow=(96,86), hand=(120,96), ground=140)
P["diamond-push-up"] = dict(head=(52,94), neck=(70,100), hip=(152,108), knee=(182,110), foot=(208,114),
                            elbow=(78,122), hand=(96,138), ground=140)
P["pike-push-up"] = dict(head=(96,118), neck=(104,104), hip=(150,52), knee=(176,96), foot=(192,138),
                         elbow=(94,128), hand=(92,140), ground=144)
P["mountain-climber"] = dict(head=(50,92), neck=(68,98), hip=(150,104), knee=(120,124), foot=(150,140),
                             knee2=(184,108), foot2=(208,112), elbow=(70,122), hand=(74,138), ground=140)
P["bird-dog"] = dict(head=(60,86), neck=(78,92), hip=(150,96), knee=(150,124), foot=(150,140),
                     knee2=(186,86), foot2=(212,78), elbow=(64,118), hand=(60,74), ground=140)
P["cat-cow"] = dict(head=(64,96), neck=(82,86), hip=(158,86), knee=(160,118), foot=(160,138),
                    elbow=(86,118), hand=(86,138), ground=140, arc=(120,70,40,200,340))
P["childs-pose"] = dict(head=(70,116), neck=(92,116), hip=(168,108), knee=(176,128), foot=(150,134),
                        elbow=(64,118), hand=(40,120), ground=140)
P["thoracic-rotation"] = dict(head=(66,92), neck=(84,92), hip=(160,94), knee=(160,120), foot=(160,138),
                              knee2=(184,120), elbow=(96,72), hand=(118,58), ground=140,
                              arc=(110,80,34,250,30))
P["kneeling-hip-flexor-stretch"] = dict(head=(132,42), neck=(132,64), hip=(132,104), knee=(108,132), foot=(80,140),
                                        knee2=(160,118), foot2=(186,140), elbow=(132,88), hand=(132,104), ground=140)

# ---------- LYING ON BACK (floor ~ y 126) ----------
P["glute-bridge"] = dict(head=(56,118), neck=(74,116), hip=(150,92), knee=(180,96), foot=(196,124),
                         elbow=(70,124), hand=(56,126), ground=128)
P["single-leg-glute-bridge"] = dict(head=(54,118), neck=(72,116), hip=(150,90), knee=(180,94), foot=(196,122),
                                    knee2=(176,60), foot2=(190,42), elbow=(68,124), hand=(54,126), ground=128)
P["hollow-hold"] = dict(head=(52,104), neck=(72,108), hip=(132,112), knee=(176,96), foot=(204,86),
                        elbow=(44,86), hand=(34,72), ground=124, arc=(120,118,0,0,0))
P["dead-bug"] = dict(head=(150,118), neck=(140,108), hip=(112,108), knee=(96,78), foot=(82,58),
                     knee2=(132,84), foot2=(150,64), elbow=(150,86), hand=(160,66),
                     elbow2=(126,84), hand2=(116,62), ground=124)
P["bicycle-crunch"] = dict(head=(60,100), neck=(78,104), hip=(140,110), knee=(160,86), foot=(150,68),
                           knee2=(178,108), foot2=(206,108), elbow=(74,88), hand=(96,92), ground=122)
P["leg-raise"] = dict(head=(52,114), neck=(72,114), hip=(140,114), knee=(150,84), foot=(158,56),
                      elbow=(64,120), hand=(50,122), ground=124)
P["russian-twist"] = dict(head=(96,66), neck=(104,84), hip=(118,116), knee=(150,104), foot=(178,116),
                          elbow=(120,92), hand=(140,92), ground=122, arc=(118,92,30,200,340))

# ---------- LYING FACE DOWN ----------
P["superman"] = dict(head=(58,98), neck=(76,100), hip=(150,104), knee=(178,96), foot=(202,84),
                     elbow=(46,84), hand=(30,72), ground=120)
P["prone-yt-raise"] = dict(head=(60,104), neck=(78,106), hip=(150,110), knee=(178,112), foot=(202,114),
                           elbow=(54,84), hand=(40,66), elbow2=(70,82), hand2=(72,60), ground=122)
P["reverse-snow-angel"] = dict(head=(60,104), neck=(78,106), hip=(150,110), knee=(178,112), foot=(202,114),
                               elbow=(70,118), hand=(86,124), ground=122, arc=(80,104,30,200,20))

# ---------- STANDING (ground y 152) ----------
P["bodyweight-squat"] = dict(head=(112,46), neck=(116,66), hip=(126,104), knee=(110,124), foot=(108,150),
                             knee2=(146,122), foot2=(150,150), elbow=(132,82), hand=(150,84), ground=152)
P["reverse-lunge"] = dict(head=(120,42), neck=(120,64), hip=(122,104), knee=(104,126), foot=(96,150),
                          knee2=(158,128), foot2=(178,150), elbow=(110,90), hand=(104,108), ground=152)
P["split-squat"] = dict(head=(116,42), neck=(118,64), hip=(120,102), knee=(100,124), foot=(92,150),
                        knee2=(156,126), foot2=(168,138), elbow=(110,88), hand=(104,104), ground=152)
P["lateral-lunge"] = dict(head=(120,46), neck=(122,66), hip=(132,100), knee=(168,122), foot=(190,150),
                          knee2=(96,118), foot2=(76,150), elbow=(118,86), hand=(150,98), ground=152)
P["wall-sit"] = dict(head=(150,52), neck=(150,72), hip=(150,108), knee=(112,108), foot=(110,150),
                     elbow=(150,92), hand=(120,96), ground=152, arc=(165,100,0,0,0))
P["calf-raise"] = dict(head=(120,40), neck=(120,62), hip=(120,104), knee=(120,128), foot=(122,144),
                       elbow=(120,88), hand=(120,108), ground=148, arc=(120,150,0,0,0))
P["wall"] = None

P["marching-high-knees"] = dict(head=(118,40), neck=(118,62), hip=(120,104), knee=(150,96), foot=(168,116),
                                knee2=(112,128), foot2=(110,150), elbow=(96,86), hand=(86,70),
                                elbow2=(140,86), hand2=(150,104), ground=152)
P["jumping-jack"] = dict(head=(120,40), neck=(120,62), hip=(120,104), knee=(100,126), foot=(86,148),
                         knee2=(140,126), foot2=(154,148), elbow=(96,40), hand=(80,24),
                         elbow2=(144,40), hand2=(160,24), ground=150)
P["downward-dog"] = dict(head=(86,96), neck=(96,86), hip=(150,46), knee=(176,96), foot=(196,140),
                         elbow=(80,108), hand=(70,124), ground=144)
P["burpee"] = dict(head=(56,96), neck=(74,100), hip=(150,106), knee=(180,108), foot=(206,112),
                   elbow=(70,122), hand=(74,138), ground=140, arc=(150,150,0,0,0))


def pt(j, name):
    return j.get(name)


def polyline(points, width=11):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points if x is not None)
    return (f'<polyline points="{pts}" fill="none" stroke="{EMBER}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')


def render(slug, j):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'role="img" aria-label="{slug}">']
    # ground shadow
    gy = j.get("ground", 150)
    parts.append(f'<ellipse cx="120" cy="{gy+8}" rx="78" ry="7" fill="{SHADOW}" opacity="0.22"/>')
    parts.append(f'<line x1="26" y1="{gy+8}" x2="214" y2="{gy+8}" stroke="{MUTED}" '
                 f'stroke-width="2" stroke-linecap="round"/>')

    # optional motion arc (muted)
    arc = j.get("arc")
    if arc and arc[2] > 0:
        import math
        cx, cy, r, a0, a1 = arc
        x0, y0 = cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0))
        x1, y1 = cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1))
        large = 1 if (a1 - a0) % 360 > 180 else 0
        parts.append(f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}" '
                     f'fill="none" stroke="{MUTED}" stroke-width="3" stroke-linecap="round" '
                     f'stroke-dasharray="2 7"/>')

    g = ['<g>']
    # legs (behind), arms, spine
    if pt(j, "knee2"):
        g.append(polyline([j["hip"], j["knee2"], j.get("foot2", j["knee2"])]))
    g.append(polyline([j["hip"], j["knee"], j.get("foot", j["knee"])]))
    g.append(polyline([j["neck"], j["hip"]]))  # spine
    if pt(j, "elbow2"):
        g.append(polyline([j["neck"], j["elbow2"], j.get("hand2", j["elbow2"])]))
    if pt(j, "elbow"):
        g.append(polyline([j["neck"], j["elbow"], j.get("hand", j["elbow"])]))
    # neck stub + head
    hx, hy = j["head"]
    nx, ny = j["neck"]
    g.append(polyline([(hx, hy), (nx, ny)], width=11))
    g.append(f'<circle cx="{hx}" cy="{hy}" r="12.5" fill="{EMBER}"/>')
    g.append('</g>')
    parts.extend(g)
    parts.append('</svg>')
    return "".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for slug, j in P.items():
        if j is None:
            continue
        svg = render(slug, j)
        with open(os.path.join(OUT, f"{slug}.svg"), "w") as f:
            f.write(svg)
        n += 1
    print(f"wrote {n} svgs to {OUT}")


if __name__ == "__main__":
    main()
