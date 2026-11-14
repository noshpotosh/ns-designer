
# 3D model

<p>Renders of the concept model from <code>hardware/case/keyboard.py</code>. The open tray is the locked design; the enclosed case is a concept at 18 mm pitch. Regenerate the images with <code>node hardware/case/render.mjs</code>.</p>

<div class="figure">
<div class="toolbar" role="group" aria-label="Colorway">
<span class="k">Colorway</span>
<button class="chip" data-cw="graphite" aria-pressed="true">Graphite</button>
<button class="chip" data-cw="chalk" aria-pressed="false">Chalk</button>
<button class="chip" data-cw="signal" aria-pressed="false">Signal</button>
</div>
<figure class="shot">
<img id="hero-shot" src="../assets/hero-graphite.png" width="1200" height="675" alt="Open tray, three-quarter view, graphite colorway">
<figcaption>Open tray, 3/4 view. 2 × 90.4 × 76.0 mm, 7.0 mm tall.</figcaption>
</figure>
</div>

<h3>Open tray views</h3>
<div class="shots">
<figure class="shot"><img src="../assets/hero-graphite-exploded.png" width="1200" height="675" loading="lazy" alt="Open tray, exploded view"><figcaption>Exploded: caps, switches, PCB, battery, tray.</figcaption></figure>
<figure class="shot"><img src="../assets/top-graphite.png" width="1200" height="675" loading="lazy" alt="Open tray, top view"><figcaption>Top.</figcaption></figure>
<figure class="shot"><img src="../assets/side-graphite.png" width="1200" height="675" loading="lazy" alt="Open tray, side profile"><figcaption>Profile.</figcaption></figure>
<figure class="shot"><img src="../assets/under-graphite.png" width="1200" height="675" loading="lazy" alt="Open tray, underside"><figcaption>Underside: battery pocket, XIAO pocket, reset pinhole.</figcaption></figure>
</div>

<h3>Enclosed concept</h3>
<div class="shots">
<figure class="shot"><img src="../assets/enclosed-hero-chalk.png" width="1200" height="675" loading="lazy" alt="Enclosed case, three-quarter view, chalk"><figcaption>Chalk, 3/4 view.</figcaption></figure>
<figure class="shot"><img src="../assets/enclosed-hero-graphite.png" width="1200" height="675" loading="lazy" alt="Enclosed case, three-quarter view, graphite"><figcaption>Graphite, 3/4 view.</figcaption></figure>
<figure class="shot"><img src="../assets/enclosed-hero-graphite-exploded.png" width="1200" height="675" loading="lazy" alt="Enclosed case, exploded view"><figcaption>Exploded: top shell over bottom plate.</figcaption></figure>
<figure class="shot"><img src="../assets/enclosed-side-chalk.png" width="1200" height="675" loading="lazy" alt="Enclosed case, side profile"><figcaption>Profile.</figcaption></figure>
</div>

<h3>Interactive</h3>
<div class="viewer" id="viewer">
<div style="display:grid;gap:12px;justify-items:center">
<p>Orbit, explode and recolor the model. Loads about 5 MB.</p>
<div class="toolbar">
<button class="chip" data-load="">Load open tray</button>
<button class="chip" data-load="?case=enclosed">Load enclosed</button>
</div>
</div>
</div>
<p class="cap" style="font-size:13px;color:var(--muted)">The viewer is <a href="../viewer/index.html">cad/viewer/index.html</a>. It fetches the model, so it needs a web server: run <code>npm run build</code> then <code>npm run preview</code> and open <code>localhost:8000/ns-designer/</code>. Opened straight from disk, only the renders work.</p>

