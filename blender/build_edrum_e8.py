# =====================================================================
#  E-Drum-Set "PULSE E8" fuer den 3D-Konfigurator  -  Blender Python Build-Script
#  Blender 4.x:  blender -b --python build_edrum_e8.py
#  oder in Blender: Scripting-Tab -> Script oeffnen -> Run Script
# =====================================================================
import bpy, bmesh, math, os, random
import numpy as np
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "/tmp/drums"
TEX = os.path.join(OUT, "textures")
os.makedirs(TEX, exist_ok=True)
random.seed(7); np.random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'CENTIMETERS'

INCH = 0.0254
rad = math.radians

# ---------------------------------------------------------------- Helfer
def T(x, y=0, z=0):
    if isinstance(x, (Vector, tuple, list)):
        return Matrix.Translation(Vector(x))
    return Matrix.Translation((x, y, z))
def Rx(a): return Matrix.Rotation(rad(a), 4, 'X')
def Ry(a): return Matrix.Rotation(rad(a), 4, 'Y')
def Rz(a): return Matrix.Rotation(rad(a), 4, 'Z')
def S(x, y, z): return Matrix.Diagonal((x, y, z, 1))
def Rzr(a): return Matrix.Rotation(a, 4, 'Z')

def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(c)
    return c

C_DRUM = collection("Trommeln")
C_CYM = collection("Becken")
C_HW = collection("Hardware")
C_EXTRA = collection("Extras")
C_RIG = collection("Rig")
C_RENDER = collection("Render_Setup")

# ---------------------------------------------------------------- Texturen
def save_image(name, arr, noncolor=False):
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels.foreach_set(np.clip(arr, 0, 1).astype(np.float32).ravel())
    path = os.path.join(TEX, name + ".png")
    img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    bpy.data.images.remove(img)
    img = bpy.data.images.load(path)
    if noncolor:
        img.colorspace_settings.name = 'Non-Color'
    img.pack()
    return img

