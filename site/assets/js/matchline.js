/* Whatta Match Media — the Match Line
   One continuous 3D line built on the logo wave. It draws itself on load and flows like a ribbon.
   In "That moment is the match" it breaks into a W (your brand) and an M (your people) that drift
   apart and then lock back together into the wave. Through Services it redraws itself, like a pen,
   into a clear symbol for each discipline.
   Requires three.js r128 (global THREE). Without WebGL the static SVG wave shows instead. */
(function () {
  "use strict";
  var canvas = document.getElementById("gl");
  if (!canvas || !window.THREE) return;
  var THREE = window.THREE;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  } catch (e) { return; }
  if (!renderer || !renderer.getContext()) return;
  document.documentElement.classList.add("has-gl");

  var mobile = window.innerWidth < 900;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.setClearColor(0x000000, 0);

  var scene = new THREE.Scene();
  var FOV = 35, CAMZ = 12;
  var camera = new THREE.PerspectiveCamera(FOV, 1, 0.1, 100);
  camera.position.set(0, 0, CAMZ);
  var HALF_H = Math.tan((FOV / 2) * Math.PI / 180) * CAMZ;   // visible half-height at z = 0

  scene.add(new THREE.HemisphereLight(0xfff4e6, 0x2a3f66, 1.0));
  var key = new THREE.DirectionalLight(0xffffff, 0.85); key.position.set(-4, 6, 8); scene.add(key);
  var rim = new THREE.DirectionalLight(0x9fb8e8, 0.5); rim.position.set(5, -2, -6); scene.add(rim);
  var warm = new THREE.PointLight(0xff8a3d, 0.3, 30); warm.position.set(3, -3, 6); scene.add(warm);

  var AMBER = new THREE.Color("#FF8A3D").convertSRGBToLinear();
  var ORANGE = new THREE.Color("#FF5F1F").convertSRGBToLinear();

  /* ---------- Geometry ---------- */
  var M = mobile ? 360 : 520;        // rings along the line
  var RAD = mobile ? 16 : 24;        // vertices around each ring
  var L = M - 1;
  var S = 6 / 280;                   // logo units to world units (the wave is 6 wide)
  var RADIUS = 11 * S;               // tube radius for the service icons
  var WAVE_R = 16 * S;               // the wave keeps the logo's own stroke weight (32 of 280)
  var H = 60 * S;                    // half the wave's height

  function V(x, y, z) { return [x, y, z || 0]; }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], (a[2] || 0) - (b[2] || 0)]; }
  function len(a) { return Math.hypot(a[0], a[1], a[2] || 0); }
  function nrm(a) { var l = len(a) || 1; return [a[0] / l, a[1] / l, (a[2] || 0) / l]; }

  function densify(pts, step) {
    var out = [];
    for (var i = 0; i < pts.length - 1; i++) {
      var a = pts[i], b = pts[i + 1], n = Math.max(1, Math.ceil(len(sub(b, a)) / step));
      for (var j = 0; j < n; j++) { var t = j / n; out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (a[2] || 0) + ((b[2] || 0) - (a[2] || 0)) * t]); }
    }
    var e = pts[pts.length - 1]; out.push([e[0], e[1], e[2] || 0]);
    return out;
  }
  // n evenly spaced points by arc length, written into out at ring offset off
  function resampleTo(pts, n, out, off) {
    var cum = [0];
    for (var i = 1; i < pts.length; i++) cum.push(cum[i - 1] + len(sub(pts[i], pts[i - 1])));
    var T = cum[cum.length - 1], j = 0;
    for (var k = 0; k < n; k++) {
      var s = (k / (n - 1)) * T;
      while (j < cum.length - 2 && cum[j + 1] < s) j++;
      var seg = cum[j + 1] - cum[j] || 1, t = Math.min(1, (s - cum[j]) / seg), a = pts[j], b = pts[j + 1], o = (off + k) * 3;
      out[o] = a[0] + (b[0] - a[0]) * t; out[o + 1] = a[1] + (b[1] - a[1]) * t; out[o + 2] = a[2] + (b[2] - a[2]) * t;
    }
  }
  function pathLen(p) { var s = 0; for (var i = 1; i < p.length; i++) s += len(sub(p[i], p[i - 1])); return s; }
  // A shape is one or more pieces of line sharing the M rings in proportion to their length.
  // Between pieces is a "break": no tube is drawn across it, and each side gets a round end.
  function shape(pieces, counts) {
    var p = new Float32Array(M * 3), br = [], off = 0;
    pieces = pieces.map(function (pc) { return densify(pc, 0.01); });
    if (!counts) {
      var ls = pieces.map(pathLen), tot = ls.reduce(function (a, b) { return a + b; }, 0), used = 0;
      counts = [];
      for (var i = 0; i < pieces.length; i++) { var c = i === pieces.length - 1 ? M - used : Math.round(M * ls[i] / tot); counts.push(c); used += c; }
    }
    for (var q = 0; q < pieces.length; q++) {
      resampleTo(pieces[q], counts[q], p, off);
      off += counts[q]; if (q < pieces.length - 1) br.push(off);
    }
    return { p: p, br: br };
  }
  // Straight edges joined by true circular arcs (radius shrinks only if an edge is too short)
  function fillet(c, rho) {
    var out = [c[0]];
    for (var i = 1; i < c.length - 1; i++) {
      var a = c[i - 1], b = c[i], d = c[i + 1];
      var u1 = nrm(sub(a, b)), u2 = nrm(sub(d, b));
      var phi = Math.acos(Math.max(-1, Math.min(1, u1[0] * u2[0] + u1[1] * u2[1])));
      if (phi > Math.PI - 0.01) { out.push(b); continue; }
      var td = rho / Math.tan(phi / 2), lim = Math.min(len(sub(a, b)), len(sub(d, b))) * 0.48;
      if (td > lim) td = lim;
      var r = td * Math.tan(phi / 2);
      var bis = nrm([u1[0] + u2[0], u1[1] + u2[1], 0]), cd = r / Math.sin(phi / 2);
      var cx = b[0] + bis[0] * cd, cy = b[1] + bis[1] * cd;
      var p1 = [b[0] + u1[0] * td, b[1] + u1[1] * td], p2 = [b[0] + u2[0] * td, b[1] + u2[1] * td];
      var a1 = Math.atan2(p1[1] - cy, p1[0] - cx), a2 = Math.atan2(p2[1] - cy, p2[0] - cx), da = a2 - a1;
      while (da > Math.PI) da -= Math.PI * 2; while (da < -Math.PI) da += Math.PI * 2;
      var n = Math.max(6, Math.ceil(Math.abs(da) * r / 0.01));
      for (var k = 0; k <= n; k++) { var an = a1 + da * k / n; out.push([cx + Math.cos(an) * r, cy + Math.sin(an) * r, b[2] || 0]); }
    }
    out.push(c[c.length - 1]);
    return out;
  }
  function arc(cx, cy, r, a0, a1) {
    var out = [], n = Math.max(8, Math.ceil(Math.abs(a1 - a0) * r / 0.01));
    for (var k = 0; k <= n; k++) { var an = a0 + (a1 - a0) * k / n; out.push([cx + Math.cos(an) * r, cy + Math.sin(an) * r, 0]); }
    return out;
  }
  function move(pts, dx, dy, dz, rot) {
    var c = Math.cos(rot), s = Math.sin(rot);
    return pts.map(function (p) { return [p[0] * c - p[1] * s + dx, p[0] * s + p[1] * c + dy, (p[2] || 0) + dz]; });
  }

  /* ---------- The wave: the exact logo path ----------
     M0,0 C20,0 20,120 40,120 C60,120 60,0 80,0 ... 280,120 (seven strokes).
     logo(u0, u1) traces it from stroke-position u0 to u1 (0 to 7). */
  function logo(u0, u1) {
    var pts = [], n = Math.ceil((u1 - u0) * 400);
    for (var k = 0; k <= n; k++) {
      var u = u0 + (u1 - u0) * k / n, sg = Math.min(6, Math.floor(u)), t = u - sg, m = 1 - t;
      var x0 = sg * 40, y0 = sg % 2 === 0 ? 0 : 120, y1 = 120 - y0;
      var x = m * m * m * x0 + 3 * m * m * t * (x0 + 20) + 3 * m * t * t * (x0 + 20) + t * t * t * (x0 + 40);
      var y = m * m * m * y0 + 3 * m * m * t * y0 + 3 * m * t * t * y1 + t * t * t * y1;
      pts.push([(x - 140) * S, -(y - 60) * S, 0]);
    }
    return pts;
  }
  var KH = Math.round(M / 2), HALVES = [KH, M - KH];

  /* ---------- The shapes (each about 4 units across) ---------- */
  // 0 · the wave, as two halves that meet seamlessly in the middle of the fourth stroke
  var WAVE = shape([logo(0.07, 3.5), logo(3.5, 6.93)], HALVES);   // ends start just inside the tips, under the round caps
  // 7 · the break: the W (your brand, strokes 1 to 4) and the M (your people, strokes 4 to 7), apart
  var WM = shape([
    move(logo(0.07, 4), -1.0, 0.08, 0.3, 0.08),
    move(logo(3, 6.93), 1.0, -0.08, -0.3, -0.08)
  ], HALVES);
  // 1 · Brand Strategy: a target. The line spirals in to the bullseye
  function target() {
    var pts = [];
    for (var k = 0; k <= 1600; k++) {
      var t = k / 1600, a = Math.PI * 0.75 - t * Math.PI * 2 * 2.1, r = 1.95 - t * 1.4;
      pts.push([Math.cos(a) * r, Math.sin(a) * r, Math.sin(t * Math.PI) * 0.18]);
    }
    return shape([pts]);
  }
  // Brand Identity & Design: a four-point star, the mark of something distinctive
  function sparkle() {
    var T = 2.15, m = 0.62, c = [];
    for (var k = 0; k < 4; k++) {
      var a = Math.PI / 2 + k * Math.PI / 2, d = a + Math.PI / 4;
      c.push([Math.cos(a) * T, Math.sin(a) * T * 1.04, 0.06]);
      c.push([Math.cos(d) * m, Math.sin(d) * m, -0.06]);
    }
    var t0 = c[0], m0 = c[1], start = [(t0[0] + m0[0]) / 2, (t0[1] + m0[1]) / 2, 0];
    var loop = [start].concat(c.slice(1), [c[0]], [[start[0] + 0.001, start[1], 0]]);
    return shape([fillet(loop, 0.26)]);
  }
  // Consulting: a compass. The ring, then the needle that sets the direction
  function compass() {
    var ring = [];
    for (var k = 0; k <= 1200; k++) { var a = -Math.PI / 2 + k / 1200 * Math.PI * 2; ring.push([Math.cos(a) * 1.95, Math.sin(a) * 1.95, 0]); }
    var t = 0.62, ca = Math.cos(t), sa = Math.sin(t);
    function N(u, v) { return [u * -sa + v * ca, u * ca + v * sa, 0.12]; }
    var needle = fillet([N(0, 0.42), N(1.5, 0), N(0, -0.42), N(-1.5, 0), N(0, 0.4199)], 0.27);
    return shape([ring, needle]);
  }
  // 3 · Content & Creative: a play button
  function play() {
    return shape([fillet([V(-1.3, 0), V(-1.3, 1.95), V(2.05, 0), V(-1.3, -1.95), V(-1.3, 0.001)], 0.55)]);
  }
  // 4 · Social & Influence: a speech bubble
  function bubble() {
    return shape([fillet([V(-1.6, -2.05), V(-0.95, -1.05), V(2.1, -1.05), V(2.1, 1.75), V(-2.1, 1.75), V(-2.1, -1.05), V(-1.3, -1.05)], 0.5)]);
  }
  // 5 · Performance & Growth: a rising line and its arrowhead
  function growth() {
    var tip = [1.85, 1.45], dir = nrm(sub(V(1.85, 1.45), V(-0.15, -0.95)));
    function rot(v, a) { return [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a)]; }
    var b1 = rot([-dir[0], -dir[1]], 0.66), b2 = rot([-dir[0], -dir[1]], -0.66);
    var stem = fillet([V(-2.25, -1.75), V(-0.95, -0.3), V(-0.15, -0.95), V(tip[0] - dir[0] * 0.3, tip[1] - dir[1] * 0.3)], 0.45);
    var head = fillet([V(tip[0] + b1[0] * 1.15, tip[1] + b1[1] * 1.15), V(tip[0], tip[1]), V(tip[0] + b2[0] * 1.15, tip[1] + b2[1] * 1.15)], 0.3);
    return shape([stem, head]);
  }
  // 6 · Media & Digital Experiences: a laptop
  function laptop() {
    var screen = fillet([V(0, -0.85), V(2.05, -0.85), V(2.05, 1.85), V(-2.05, 1.85), V(-2.05, -0.85), V(0.001, -0.85)], 0.4);
    var base = fillet([V(-2.75, -1.3), V(-2.35, -1.72), V(2.35, -1.72), V(2.75, -1.3)], 0.35);
    return shape([screen, base]);
  }
  var BREAKSHAPE = 8;
  var SHAPES = [WAVE, compass(), target(), sparkle(), play(), bubble(), growth(), laptop(), WM];

  /* ---------- Tube mesh, rebuilt in place from the centre line ---------- */
  var pos = new Float32Array(M * RAD * 3), nor = new Float32Array(M * RAD * 3), col = new Float32Array(M * RAD * 3);
  var idx = [];
  for (var i = 0; i < M - 1; i++) for (var j = 0; j < RAD; j++) {
    var a = i * RAD + j, b = (i + 1) * RAD + j, c = (i + 1) * RAD + (j + 1) % RAD, d = i * RAD + (j + 1) % RAD;
    idx.push(a, d, b, b, d, c);   // counter-clockwise from outside, so the outer wall faces the camera
  }
  var ringCol = [];
  (function () {
    for (var i = 0; i < M; i++) {
      var cc = AMBER.clone().lerp(ORANGE, i / L); ringCol.push(cc);
      for (var j = 0; j < RAD; j++) { var o = (i * RAD + j) * 3; col[o] = cc.r; col[o + 1] = cc.g; col[o + 2] = cc.b; }
    }
  })();
  var geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute("normal", new THREE.BufferAttribute(nor, 3).setUsage(THREE.DynamicDrawUsage));
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  geo.setIndex(idx);
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 50);

  var COS = [], SIN = [];
  for (var r = 0; r < RAD; r++) { COS.push(Math.cos(r / RAD * Math.PI * 2)); SIN.push(Math.sin(r / RAD * Math.PI * 2)); }
  var line = new Float32Array(M * 3), GC = new THREE.Color();
  function gradAt(x) { return GC.copy(AMBER).lerp(ORANGE, Math.min(1, Math.max(0, (x + 3) / 6))); }
  var TAN = new Float32Array(M * 3), FOLDFIX = false;
  function build(p, n, R) {
    var nx = 0, ny = 0, nz = 0, tx = 1, ty = 0, tz = 0;
    for (var i = 0; i < n; i++) {
      var i0 = Math.max(0, i - 1), i1 = Math.min(n - 1, i + 1);
      var ux = p[i1 * 3] - p[i0 * 3], uy = p[i1 * 3 + 1] - p[i0 * 3 + 1], uz = p[i1 * 3 + 2] - p[i0 * 3 + 2];
      var tl = Math.hypot(ux, uy, uz);
      if (tl > 1e-6) { tx = ux / tl; ty = uy / tl; tz = uz / tl; }        // coincident points keep the last direction
      TAN[i * 3] = tx; TAN[i * 3 + 1] = ty; TAN[i * 3 + 2] = tz;
      if (i === 0) { nx = -ty; ny = tx; nz = 0; if (Math.hypot(nx, ny) < 1e-4) { nx = 1; ny = 0; } }
      else { var dp = nx * tx + ny * ty + nz * tz; nx -= dp * tx; ny -= dp * ty; nz -= dp * tz; }   // parallel transport
      var nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
      var bx = ty * nz - tz * ny, by = tz * nx - tx * nz, bz = tx * ny - ty * nx;
      for (var j = 0; j < RAD; j++) {
        var cx = COS[j] * nx + SIN[j] * bx, cy = COS[j] * ny + SIN[j] * by, cz = COS[j] * nz + SIN[j] * bz, o = (i * RAD + j) * 3;
        pos[o] = p[i * 3] + cx * R; pos[o + 1] = p[i * 3 + 1] + cy * R; pos[o + 2] = p[i * 3 + 2] + cz * R;
        nor[o] = cx; nor[o + 1] = cy; nor[o + 2] = cz;
      }
      var gc = gradAt(p[i * 3]);                               // amber on the left to orange on the right, like the logo
      for (var j2 = 0; j2 < RAD; j2++) { var o2 = (i * RAD + j2) * 3; col[o2] = gc.r; col[o2 + 1] = gc.g; col[o2 + 2] = gc.b; }
    }
    // The logo's bends are tighter than its stroke is wide. On the inside of a bend no ring may run
    // backwards along the line: it is pinned to the ring before, so the inner wall closes up like the logo's.
    for (var a2 = 1; a2 < (FOLDFIX ? n : 0); a2++) {
      var Tx = TAN[a2 * 3], Ty = TAN[a2 * 3 + 1], Tz = TAN[a2 * 3 + 2];
      for (var b2 = 0; b2 < RAD; b2++) {
        var o3 = (a2 * RAD + b2) * 3, q3 = o3 - RAD * 3;
        if ((pos[o3] - pos[q3]) * Tx + (pos[o3 + 1] - pos[q3 + 1]) * Ty + (pos[o3 + 2] - pos[q3 + 2]) * Tz < 0) {
          pos[o3] = pos[q3]; pos[o3 + 1] = pos[q3 + 1]; pos[o3 + 2] = pos[q3 + 2];
          nor[o3] = nor[q3]; nor[o3 + 1] = nor[q3 + 1]; nor[o3 + 2] = nor[q3 + 2];
        }
      }
    }
    geo.attributes.color.needsUpdate = true;
    geo.attributes.position.needsUpdate = true;
    geo.attributes.normal.needsUpdate = true;
  }

  /* The ribbon flow runs in the vertex shader, only while the line is the wave.
     The round ends use the same formula at their centre, so they always stay attached. */
  var uniforms = { uTime: { value: 0 }, uFlow: { value: 0 } };
  var FLOW = "vec3 wmFlow(vec3 P) {\n  float u = clamp((P.x + 3.0) / 6.0, 0.0, 1.0);\n  float tp = sin(3.14159265 * u);\n" +
    "  return vec3(0.0, cos(P.x * 0.9 - uTime * 0.9) * 0.05 * tp * uFlow, sin(P.x * 1.25 - uTime * 1.3) * 0.28 * tp * uFlow);\n}\n";
  var mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.34, metalness: 0.05 });
  mat.onBeforeCompile = function (shader) {
    shader.uniforms.uTime = uniforms.uTime; shader.uniforms.uFlow = uniforms.uFlow;
    shader.vertexShader = "uniform float uTime;\nuniform float uFlow;\n" + FLOW + shader.vertexShader.replace("#include <begin_vertex>",
      "#include <begin_vertex>\ntransformed += wmFlow(position);\n");
  };
  var mesh = new THREE.Mesh(geo, [mat]); mesh.frustumCulled = false;
  var group = new THREE.Group(); group.add(mesh); scene.add(group);
  var capGeo = new THREE.SphereGeometry(RADIUS, 32, 24), caps = [];
  for (var ci = 0; ci < 10; ci++) {
    (function () {
      var cm = new THREE.MeshStandardMaterial({ color: AMBER.clone(), roughness: 0.34, metalness: 0.05 });
      var capC = { value: new THREE.Vector3() };
      cm.onBeforeCompile = function (shader) {
        shader.uniforms.uTime = uniforms.uTime; shader.uniforms.uFlow = uniforms.uFlow; shader.uniforms.capC = capC;
        shader.vertexShader = "uniform float uTime;\nuniform float uFlow;\nuniform vec3 capC;\n" + FLOW + shader.vertexShader.replace("#include <begin_vertex>",
          "#include <begin_vertex>\ntransformed += wmFlow(capC);\n");
      };
      var cmesh = new THREE.Mesh(capGeo, cm); cmesh.visible = false; cmesh.userData.capC = capC;
      caps.push(cmesh); group.add(cmesh);
    })();
  }

  /* ---------- Scroll path ----------
     Each key pins a pose to a point on the page: element, fraction, pose, phone overrides.
     nx/ny place the line as a fraction of the screen (-1 to 1), w is its width as a share of the screen.
     Inside the pinned Services chapter, fractions are of its scroll distance, in step with the copy. */
  function P(o) { return Object.assign({ nx: 0, ny: 0, w: 0.4, rx: 0, ry: 0, rz: 0, fade: 1, shape: 0 }, o); }
  var SVC = P({ nx: 0.48, ny: -0.02, w: 0.3, rx: 0.06, ry: -0.16 });
  var SVC_M = { nx: 0, ny: 0.5, w: 0.62 };
  var KEYS = [
    ["#hero", 0.0, P({ nx: 0.5, ny: 0.12, w: 0.36, rx: 0.1, ry: -0.26, alignTo: ".hero-inner" }), { nx: 0, ny: 0.52, w: 0.78 }],
    ["#hero", 0.8, P({ nx: 0.5, ny: 0.32, w: 0.36, rx: 0.1, ry: 0.1 }), { nx: 0, ny: 0.6, w: 0.74 }],
    ["#match", 0.22, P({ nx: 0, ny: 0.42, w: 0.36, shape: BREAKSHAPE }), { nx: 0, ny: 0.5, w: 0.6 }],
    ["#match", 0.36, P({ nx: 0, ny: 0.38, w: 0.38, shape: BREAKSHAPE }), { nx: 0, ny: 0.49, w: 0.64 }],
    ["#match", 0.56, P({ nx: 0, ny: 0.44, w: 0.4 }), { nx: 0, ny: 0.55, w: 0.8 }],
    ["#match", 0.95, P({ nx: 0.6, ny: -0.42, w: 0.28, ry: -0.1 }), { nx: 0, ny: 0.6, w: 0.62 }],
    [".svc-track", 0.0, P(Object.assign({}, SVC, { shape: 0 })), SVC_M]
  ];
  var NS = 7;                                                 // disciplines, in the order of the list on the page
  for (var s = 0; s < NS; s++) {
    KEYS.push([".svc-track", s / NS + 0.055, P(Object.assign({}, SVC, { shape: s + 1 })), SVC_M]);
    KEYS.push([".svc-track", (s + 1) / NS - 0.055, P(Object.assign({}, SVC, { shape: s + 1 })), SVC_M]);
  }
  KEYS.push([".svc-track", 1.0, P(Object.assign({}, SVC, { shape: 0, ry: 0.3 })), SVC_M]);
  KEYS.push(["#approach", 0.5, P({ nx: 0.93, ny: 0.15, w: 0.24, rx: 0.3, ry: 0.6, rz: -1.45, fade: 0.6 }), { nx: 0.95, ny: 0.2, w: 0.5, fade: 0.18 }]);
  KEYS.push(["#work", 0.5, P({ nx: 0.94, ny: -0.1, w: 0.24, rx: -0.25, ry: -0.5, rz: -1.65, fade: 0.55 }), { nx: 0.95, ny: -0.1, w: 0.5, fade: 0.18 }]);
  KEYS.push(["#contact", 0.5, P({ nx: 0.5, ny: 0.1, w: 0.36, rx: 0.08, ry: 0.15 }), { nx: 0, ny: 0.55, w: 0.72 }]);

  var FIELDS = ["nx", "ny", "w", "rx", "ry", "rz", "fade"];
  var keyPos = [];
  function measure() {
    var vh = window.innerHeight;
    keyPos = KEYS.map(function (k) {
      var el = document.querySelector(k[0]);
      if (!el) return null;
      var r = el.getBoundingClientRect(), top = r.top + window.scrollY;
      var y = k[0] === ".svc-track" ? top + (r.height - vh) * k[1] : top + r.height * k[1] - vh / 2;
      var st = mobile ? Object.assign({}, k[2], k[3] || {}) : Object.assign({}, k[2]);
      if (st.alignTo && !mobile) {                             // sit level with the hero copy on any screen height
        var e2 = document.querySelector(st.alignTo);
        if (e2) { var r2 = e2.getBoundingClientRect(), cy = r2.top + window.scrollY + r2.height / 2 - Math.max(0, y); st.ny = 1 - 2 * cy / vh; }
      }
      return { y: y, st: st };
    }).filter(Boolean).sort(function (a, b) { return a.y - b.y; });
  }
  function cr(p0, p1, p2, p3, t) {
    var t2 = t * t, t3 = t2 * t;
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3);
  }
  function poseAt(y) {
    var n = keyPos.length;
    if (!n) return { p: P({}), a: 0, b: 0, t: 0 };
    if (y <= keyPos[0].y) return { p: keyPos[0].st, a: keyPos[0].st.shape, b: keyPos[0].st.shape, t: 0 };
    if (y >= keyPos[n - 1].y) return { p: keyPos[n - 1].st, a: keyPos[n - 1].st.shape, b: keyPos[n - 1].st.shape, t: 0 };
    for (var i = 0; i < n - 1; i++) {
      if (y <= keyPos[i + 1].y) {
        var t = (y - keyPos[i].y) / Math.max(1, keyPos[i + 1].y - keyPos[i].y);
        var A = keyPos[Math.max(0, i - 1)].st, B = keyPos[i].st, C = keyPos[i + 1].st, D = keyPos[Math.min(n - 1, i + 2)].st;
        var o = {};
        FIELDS.forEach(function (f) { o[f] = (B[f] === C[f]) ? B[f] : cr(A[f], B[f], C[f], D[f], t); });
        return { p: o, a: B.shape, b: C.shape, t: t };
      }
    }
  }

  /* ---------- What to draw at each moment ----------
     Wave <-> W/M: a true morph (same strokes, so it stays clean).
     Between any other shapes the line redraws itself like a pen: the old shape is drawn away until a
     short stroke is left, that stroke glides to where the new shape begins, and the new shape is drawn out. */
  var GL = Math.round(0.12 * L);
  function ease(x) { x = Math.min(1, Math.max(0, x)); return x * x * x * (x * (6 * x - 15) + 10); }
  function ranges(br, w0, w1) {
    var out = [], s0 = w0;
    for (var i = 0; i < br.length; i++) { var k = br[i]; if (k > w0 && k <= w1) { if (k - 1 > s0) out.push([s0, k - 1]); s0 = k; } }
    if (w1 > s0) out.push([s0, w1]);
    return out;
  }
  function radOf(k) { return k === 0 || k === BREAKSHAPE ? WAVE_R : RADIUS; }
  function compose(st) {
    var A = SHAPES[st.a], B = SHAPES[st.b], t = st.t;
    if (st.a === st.b || st.a + st.b === BREAKSHAPE && (st.a === 0 || st.b === 0)) {
      var e = st.a === st.b ? 0 : ease(t);
      return { key: "m" + st.a + "," + st.b + "," + e.toFixed(4), n: M, rad: radOf(st.a), br: A.br.length ? A.br : B.br, w0: 0, w1: L,
        wave: (st.a === 0 ? 1 - e : 0) + (st.b === 0 ? e : 0),
        fill: function () { for (var i = 0; i < M * 3; i++) line[i] = A.p[i] + (B.p[i] - A.p[i]) * e; } };
    }
    if (t < 0.42) {
      var u = ease(t / 0.42);
      return { key: "a" + st.a, n: M, rad: radOf(st.a), br: A.br, w0: Math.round(u * (L - GL)), w1: L, wave: st.a === 0 ? 1 - u : 0,
        fill: function () { line.set(A.p); } };
    }
    if (t < 0.58) {
      var g = ease((t - 0.42) / 0.16);
      return { key: "g" + st.a + "," + st.b + "," + g.toFixed(4), n: GL + 1, rad: radOf(st.a) + (radOf(st.b) - radOf(st.a)) * g, br: [], w0: 0, w1: GL, wave: 0,
        fill: function () {
          var lift = Math.sin(g * Math.PI) * 0.6;
          for (var i = 0; i <= GL; i++) for (var d = 0; d < 3; d++) {
            var o = i * 3 + d, from = A.p[(L - GL + i) * 3 + d], to = B.p[o];
            line[o] = from + (to - from) * g + (d === 2 ? lift : 0);
          }
        } };
    }
    var v = ease((t - 0.58) / 0.42);
    return { key: "b" + st.b, n: M, rad: radOf(st.b), br: B.br, w0: 0, w1: GL + Math.round(v * (L - GL)), wave: st.b === 0 ? v : 0,
      fill: function () { line.set(B.p); } };
  }

  /* ---------- Resize ---------- */
  var halfW = HALF_H;
  function resize() {
    var w = window.innerWidth, h = window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    halfW = HALF_H * camera.aspect;
    mobile = w < 900;
    measure();
  }
  window.addEventListener("resize", resize);
  window.addEventListener("load", measure);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
  resize();
  setTimeout(measure, 800);

  var mx = 0, my = 0, pmx = 0, pmy = 0;
  window.addEventListener("pointermove", function (e) {
    if (e.pointerType !== "mouse") return;
    mx = e.clientX / window.innerWidth - 0.5; my = e.clientY / window.innerHeight - 0.5;
  }, { passive: true });

  /* ---------- Loop ---------- */
  var t0 = performance.now(), last = t0, running = true, sy = window.scrollY, cur = null, lastKey = "", flowNow = 0;
  document.addEventListener("visibilitychange", function () {
    running = !document.hidden;
    if (running) { last = performance.now(); requestAnimationFrame(frame); }
  });

  function frame(now) {
    if (!running) return;
    var dt = Math.min(0.05, (now - last) / 1000); last = now;
    var time = (now - t0) / 1000;

    // Smooth the scroll itself, so position, rotation and shape all glide together
    sy += (window.scrollY - sy) * (reduce ? 1 : 1 - Math.pow(0.0025, dt));
    var st = reduce ? { p: keyPos[0] ? keyPos[0].st : P({}), a: 0, b: 0, t: 0 } : poseAt(sy);
    var c = compose(st);
    if (c.key !== lastKey) { c.fill(); build(line, c.n, c.rad); lastKey = c.key; }

    // Draw-on at load, then split the visible stretch at any breaks; every end gets a round cap
    var draw = reduce ? 1 : Math.min(1, Math.max(0, (time - 0.25) / 2.4));
    draw = 1 - Math.pow(1 - draw, 3);
    var open = c.br.filter(function (k) { return Math.hypot(line[k * 3] - line[k * 3 - 3], line[k * 3 + 1] - line[k * 3 - 2], line[k * 3 + 2] - line[k * 3 - 1]) > 0.15; });
    var rs = ranges(open, c.w0, Math.min(c.w1, Math.round(L * draw)));
    geo.clearGroups();
    for (var q = 0; q < caps.length; q++) caps[q].visible = false;
    var ci = 0;
    rs.forEach(function (rg) {
      geo.addGroup(rg[0] * RAD * 6, (rg[1] - rg[0]) * RAD * 6, 0);
      [rg[0], rg[1]].forEach(function (k) {
        if (ci >= caps.length) return;
        var cp = caps[ci++]; cp.visible = true; cp.scale.setScalar(c.rad / RADIUS);
        cp.position.set(line[k * 3], line[k * 3 + 1], line[k * 3 + 2]);
        cp.userData.capC.value.copy(cp.position);
        cp.material.color.copy(gradAt(line[k * 3]));
      });
    });

    var flowTarget = reduce ? 0 : Math.min(1, Math.max(0, (time - 2.4) / 1.5)) * c.wave;
    flowNow += (flowTarget - flowNow) * (1 - Math.pow(0.05, dt));
    uniforms.uTime.value = time; uniforms.uFlow.value = flowNow;

    var p = st.p;
    if (!cur) cur = Object.assign({}, p);
    var k = reduce ? 1 : 1 - Math.pow(0.02, dt);
    FIELDS.forEach(function (f) { cur[f] += (p[f] - cur[f]) * k; });
    pmx += (mx - pmx) * 0.04; pmy += (my - pmy) * 0.04;
    var bob = reduce ? 0 : Math.sin(time * 0.6) * 0.06;
    var sway = reduce ? 0 : Math.sin(time * 0.35) * 0.08;

    var scale = Math.min(cur.w * 2 * halfW / 6, 0.62 * 2 * HALF_H / 3.9);
    group.position.set(cur.nx * halfW, cur.ny * HALF_H + bob, 0);
    group.rotation.set(cur.rx + pmy * 0.14, cur.ry + sway + pmx * 0.2, cur.rz);
    group.scale.setScalar(scale);
    canvas.style.opacity = String(Math.max(0, Math.min(1, cur.fade)));

    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