def smooth_noise(h, w, cells, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((cells + 1, cells + 1))
    ys = np.linspace(0, cells, h); xs = np.linspace(0, cells, w)
    y0 = np.floor(ys).astype(int).clip(0, cells - 1); x0 = np.floor(xs).astype(int).clip(0, cells - 1)
    fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy

def cymbal_textures(size=1024, grooves=95):
    lin = np.linspace(-1, 1, size)
    x, y = np.meshgrid(lin, lin)
    r = np.sqrt(x * x + y * y)
    groove = np.sin(r * 2 * np.pi * grooves)
    H = 0.35 * groove
    # Hammerschlaege
    px = size / 2.0
    for _ in range(420):
        rr = np.sqrt(random.random()) * 0.97; a = random.random() * 2 * np.pi
        cx = int(px + rr * np.cos(a) * px); cy = int(px + rr * np.sin(a) * px)
        s = random.uniform(5, 11); win = int(s * 3)
        x0, x1 = max(cx - win, 0), min(cx + win, size); y0, y1 = max(cy - win, 0), min(cy + win, size)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        H[y0:y1, x0:x1] -= 2.2 * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))
    H[(r > 1.0) | (r < 0.03)] = 0
    gy, gx = np.gradient(H)
    st = 1.6
    n = np.dstack([-gx * st, -gy * st, np.ones_like(H)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = np.dstack([n * 0.5 + 0.5, np.ones_like(H)])
    bronze = np.array([0.80, 0.57, 0.29])
    shade = 0.86 + 0.10 * (0.5 + 0.5 * groove) + 0.04 * (r < 0.24)
    tone = 0.97 + 0.06 * smooth_noise(size, size, 6, 3)
    col = bronze[None, None, :] * (shade * tone)[:, :, None]
    color = np.dstack([col, np.ones_like(H)])
    return save_image("cymbal_color", color), save_image("cymbal_normal", normal, True)

def sparkle_textures(size=1024, flakes=26000):
    """Graue Flake-Helligkeit (wird mit der Lackfarbe multipliziert) + Flake-Normal-Map."""
    rng = np.random.default_rng(21)
    bright = np.full((size, size), 0.80) + 0.05 * smooth_noise(size, size, 9, 4)
    nx = np.zeros((size, size)); ny = np.zeros((size, size))
    xs = rng.integers(0, size, flakes); ys = rng.integers(0, size, flakes)
    val = rng.random(flakes) ** 3
    ang = rng.random(flakes) * 2 * np.pi; tilt = rng.random(flakes) * 0.8
    for dx in (0, 1):
        for dy in (0, 1):
            xx = (xs + dx) % size; yy = (ys + dy) % size
            bright[yy, xx] = np.maximum(bright[yy, xx], 0.80 + 0.20 * val + 0.0)
            nx[yy, xx] = np.cos(ang) * tilt; ny[yy, xx] = np.sin(ang) * tilt
    col = np.dstack([bright, bright, bright, np.ones_like(bright)])
    n = np.dstack([nx, ny, np.ones_like(nx)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    nor = np.dstack([n * 0.5 + 0.5, np.ones_like(nx)])
    return save_image("sparkle_flakes", col), save_image("sparkle_normal", nor, True)

def wood_texture(size=512):
    v = np.linspace(0, 1, size)[:, None] * np.ones((1, size))
    warp = smooth_noise(size, size, 5, 11) * 2.5 + smooth_noise(size, size, 23, 12) * 0.4
    grain = 0.5 + 0.5 * np.sin((v * 34 + warp) * 2 * np.pi)
    grain = grain ** 3
    light = np.array([0.80, 0.62, 0.42]); dark = np.array([0.58, 0.40, 0.24])
    col = light[None, None] * (1 - grain[..., None] * 0.55) + dark[None, None] * grain[..., None] * 0.55
    return save_image("maple_wood", np.dstack([col, np.ones((size, size))]))

# ---------------------------------------------------------------- Materialien
def setin(node, names, val):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = val
            return

def material(name, color, metallic=0.0, rough=0.5, coat=0.0, coat_rough=0.03):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if coat:
        setin(b, ["Coat Weight", "Clearcoat"], coat)
        setin(b, ["Coat Roughness", "Clearcoat Roughness"], coat_rough)
    m.diffuse_color = (*color, 1)
    return m

def add_textures(m, color_img=None, normal_img=None, nstrength=1.0):
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    if color_img:
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = color_img; t.location = (-500, 300)
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if normal_img:
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = normal_img; t.location = (-700, -200)
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-300, -200)
        nm.inputs["Strength"].default_value = nstrength
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])

# ---------------------------------------------------------------- Geometrie-Bausteine
def lathe(prof, segs=48, closed=True, planar_R=None, smooth=True):
    """Dreht ein (r, z)-Profil um die Z-Achse (wie Blender 'Spin')."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    n = len(prof)
    L = [0.0]
    for j in range(1, n):
        L.append(L[-1] + math.dist(prof[j], prof[j - 1]))
    total = (L[-1] + (math.dist(prof[-1], prof[0]) if closed else 0)) or 1.0
    grid, centers = [], {}
    for i in range(segs):
        a = 2 * math.pi * i / segs; ca, sa = math.cos(a), math.sin(a)
        row = []
        for j, (r, z) in enumerate(prof):
            if r < 1e-7:
                if j not in centers:
                    centers[j] = bm.verts.new((0, 0, z))
                row.append(centers[j])
            else:
                row.append(bm.verts.new((r * ca, r * sa, z)))
        grid.append(row)
    for i in range(segs):
        for j in (range(n) if closed else range(n - 1)):
            quad = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            vs, ids = [], []
            for (ci, pj) in quad:
                v = grid[ci % segs][pj % n]
                if v in vs:
                    continue
                vs.append(v); ids.append((ci, pj))
            if len(vs) < 3:
                continue
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            f.smooth = smooth
            for loop, (ci, pj) in zip(f.loops, ids):
                if planar_R:
                    co = loop.vert.co
                    loop[uvl].uv = (co.x / (2 * planar_R) + 0.5, co.y / (2 * planar_R) + 0.5)
                else:
                    loop[uvl].uv = (ci / segs, (L[pj] if pj < n else total) / total)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm

def box(sx, sy, sz, bevel=0.0, seg=2):
    bm = bmesh.new(); bm.loops.layers.uv.new("UVMap")
    bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=seg, profile=0.5,
                        affect='EDGES', clamp_overlap=True)
    for f in bm.faces:
        f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm

def tube_prof(r, z0, z1, ch=None):
    ch = min(r * 0.25, 0.0015) if ch is None else ch
    return [(0, z0), (r - ch, z0), (r, z0 + ch), (r, z1 - ch), (r - ch, z1), (0, z1)]

def torus_prof(Rm, rm, n=12):
    return [(Rm + rm * math.cos(2 * math.pi * k / n), rm * math.sin(2 * math.pi * k / n)) for k in range(n)]

def orient(p1, p2):
    d = Vector(p2) - Vector(p1)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return T(p1) @ q.to_matrix().to_4x4(), d.length

def cyl_between(p1, p2, r, segs=16):
    M, L = orient(p1, p2)
    return lathe(tube_prof(r, 0, L), segs), M

class Mesh:
    """Sammelt viele Einzelteile in einem Objekt (mit Material-Slots)."""
    def __init__(self, mats):
        self.bm = bmesh.new(); self.bm.loops.layers.uv.new("UVMap")
        self.mats = mats
    def add(self, src, M=Matrix(), mat=0):
        me = bpy.data.meshes.new("_tmp"); src.to_mesh(me); src.free()
        n0, f0 = len(self.bm.verts), len(self.bm.faces)
        self.bm.from_mesh(me); bpy.data.meshes.remove(me)
        self.bm.verts.ensure_lookup_table(); self.bm.faces.ensure_lookup_table()
        bmesh.ops.transform(self.bm, matrix=M, verts=self.bm.verts[n0:])
        new_faces = self.bm.faces[f0:]
        if M.determinant() < 0:
            bmesh.ops.reverse_faces(self.bm, faces=new_faces)
        if mat is not None:
            for f in new_faces:
                f.material_index = mat
        return self
    def tube(self, p1, p2, r, mat=0, segs=16):
        bm, M = cyl_between(p1, p2, r, segs); return self.add(bm, M, mat)
    def build(self, name, coll, M=Matrix(), smooth_angle=48):
        me = bpy.data.meshes.new(name); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        me.use_auto_smooth = True
        me.auto_smooth_angle = rad(smooth_angle)
        ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
        ob.matrix_world = M
        return ob

def shape_key(ob, key_name, fn):
    """fn(co: Vector) -> neue Koordinate (Objekt-Raum)."""
    if not ob.data.shape_keys:
        ob.shape_key_add(name="Basis", from_mix=False)
    k = ob.shape_key_add(name=key_name, from_mix=False)
    for i, v in enumerate(ob.data.vertices):
        k.data[i].co = fn(v.co.copy())
    k.value = 0.0
    return k

def wingnut(mesh, M, mat=0, s=1.0):
    mesh.add(lathe(tube_prof(0.0055 * s, 0, 0.009 * s), 14), M, mat)
    mesh.add(box(0.026 * s, 0.004 * s, 0.009 * s, 0.0012 * s), M @ T(0, 0, 0.006 * s), mat)

# ---------------------------------------------------------------- Becken
def cymbal_profile(R, bell_r, bell_h, bow_h, t, n=34):
    top = []
    hole = 0.0065
    for k in range(n + 1):
        u = k / n
        r = hole + (R - hole) * u
        if r < bell_r:
            b = (r - hole) / (bell_r - hole)
            z = bow_h + bell_h * (1 - b ** 2.2) ** 0.8
        else:
            b = (r - bell_r) / (R - bell_r)
            z = bow_h * (1 - b) ** 1.25
        top.append((r, z))
    bot = []
    for (r, z) in reversed(top):
        tt = t * (1 - 0.45 * (r / R))
        bot.append((r, z - tt))
    return top + bot

def make_cymbal(name, R, M, coll, bell_r=None, bell_h=0.022, bow_h=0.03, t=0.0016):
    bell_r = bell_r or R * 0.26
    bm = lathe(cymbal_profile(R, bell_r, bell_h, bow_h, t), 96, planar_R=R)
    ob = Mesh([M_CYM]).add(bm).build(name, coll, M, 60)
    ob["bell_r"], ob["R"], ob["bow_h"] = bell_r, R, bow_h
    return ob

def cymbal_mount(mesh, M, post_len=0.075):
    """Halterung auf dem Galgen: Gewindestange, Filze, Huelse, Fluegelmutter."""
    mesh.add(lathe(tube_prof(0.0042, -0.04, post_len - 0.04), 12), M, 0)
    felt = [(0.0045, 0), (0.019, 0), (0.019, 0.011), (0.0045, 0.011)]
    mesh.add(lathe(felt, 24), M @ T(0, 0, -0.012), 2)
    mesh.add(lathe(felt, 24), M @ T(0, 0, 0.024), 2)
    mesh.add(lathe(tube_prof(0.0075, 0, 0.004), 20), M @ T(0, 0, -0.016), 0)
    wingnut(mesh, M @ T(0, 0, 0.0355), 0, 1.1)

# ---------------------------------------------------------------- Staender
def tripod(mesh, base, top_z=0.33, leg_r=0.30, collar_z=0.30, brace_z=0.11, double=True):
    bx, by = base
    mesh.add(lathe(tube_prof(0.019, collar_z - 0.025, collar_z + 0.02), 24), T(bx, by, 0), 0)
    mesh.add(lathe(tube_prof(0.017, brace_z - 0.015, brace_z + 0.015), 24), T(bx, by, 0), 0)
    for k in range(3):
        a = rad(90 + 120 * k)
        ca, sa = math.cos(a), math.sin(a)
        p1 = Vector((bx + 0.02 * ca, by + 0.02 * sa, collar_z))
        p2 = Vector((bx + leg_r * ca, by + leg_r * sa, 0.018))
        off = Vector((-sa, ca, 0)) * 0.009
        for o in ((off, -off) if double else (Vector(),)):
            mesh.tube(p1 + o, p2 + o, 0.0062, 0, 12)
        foot = [(0, 0), (0.014, 0), (0.015, 0.004), (0.011, 0.028), (0, 0.028)]
        mesh.add(lathe(foot, 16), T(p2.x, p2.y, 0.0), 1)
        pm = p1.lerp(p2, 0.55)
        mesh.tube(Vector((bx + 0.018 * ca, by + 0.018 * sa, brace_z)), pm, 0.0048, 0, 10)

def joint_clamp(mesh, x, y, z, r=0.017):
    mesh.add(lathe(tube_prof(r, z - 0.016, z + 0.016), 24), T(x, y, 0), 0)
    wingnut(mesh, T(x + r, y, z) @ Ry(90), 0)

rig_bones = []   # (name, head, tail, parent, objects)

# =====================================================================
#  E-DRUM-SET  "PULSE E8"
#  Rohr-Rack (Querstange + zwei Seitenfluegel), runde Mesh-Pads,
#  Gummi-Becken mit Noppen, Kick-Saeule, Alu-Pedale, Modul mit Handyhalter.
#  Drummer sitzt bei -Y, Publikum bei +Y.
# =====================================================================

# ---------------------------------------------------------------- Texturen
def mesh_head_texture(size=1024, cells=120):
    """Gewebtes Mesh-Fell (weiss): Farbe + Normal-Map."""
    lin = np.linspace(0, cells * 2 * np.pi, size)
    x, y = np.meshgrid(lin, lin)
    H = 0.5 + 0.5 * np.maximum(np.abs(np.sin(x)) * (np.cos(y * 0.5) > 0), np.abs(np.sin(y)) * (np.cos(x * 0.5) <= 0))
    gy, gx = np.gradient(H)
    n = np.dstack([-gx * 3, -gy * 3, np.ones_like(H)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    nor = np.dstack([n * 0.5 + 0.5, np.ones_like(H)])
    v = 0.78 + 0.18 * H
    return save_image("mesh_head_color", np.dstack([v, v, v, np.ones_like(H)])), save_image("mesh_head_normal", nor, True)

def dots_normal(size=1024):
    """Noppen auf den Gummi-Becken: Ringe aus kleinen Kuppen (planare UV)."""
    H = np.zeros((size, size))
    c = size / 2
    yy, xx = np.mgrid[0:size, 0:size]
    for ring in range(6, 15):
        rr = ring / 15 * c * 0.97
        n = int(2 * np.pi * rr / 26)
        for k in range(n):
            a = 2 * np.pi * (k + 0.5 * (ring % 2)) / n
            cx, cy = c + rr * np.cos(a), c + rr * np.sin(a)
            x0, x1 = int(max(cx - 7, 0)), int(min(cx + 8, size)); y0, y1 = int(max(cy - 7, 0)), int(min(cy + 8, size))
            sx, sy = xx[y0:y1, x0:x1], yy[y0:y1, x0:x1]
            H[y0:y1, x0:x1] = np.maximum(H[y0:y1, x0:x1], np.clip(1 - ((sx - cx) ** 2 + (sy - cy) ** 2) / 30.0, 0, 1))
    gy, gx = np.gradient(H)
    n = np.dstack([-gx * 2.5, -gy * 2.5, np.ones_like(H)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    return save_image("cymbal_dots_normal", np.dstack([n * 0.5 + 0.5, np.ones_like(H)]), True)

def module_screen_texture(w=512, h=256):
    """LC-Display des Moduls: Kit-Nummer, Tempo, Balken."""
    img = np.zeros((h, w, 4)); img[..., 3] = 1; img[..., 0:3] = (0.02, 0.05, 0.12)
    blue = np.array([0.35, 0.65, 1.0]); white = np.array([0.85, 0.92, 1.0])
    img[h - 60:h - 20, 24:150, 0:3] = blue           # "Kit"-Feld
    img[h - 60:h - 20, 170:300, 0:3] = white * 0.8   # Name
    img[h - 60:h - 20, w - 140:w - 24, 0:3] = blue   # Tempo
    for k in range(8):
        lvl = [120, 90, 150, 60, 110, 140, 80, 100][k]
        img[30:30 + lvl, 30 + k * 58:30 + k * 58 + 34, 0:3] = blue * (0.5 + 0.06 * k)
    return save_image("module_screen", img)

def phone_screen_texture(w=256, h=512):
    """Handy im Halter: allgemeine Musik-App (erfunden)."""
    img = np.zeros((h, w, 4)); img[..., 3] = 1; img[..., 0:3] = (0.06, 0.07, 0.09)
    img[h - 230:h - 40, 20:w - 20, 0:3] = (0.85, 0.42, 0.18)       # Cover
    img[h - 270:h - 250, 20:w - 60, 0:3] = (0.9, 0.9, 0.92)         # Titel
    img[h - 295:h - 282, 20:w - 120, 0:3] = (0.5, 0.52, 0.56)       # Untertitel
    img[150:156, 20:w - 20, 0:3] = (0.25, 0.27, 0.3); img[150:156, 20:140, 0:3] = (0.95, 0.95, 0.95)  # Fortschritt
    for k, x in enumerate((50, 128, 206)):                           # Tasten
        r = 26 if k == 1 else 16
        yy, xx = np.mgrid[0:h, 0:w]
        img[((xx - x) ** 2 + (yy - 90) ** 2) < r * r, 0:3] = (0.95, 0.95, 0.95)
    return save_image("phone_screen", img)

# ---------------------------------------------------------------- Materialien
def emissive(name, color, strength, base=(0.02, 0.02, 0.02), img=None):
    m = material(name, base, rough=0.35)
    b = m.node_tree.nodes["Principled BSDF"]
    setin(b, ["Emission Color", "Emission"], (*color, 1))
    setin(b, ["Emission Strength"], strength)
    if img:
        t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = img; t.location = (-500, -100)
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Emission Color"] if "Emission Color" in b.inputs else b.inputs["Emission"])
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    return m

M_SHELL = material("Shell_Finish", (0.015, 0.015, 0.017), metallic=0.0, rough=0.4)     # Pad-Rahmen: schwarz
M_CHROME = material("Hardware_Metal", (0.018, 0.018, 0.02), metallic=0.3, rough=0.45)   # Rack: schwarz
M_CYM = material("Cymbal_Pad", (0.02, 0.02, 0.022), rough=0.8)                       # Becken: Gummi
_dn = dots_normal()
add_textures(M_CYM, normal_img=_dn, nstrength=1.0)
_mc, _mn = mesh_head_texture()
M_HEAD = material("Drumhead", (0.85, 0.85, 0.84), rough=0.85)                           # Mesh: weiss
add_textures(M_HEAD, color_img=_mc, normal_img=_mn, nstrength=0.5)
M_LED = emissive("LED_Glow", (0.0, 0.0, 0.0), 0.0)                                      # LED-Ring (Standard: aus)
M_SCREEN = emissive("Screen", (1, 1, 1), 0.7, img=module_screen_texture())
M_PHONE = material("Phone_Screen", (0.008, 0.008, 0.01), metallic=0.0, rough=0.06, coat=1.0, coat_rough=0.02)   # Handy aus: schwarzes Glas
M_LOGO = material("Logo", (0.92, 0.92, 0.9), rough=0.45)
M_PRINT = material("Print_Dark", (0.02, 0.02, 0.02), rough=0.5)
M_ALU = material("Pedal_Alu", (0.78, 0.79, 0.8), metallic=1.0, rough=0.24)
M_STEEL = material("Bolt_Steel", (0.85, 0.85, 0.87), metallic=1.0, rough=0.15)
M_BLACK = material("Black_Hardware", (0.02, 0.02, 0.023), metallic=0.3, rough=0.45)
M_RUBBER = material("Rubber", (0.015, 0.015, 0.015), rough=0.85)
M_FELT = material("Felt", (0.88, 0.87, 0.84), rough=1.0)
M_LEATHER = material("Throne_Leather", (0.03, 0.025, 0.025), rough=0.55)
M_STICK = material("Stick_Wood", (0.82, 0.62, 0.38), rough=0.5)

# ---------------------------------------------------------------- Werkzeuge
def sweep(points, r, res=3):
    cu = bpy.data.curves.new("sweep", "CURVE"); cu.dimensions = '3D'
    cu.bevel_depth = r; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    ob = bpy.data.objects.new("tmp", cu); C_HW.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bm = bmesh.new(); bm.loops.layers.uv.new("UVMap"); bm.from_mesh(me)
    for f in bm.faces:
        f.smooth = True
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.curves.remove(cu)
    return bm

def quad(w, h):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new(c) for c in ((-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2))]
    f = bm.faces.new(vs)
    for loop, c in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = c
    if f.normal.y > 0:
        bmesh.ops.reverse_faces(bm, faces=[f])
    return bm

def text_bm(body, size, spacing=1.0):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.extrude = 0.0006
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.space_character = spacing
    ob = bpy.data.objects.new("tmp", cu); C_HW.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bm = bmesh.new(); bm.loops.layers.uv.new("UVMap"); bm.from_mesh(me)
    bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.curves.remove(cu)
    return bm

def ball(mesh, p, r, mat):
    prof = [(0, -r)] + [(r * math.cos(rad(t)), r * math.sin(rad(t))) for t in range(-75, 76, 15)] + [(0, r)]
    mesh.add(lathe(prof, 20), T(p), mat)

grow_keys = []   # (Objekt, Radius) -> Shape Key "Pad_Gross"

# ---------------------------------------------------------------- Pads
def make_pad(name, D, M, depth=0.062, lugs=6):
    R = D / 2
    m = Mesh([M_SHELL, M_LED, M_RUBBER, M_HEAD, M_BLACK, M_STEEL])
    m.add(lathe(tube_prof(R - 0.002, -depth, -0.012, 0.008), 96), mat=0)                                   # Kessel
    m.add(lathe([(R - 0.003, -0.026), (R - 0.0005, -0.026), (R - 0.0005, -0.021), (R - 0.003, -0.021)], 96), mat=1)  # LED-Ring
    hoop = [(R - 0.005, -0.013), (R + 0.010, -0.013), (R + 0.0125, -0.009), (R + 0.0125, 0.010),
            (R + 0.009, 0.0145), (R - 0.002, 0.0145), (R - 0.005, 0.011)]
    m.add(lathe(hoop, 96), mat=0)                                                                           # Spannreifen
    head = [(0, 0.0062), (R * 0.6, 0.0058), (R - 0.004, 0.0048), (R - 0.004, -0.004), (0, -0.004)]
    m.add(lathe(head, 96, planar_R=R * 0.3), mat=3)                                                        # Mesh-Fell
    for k in range(lugs):                                                                                   # Spannschrauben
        a = 2 * math.pi * k / lugs + math.pi / lugs
        RA = Rzr(a)
        m.add(box(0.012, 0.018, 0.034, 0.003), RA @ T(R + 0.004, 0, -0.03), 4)                           # Boeckchen
        m.add(lathe([(0, 0), (0.0052, 0), (0.0052, 0.0045), (0.004, 0.0058), (0, 0.0058)], 16), RA @ T(R + 0.006, 0, 0.0145), 5)
        m.add(lathe(tube_prof(0.0022, -0.026, 0.0), 10), RA @ T(R + 0.006, 0, 0.0145), 5)
    m.add(box(0.06, 0.05, 0.03, 0.006), T(0, 0, -depth - 0.012), 4)                                        # Halter
    m.add(lathe(tube_prof(0.0075, 0, 0.016), 16), T(0, -R * 0.6, -depth) @ Rx(180), 4)                     # Buchse
    ob = m.build(name, C_DRUM, M, 40)
    grow_keys.append((ob, R))
    return ob

def make_cym_pad(name, R, M, coll, zone=True):
    m = Mesh([M_CYM, M_BLACK, M_LED])
    prof = [(0.007, 0.016), (R * 0.17, 0.016), (R * 0.24, 0.006), (R * 0.6, 0.0025), (R - 0.004, 0.0), (R, -0.004),
            (R - 0.004, -0.008), (R * 0.6, -0.0055), (R * 0.24, -0.003), (R * 0.17, 0.006), (0.007, 0.006)]
    m.add(lathe(prof, 96, planar_R=R), mat=0)
    m.add(lathe([(R - 0.0012, -0.0058), (R + 0.0007, -0.0058), (R + 0.0007, -0.0028), (R - 0.0012, -0.0028)], 96), mat=2)
    m.add(lathe(tube_prof(R * 0.5, -0.016, -0.005, 0.002), 64), mat=1)                                   # Sensor-Schale
    ob = m.build(name, coll, M, 40)
    grow_keys.append((ob, R))
    return ob

# ---------------------------------------------------------------- Rohr-Rack
RACK_Z = 0.56; TUBE = 0.019
FL, FR = Vector((-0.34, 0.10, RACK_Z)), Vector((0.34, 0.10, RACK_Z))       # vordere Ecken
BL, BR = Vector((-0.68, -0.40, RACK_Z)), Vector((0.68, -0.40, RACK_Z))     # hintere Enden der Fluegel
RACK_PATH = [BL, FL, FR, BR]

rack = Mesh([M_CHROME, M_RUBBER, M_BLACK])
rack.tube(FL + Vector((-0.04, 0, 0)), FR + Vector((0.04, 0, 0)), TUBE, 0, 24)      # Querstange
for a_, b_ in ((FL, BL), (FR, BR)):
    d = (b_ - a_).normalized()
    rack.tube(a_ - d * 0.03, b_ + d * 0.05, TUBE, 0, 24)                          # Seitenfluegel
for p in (FL, FR, BL, BR):                                                         # Beine
    rack.tube(Vector((p.x, p.y, 0.03)), Vector((p.x, p.y, RACK_Z + 0.11)), 0.0185, 0, 24)
    rack.add(box(0.07, 0.07, 0.075, 0.012), T(p), 2)                               # Eckklemme
    rack.add(lathe([(0, 0), (0.021, 0), (0.022, 0.006), (0.021, 0.02), (0, 0.02)], 20), T(p.x, p.y, RACK_Z + 0.105), 1)  # Kappe
    rack.add(lathe([(0, 0), (0.024, 0), (0.025, 0.005), (0.02, 0.04), (0, 0.04)], 20), T(p.x, p.y, 0.0), 1)              # Fuss
    wingnut(rack, T(p + Vector((0.035, 0, 0))) @ Ry(90), 2)

def rack_point(p):
    """naechster Punkt auf dem Rack (fuer Klemmen und Kabel); gibt Punkt und Weg-Parameter zurueck."""
    best = None; acc = 0.0
    for a_, b_ in zip(RACK_PATH[:-1], RACK_PATH[1:]):
        seg = b_ - a_; L = seg.length
        t = max(0.0, min(1.0, (p - a_).dot(seg) / (L * L)))
        q = a_ + seg * t
        dist = (Vector((p.x, p.y, RACK_Z)) - q).length
        if best is None or dist < best[0]:
            best = (dist, q, acc + t * L)
        acc += L
    return best[1], best[2]

def path_point(s):
    acc = 0.0
    for a_, b_ in zip(RACK_PATH[:-1], RACK_PATH[1:]):
        L = (b_ - a_).length
        if s <= acc + L:
            return a_.lerp(b_, (s - acc) / L)
        acc += L
    return RACK_PATH[-1].copy()

def clamp_on_rack(mesh, q):
    mesh.add(box(0.062, 0.062, 0.06, 0.01), T(q), 2)
    wingnut(mesh, T(q + Vector((0, 0, 0.032))), 2, 1.0)

jacks = []

def place_pad(name, D, center, rx, rz, depth=0.062, attach=None):
    M = T(center) @ Rz(rz) @ Rx(rx)
    ob = make_pad(name, D, M, depth)
    under = M @ Vector((0, 0, -depth - 0.03))
    q, s = rack_point(attach if attach else under)
    clamp_on_rack(rack, q)
    elbow = Vector((q.x, q.y, under.z - 0.04)) if under.z - q.z > 0.12 else q + Vector((0, 0, 0.05))
    rack.tube(q, elbow, 0.0125, 0, 16)
    rack.add(lathe(tube_prof(0.016, -0.02, 0.02), 20), T(elbow), 2)
    rack.tube(elbow, under, 0.0115, 0, 16)
    ball(rack, under, 0.017, 2)
    jacks.append(M @ Vector((0, -D / 2 * 0.6, -depth - 0.016)))
    return ob, M

tom1, _ = place_pad("Tom1_Pad", 8 * INCH, Vector((-0.15, 0.08, 0.80)), 16, 6, attach=Vector((-0.15, 0.10, 0)))
tom2, _ = place_pad("Tom2_Pad", 8 * INCH, Vector((0.15, 0.08, 0.80)), 16, -6, attach=Vector((0.15, 0.10, 0)))
snare, SN_M = place_pad("Snare_Pad", 10 * INCH, Vector((-0.31, -0.33, 0.64)), 8, -14, attach=Vector((-0.50, -0.16, 0)))
tom3, _ = place_pad("Tom3_Pad", 8 * INCH, Vector((0.45, -0.38, 0.60)), 6, 18, attach=Vector((0.56, -0.24, 0)))
rack.build("Rack", C_HW)

# ---------------------------------------------------------------- Kick-Saeule
KICK_Z = 0.30; KICK_Y = -0.02
kick_M = T(0, KICK_Y, KICK_Z) @ Rx(90)
kick_pad = make_pad("Kick_Pad", 6.5 * INCH, kick_M, depth=0.05, lugs=0)
kt = Mesh([M_SHELL, M_BLACK, M_RUBBER, M_ALU])
kt.add(box(0.05, 0.05, 0.30, 0.008), T(0, KICK_Y + 0.07, 0.17), 1)                   # Mittelstrebe
kt.add(box(0.14, 0.03, 0.06, 0.008), T(0, KICK_Y + 0.05, KICK_Z), 1)                 # Halter
for sx in (1, -1):                                                                   # Fuesse + Sporen
    kt.tube(Vector((0, KICK_Y + 0.07, 0.04)), Vector((sx * 0.14, KICK_Y + 0.16, 0.02)), 0.011, 1, 14)
    kt.add(lathe([(0, 0), (0.015, 0), (0.016, 0.004), (0.012, 0.025), (0, 0.025)], 16), T(sx * 0.14, KICK_Y + 0.16, 0.0), 2)
    kt.tube(Vector((sx * 0.06, KICK_Y + 0.06, 0.03)), Vector((sx * 0.10, KICK_Y - 0.03, 0.01)), 0.009, 1, 14)
kt.add(box(0.16, 0.12, 0.012, 0.004), T(0, KICK_Y + 0.02, 0.006), 1)                  # Bodenplatte
kick_tower = kt.build("Kick_Turm", C_DRUM)
jacks.append(Vector((0.03, KICK_Y + 0.09, 0.12)))

# ---------------------------------------------------------------- Becken-Pads (Crash und Ride an Pfosten)
def rack_cymbal(name, base, top_z, target, R, tilt):
    lower = Mesh([M_CHROME, M_RUBBER, M_BLACK])
    clamp_on_rack(lower, base)
    lower.tube(base, base + Vector((0, 0, 0.30)), 0.0145, 0, 18)
    lower.add(lathe(tube_prof(0.018, -0.016, 0.016), 24), T(base + Vector((0, 0, 0.30))), 2)
    lower.build(f"{name}_Pfosten_Unten", C_HW)
    upper = Mesh([M_CHROME, M_RUBBER, M_BLACK])
    piv = Vector((base.x, base.y, top_z))
    upper.tube(base + Vector((0, 0, 0.22)), piv - Vector((0, 0, 0.02)), 0.0115, 0, 18)
    upper.add(box(0.036, 0.036, 0.045, 0.008), T(piv), 2)
    ob_upper = upper.build(f"{name}_Pfosten_Oben", C_HW)
    d = target - piv
    boom = Mesh([M_CHROME, M_RUBBER, M_FELT])
    boom.tube(piv - d.normalized() * 0.06, target, 0.0095, 0, 18)
    hd = math.degrees(math.atan2(d.y, d.x))
    cymM = T(target + Vector((0, 0, 0.022))) @ Rz(hd - 90) @ Rx(tilt)
    boom.add(lathe(tube_prof(0.006, -0.03, 0.03), 12), cymM, 0)
    boom.add(lathe([(0, 0), (0.012, 0), (0.012, 0.022), (0.006, 0.03), (0, 0.03)], 20), cymM @ T(0, 0, 0.016), 1)   # Fluegelkappe
    ob_boom = boom.build(f"{name}_Galgen", C_HW)
    cym = make_cym_pad(f"{name}_Cymbal", R, cymM, C_CYM)
    rig_bones.append((f"{name}_Hoehe", base + Vector((0, 0, 0.30)), piv.copy(), None, [ob_upper]))
    rig_bones.append((f"{name}_Neigung", piv.copy(), piv + d.normalized() * 0.1, f"{name}_Hoehe", [ob_boom, cym]))
    jacks.append(cymM @ Vector((0, -R * 0.3, -0.02)))
    return cym

crash = rack_cymbal("Crash", Vector((-0.04, 0.10, RACK_Z)), 1.06, Vector((-0.02, 0.30, 1.12)), 12 * INCH / 2, 8)
ride = rack_cymbal("Ride", Vector((0.50, -0.15, RACK_Z)), 0.96, Vector((0.56, 0.06, 0.98)), 12 * INCH / 2, 10)

# ---------------------------------------------------------------- Hi-Hat-Pad am Rack + Controller-Pedal
hh_base = path_point(0.46)                     # auf dem linken Fluegel
HH_C = Vector((-0.57, 0.03, 0.92))
hhm = Mesh([M_CHROME, M_RUBBER, M_BLACK])
clamp_on_rack(hhm, hh_base)
hhm.tube(hh_base, Vector((hh_base.x, hh_base.y, 0.84)), 0.0125, 0, 16)
hhm.add(lathe(tube_prof(0.016, -0.02, 0.02), 20), T(hh_base.x, hh_base.y, 0.84), 2)
hhm.tube(Vector((hh_base.x, hh_base.y, 0.84)), HH_C - Vector((0, 0, 0.03)), 0.0105, 0, 16)
hhm.build("HiHat_Arm", C_HW)
HH_TOP_Z = HH_C.z
hh_top = make_cym_pad("HiHat_Top", 10 * INCH / 2, T(HH_C) @ Rx(6), C_CYM)
hhr = Mesh([M_CHROME, M_FELT, M_BLACK])
hhr.add(lathe(tube_prof(0.006, -0.035, 0.03), 12), T(HH_C) @ Rx(6), 0)
hhr.add(lathe([(0, 0), (0.012, 0), (0.012, 0.022), (0.006, 0.03), (0, 0.03)], 20), T(HH_C) @ Rx(6) @ T(0, 0, 0.016), 2)
ob_hh_rod = hhr.build("HiHat_Stange_Clutch", C_HW)
jacks.append(HH_C + Vector((0, -0.05, -0.03)))
# Controller-Pedal am Boden
HH_PED_PIV = Vector((-0.40, -0.68, 0.028))
hhb = Mesh([M_BLACK, M_ALU, M_RUBBER])
hhb.add(box(0.095, 0.30, 0.016, 0.005), T(HH_PED_PIV.x, HH_PED_PIV.y + 0.13, 0.008), 0)
hhb.add(box(0.07, 0.06, 0.05, 0.01), T(HH_PED_PIV.x, HH_PED_PIV.y + 0.255, 0.035), 0)
hhb.build("HiHat_Controller", C_HW)
hhp = Mesh([M_ALU, M_PRINT, M_RUBBER])
hhp.add(box(0.078, 0.25, 0.009, 0.003), T(0, 0.125, 0), 0)
for k in range(3):
    hhp.add(box(0.05, 0.004, 0.003, 0.001), T(0, 0.205 + k * 0.012, 0.005), 1)
ob_hh_ped = hhp.build("HiHat_Pedal_Mesh", C_HW, T(HH_PED_PIV) @ Rx(9))
rig_bones.append(("HiHat_Offen", HH_C.copy(), HH_C + Vector((0, 0, 0.1)), None, [hh_top, ob_hh_rod]))
rig_bones.append(("HiHat_Pedal", HH_PED_PIV.copy(), HH_PED_PIV + Vector((0, 0.1, 0.018)), None, [ob_hh_ped]))
jacks.append(Vector((HH_PED_PIV.x, HH_PED_PIV.y + 0.29, 0.04)))

# ---------------------------------------------------------------- Fussmaschine (Alu)
front_y = KICK_Y - 0.05
KP_Y = front_y - 0.04
kp = Mesh([M_ALU, M_BLACK, M_RUBBER, M_STEEL])
kp.add(box(0.12, 0.40, 0.006, 0.002), T(0, KP_Y - 0.20, 0.003), 1)
for sx in (1, -1):
    kp.add(box(0.016, 0.026, 0.17, 0.004), T(sx * 0.058, KP_Y, 0.09), 0)
    kp.add(lathe(tube_prof(0.013, -0.008, 0.008), 20), T(sx * 0.058, KP_Y, 0.165) @ Ry(90), 0)
kp.add(lathe(tube_prof(0.005, -0.065, 0.065), 16), T(0, KP_Y, 0.165) @ Ry(90), 3)
kp.add(box(0.13, 0.03, 0.014, 0.004), T(0, KP_Y + 0.004, 0.012), 0)
kp.add(lathe(tube_prof(0.026, -0.0045, 0.0045), 32), T(0.03, KP_Y, 0.165) @ Ry(90), 0)
kp.add(box(0.012, 0.004, 0.085, 0.001), T(0.03, KP_Y - 0.027, 0.12), 1)
kp.add(sweep([Vector((0.077 + 0.0065 * math.cos(2 * math.pi * 13 * i / 156), KP_Y + 0.0065 * math.sin(2 * math.pi * 13 * i / 156), 0.03 + 0.10 * i / 156)) for i in range(157)], 0.0013, 2), mat=3)
kp.tube((0.077, KP_Y, 0.13), (0.077, KP_Y, 0.165), 0.0025, 3, 10)
kp.build("Fussmaschine_Rahmen", C_HW)
KP_PIV = Vector((0, KP_Y, 0.165))
beat = Mesh([M_STEEL, M_FELT, M_BLACK])
beat.add(lathe(tube_prof(0.0035, 0, 0.17), 12), Matrix(), 0)
beat.add(lathe([(0, -0.018), (0.026, -0.018), (0.03, -0.012), (0.03, 0.012), (0.026, 0.018), (0, 0.018)], 32), T(0, 0, 0.17) @ Rx(90), 2)
ob_beater = beat.build("Fussmaschine_Schlaegel_Mesh", C_HW, T(KP_PIV) @ Rx(22))
fb = Mesh([M_ALU, M_PRINT])
fb.add(box(0.078, 0.29, 0.009, 0.003), T(0, 0.145, 0), 0)
for k in range(4):
    fb.add(box(0.054, 0.004, 0.003, 0.001), T(0, 0.235 + k * 0.012, 0.005), 1)
KP_HEEL = Vector((0, KP_Y - 0.335, 0.022))
ob_footb = fb.build("Fussmaschine_Trittbrett_Mesh", C_HW, T(KP_HEEL) @ Rx(13))
kp2 = Mesh([M_ALU]); kp2.add(box(0.08, 0.075, 0.016, 0.004), T(0, KP_HEEL.y - 0.03, 0.011), 0)
kp2.build("Fussmaschine_Fersenplatte", C_HW)
rig_bones.append(("Fussmaschine_Schlaegel", KP_PIV.copy(), KP_PIV + Vector((0, -0.04, 0.1)), None, [ob_beater]))
rig_bones.append(("Fussmaschine_Trittbrett", KP_HEEL.copy(), KP_HEEL + Vector((0, 0.1, 0.02)), None, [ob_footb]))

# ---------------------------------------------------------------- Modul mit Handyhalter
mod_q = path_point(0.12)                       # weit hinten auf dem linken Fluegel
MOD_M = T(mod_q.x + 0.02, mod_q.y + 0.10, 0.76) @ Rz(36) @ Rx(-38)
mod = Mesh([M_BLACK, M_SCREEN, M_LOGO, M_RUBBER, M_PHONE, M_STEEL])
mod.add(box(0.22, 0.035, 0.15, 0.01, 3), Matrix(), 0)
mod.add(quad(0.09, 0.045), T(-0.04, -0.0179, 0.03), 1)
for k in range(2):                                                         # grosse Tasten
    mod.add(lathe([(0, 0), (0.011, 0), (0.011, 0.004), (0, 0.004)], 24), T(-0.075 + k * 0.035, -0.0175, -0.045) @ Rx(90), 3)
mod.add(lathe([(0, 0), (0.017, 0), (0.0175, 0.006), (0.016, 0.012), (0, 0.012)], 32), T(0.06, -0.0175, 0.015) @ Rx(90), 3)  # Drehrad
for r_ in range(3):
    for c_ in range(4):
        mod.add(box(0.014, 0.004, 0.009, 0.0015), T(0.02 + c_ * 0.02, -0.019, -0.03 - r_ * 0.016), 3)
# Handyhalter hinter dem Modul (Schlitz) + Handy
mod.add(box(0.15, 0.03, 0.02, 0.005), T(0, 0.005, 0.085), 0)
PH = T(0, -0.002, 0.15) @ Rx(-8)
mod.add(box(0.075, 0.008, 0.155, 0.009, 3), PH, 0)
mod.add(quad(0.068, 0.146), PH @ T(0, -0.0042, 0), 4)
ob_mod = mod.build("Modul", C_HW, MOD_M, 30)
mm = Mesh([M_CHROME, M_RUBBER, M_BLACK])
clamp_on_rack(mm, mod_q)
mod_back = MOD_M @ Vector((0, 0.03, -0.03))
mm.tube(mod_q, Vector((mod_q.x, mod_q.y, mod_back.z - 0.05)), 0.0125, 0, 16)
mm.tube(Vector((mod_q.x, mod_q.y, mod_back.z - 0.05)), mod_back, 0.011, 0, 16)
ball(mm, mod_back, 0.016, 2)
mm.build("Modul_Halter", C_HW)

# ---------------------------------------------------------------- Hocker
TH = Vector((0, -0.84))
th = Mesh([M_CHROME, M_RUBBER, M_BLACK])
tripod(th, TH, leg_r=0.27)
th.tube((TH.x, TH.y, 0.06), (TH.x, TH.y, 0.40), 0.016, 0, 20)
joint_clamp(th, TH.x, TH.y, 0.37, 0.022)
th.add(box(0.22, 0.22, 0.02, 0.005), T(TH.x, TH.y, 0.425), 2)
th.build("Hocker_Gestell", C_HW)
seat = Mesh([M_LEATHER, M_BLACK])
sp_ = [(0, 0.43), (0.15, 0.43), (0.168, 0.44), (0.176, 0.462), (0.174, 0.495), (0.162, 0.512), (0.12, 0.521), (0, 0.523)]
seat.add(lathe(sp_, 64), T(TH.x, TH.y, 0), 0)
seat.add(lathe(torus_prof(0.1765, 0.0035, 8), 64), T(TH.x, TH.y, 0.468), 1)
seat.build("Hocker_Sitz", C_HW, smooth_angle=60)

# ---------------------------------------------------------------- Sticks (auf dem Snare-Pad)
def stick_bm():
    p = [(0, 0), (0.0062, 0.0008), (0.0072, 0.006), (0.0072, 0.27), (0.0052, 0.36), (0.0036, 0.392),
         (0.0045, 0.396), (0.0048, 0.4), (0.0042, 0.404), (0.002, 0.4065), (0, 0.407)]
    return lathe(p, 20)
sticks = Mesh([M_STICK])
R_sn = 10 * INCH / 2
for off in (-0.018, 0.018):
    a = rad(30)
    dirv = Vector((-math.cos(a), -math.sin(a), 0)); dirv.rotate(Matrix.Rotation(rad(-10), 3, 'Z'))
    tang = Vector((-dirv.y, dirv.x, 0))
    p_rim = Vector((math.cos(a), math.sin(a), 0)) * (R_sn + 0.004) + tang * off
    p_rim.z = 0.0145 + 0.0072
    p_tip = p_rim + dirv * 0.26; p_tip.z = 0.0062 + 0.0072
    d = (p_tip - p_rim).normalized()
    butt = p_rim - d * 0.13
    M_, _ = orient(butt, butt + d)
    sticks.add(stick_bm(), SN_M @ M_, 0)
sticks.build("Sticks", C_HW, smooth_angle=60)

# ---------------------------------------------------------------- EXTRAS
# zweites Crash-Pad am rechten vorderen Bein
exa = Mesh([M_CHROME, M_RUBBER, M_FELT, M_BLACK])
eb = FR + Vector((0, 0, 0.11))
ex_t = Vector((0.30, 0.30, 1.10))
exa.add(lathe(tube_prof(0.02, -0.02, 0.02), 20), T(eb), 3)
exa.tube(eb, Vector((eb.x, eb.y, 1.0)), 0.0125, 0, 16)
exa.add(box(0.034, 0.034, 0.04, 0.008), T(eb.x, eb.y, 1.0), 3)
exa.tube(Vector((eb.x, eb.y, 1.0)), ex_t, 0.009, 0, 16)
exM = T(ex_t + Vector((0, 0, 0.022))) @ Rz(180) @ Rx(10)
exa.add(lathe(tube_prof(0.006, -0.03, 0.03), 12), exM, 0)
exa.add(lathe([(0, 0), (0.012, 0), (0.012, 0.022), (0.006, 0.03), (0, 0.03)], 20), exM @ T(0, 0, 0.016), 1)
exa.build("Extra_Crash2_Arm", C_EXTRA)
make_cym_pad("Extra_Crash2_Cymbal", 10 * INCH / 2, exM, C_EXTRA)

# Kabelbaum: von jeder Buchse zum Rack, am Rohr entlang zum Modul
cab = Mesh([M_RUBBER, M_BLACK])
mod_in = MOD_M @ Vector((0.05, 0.015, -0.077))
_, s_mod = rack_point(mod_q)
for k, jp in enumerate(jacks):
    q, s = rack_point(jp)
    z_run = RACK_Z - TUBE - 0.004 - 0.003 * (k % 4)
    pts = [jp, jp + Vector((0, 0, -0.04)), Vector((q.x, q.y, z_run))]
    steps = max(2, int(abs(s - s_mod) / 0.06))
    for i in range(1, steps + 1):
        pp = path_point(s + (s_mod - s) * i / steps)
        sag = 0.015 if i % 3 == 1 else 0.0
        pts.append(Vector((pp.x, pp.y, z_run - sag)))
    pts.append(Vector((mod_q.x, mod_q.y, 0.66)))
    pts.append(mod_in + Vector((0.004 * k - 0.02, 0, -0.005)))
    for _ in range(2):
        sm = [pts[0]]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            sm += [a_.lerp(b_, 0.25), a_.lerp(b_, 0.75)]
        sm.append(pts[-1]); pts = sm
    cab.add(sweep(pts, 0.0028, 2), mat=0)
    cab.add(lathe(tube_prof(0.0055, 0, 0.02), 12), orient(jp + Vector((0, 0, -0.02)), jp)[0], 1)
cab.build("Extra_Kabel", C_EXTRA, smooth_angle=60)

# =====================================================================
#  SHAPE KEYS (Morph Targets)
# =====================================================================
# 1) Pad_Gross: alle Pads und Becken 25 % groesser (z. B. 8" -> 10")
for ob, R in grow_keys:
    def grow(co, R=R):
        r = math.hypot(co.x, co.y)
        w = min(1.0, max(0.0, (r - 0.035) / 0.04))
        f = 1 + 0.25 * w
        return Vector((co.x * f, co.y * f, co.z))
    shape_key(ob, "Pad_Gross", grow)

# 2) Kick_Gross: Kick-Pad hoeher und groesser
_lift = kick_M.inverted().to_3x3() @ Vector((0, 0, 0.05))
shape_key(kick_pad, "Kick_Gross", lambda co: Vector((co.x * 1.3, co.y * 1.3, co.z)) + _lift)
shape_key(kick_tower, "Kick_Gross", lambda co: Vector((co.x, co.y, co.z + 0.05)) if co.z > 0.2 else (Vector((co.x, co.y, co.z + (co.z - 0.05) / 0.15 * 0.05)) if co.z > 0.05 else co))

# =====================================================================
#  ARMATURE (Bones)
# =====================================================================
arm_data = bpy.data.armatures.new("Drum_Rig")
arm = bpy.data.objects.new("Drum_Rig", arm_data); C_RIG.objects.link(arm)
arm_data.display_type = 'STICK'
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
for (bn, head, tail, parent, _) in rig_bones:
    eb = arm_data.edit_bones.new(bn); eb.head = head; eb.tail = tail
    if parent:
        eb.parent = arm_data.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
for (bn, head, tail, parent, obs) in rig_bones:
    b = arm_data.bones[bn]
    pm = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    for ob in obs:
        mw = ob.matrix_world.copy()
        ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = bn
        ob.matrix_parent_inverse = pm.inverted()
        ob.matrix_basis = mw

# =====================================================================
#  RENDER-SETUP (Boden, Licht, Kameras)
# =====================================================================
M_FLOOR = material("Render_Boden", (0.06, 0.045, 0.035), rough=0.55)
nt = M_FLOOR.node_tree; b = nt.nodes["Principled BSDF"]
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3.0
wv.inputs["Distortion"].default_value = 6.0; wv.bands_direction = 'X'
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = 0.6; mr.inputs[4].default_value = 1.0
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
mix.inputs["Factor"].default_value = 1.0; mix.inputs[6].default_value = (0.20, 0.12, 0.07, 1)
nt.links.new(wv.outputs["Fac"], mr.inputs[0]); nt.links.new(mr.outputs[0], mix.inputs[7])
nt.links.new(mix.outputs[2], b.inputs["Base Color"])
M_RUG = material("Render_Teppich", (0.5, 0.5, 0.5), rough=0.95)
M_WALL = material("Render_Wand", (0.45, 0.45, 0.46), rough=0.85)

Mesh([M_FLOOR]).add(box(8, 8, 0.02), T(0, 0, -0.0105)).build("Boden", C_RENDER)
Mesh([M_RUG]).add(box(2.3, 2.1, 0.008, 0.003), T(0, -0.22, -0.004)).build("Teppich", C_RENDER)
wall_bm = lathe([(5.0, -0.1), (5.05, -0.1), (5.05, 5), (5.0, 5)], 96)
Mesh([M_WALL]).add(wall_bm).build("Hintergrund", C_RENDER)

world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.05, 0.055, 0.065, 1); bg.inputs[1].default_value = 0.6

def light(name, kind, loc, target, energy, color=(1, 1, 1), size=1.0, spot=None):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == 'AREA':
        ld.shape = 'DISK'; ld.size = size
    if kind == 'SPOT':
        ld.spot_size = rad(spot or 40); ld.spot_blend = 0.4; ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld); C_RENDER.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob

studio = [
    light("Key_Studio", 'AREA', (2.4, 2.2, 2.8), (0, -0.1, 0.6), 900, (1.0, 0.95, 0.88), 2.2),
    light("Fill_Studio", 'AREA', (-2.6, 1.2, 1.8), (0, 0, 0.6), 350, (0.85, 0.9, 1.0), 2.5),
    light("Rim_Studio", 'AREA', (0.3, -2.6, 2.6), (0, 0, 0.8), 600, (1, 1, 1), 1.5),
    light("Top_Studio", 'AREA', (0, 0, 3.2), (0, 0, 0), 400, (1, 1, 1), 3.0),
]
stage = [
    light("Spot_Magenta", 'SPOT', (-2.2, 1.8, 3.2), (0, 0, 0.7), 2500, (1.0, 0.15, 0.6), 0.15, 45),
    light("Spot_Cyan", 'SPOT', (2.4, 1.6, 3.0), (0, 0, 0.7), 2500, (0.1, 0.6, 1.0), 0.15, 45),
    light("Spot_Warm_Top", 'SPOT', (0.2, -0.6, 3.6), (0, 0.0, 0.6), 1800, (1.0, 0.75, 0.45), 0.2, 50),
    light("Spot_Front", 'SPOT', (0.0, 3.2, 1.6), (0, 0, 0.7), 600, (1.0, 0.9, 0.8), 0.3, 35),
]

def camera(name, loc, target, lens=35, fstop=None, focus=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = (Vector(focus or target) - Vector(loc)).length
    ob = bpy.data.objects.new(name, cd); C_RENDER.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return ob

cam_all = camera("Cam_Gesamt", (0.0, -1.8, 2.2), (0.0, -0.02, 0.6), 32)
cam_det = camera("Cam_Detail", (-0.66, -0.80, 0.90), (-0.31, -0.33, 0.65), 58, 2.8, (-0.33, -0.38, 0.66))
cam_stage = camera("Cam_Buehne", (-1.6, 1.9, 1.3), (0.0, -0.2, 0.62), 34)
scene.camera = cam_all

r = scene.render
r.engine = 'CYCLES'; scene.cycles.device = 'CPU'
r.resolution_x, r.resolution_y = 1920, 1080
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.sample_clamp_indirect = 2.5
looks = [i.identifier for i in scene.view_settings.bl_rna.properties['look'].enum_items]
scene.view_settings.look = 'AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in looks else 'None'

for o in stage:
    o.hide_render = o.hide_viewport = True

# ---------------------------------------------------------------- Speichern
stats = sum(len(o.data.polygons) for o in scene.objects if o.type == 'MESH' and C_RENDER not in o.users_collection)
print("POLYGONE (ohne Render-Setup):", stats)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "edrum_e8.blend"), compress=True)
print("SAVED")
