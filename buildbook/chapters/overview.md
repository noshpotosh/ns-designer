<header class="hero">
<div class="eyebrow">36 keys · PG1316S · XIAO nRF52840 · ZMK</div>
<h1>An ultra-thin wireless split, two clean rectangles</h1>
<p class="lede">A pocketable 36-key keyboard with no row or column stagger. It uses Kailh PG1316S laptop-style butterfly switches, 0.8 mm PCBs (separate left and right boards) and a 3D-printed tray. The target is 7 mm or less from desk to keycap. This is an unvalidated design; see the build-readiness chapter before ordering.</p>

<div class="specs">
<div class="spec"><span class="k">Keys</span><span class="v">36 (18 per half)</span></div>
<div class="spec"><span class="k">Layout</span><span class="v">Ortholinear 5×4 grid</span></div>
<div class="spec"><span class="k">Switch</span><span class="v">Kailh PG1316S, SMD</span></div>
<div class="spec"><span class="k">Controller</span><span class="v">XIAO nRF52840 ×2</span></div>
<div class="spec"><span class="k">Firmware</span><span class="v">ZMK, split BLE</span></div>
<div class="spec"><span class="k">Battery</span><span class="v">2.5 mm LiPo, ~100 mAh</span></div>
<div class="spec"><span class="k">PCB</span><span class="v">0.8 mm FR4, 2-layer, left + right boards</span></div>
<div class="spec"><span class="k">Target height</span><span class="v">≤ 7 mm</span></div>
</div>

<div class="figure">
<div class="scroll">
<svg id="board" viewBox="-6 -10 202 94" width="100%" style="min-width:520px" role="img" aria-label="Top view of both halves at 17 mm pitch"></svg>
</div>
<div class="cap">Top view drawn to scale at 17 mm pitch. The XIAO, shown in gold, fills the two empty outer slots of the thumb row.</div>
</div>

<h3>Build phases</h3>
<ul class="phases">
<li><label><input type="checkbox" id="ph0"><span class="n">00</span><span class="t"><a href="#requirements">Lock requirements</a><small>Resolve the open questions</small></span></label></li>
<li><label><input type="checkbox" id="ph1"><span class="n">01</span><span class="t"><a href="#layout">Layout &amp; matrix</a><small>Pitch, grid, GPIO map</small></span></label></li>
<li><label><input type="checkbox" id="ph2"><span class="n">02</span><span class="t"><a href="#pcb">PCB design</a><small>KiCad → JLCPCB</small></span></label></li>
<li><label><input type="checkbox" id="ph3"><span class="n">03</span><span class="t"><a href="#firmware">Firmware</a><small>ZMK shield. Can run in parallel with the PCB</small></span></label></li>
<li><label><input type="checkbox" id="ph4"><span class="n">04</span><span class="t"><a href="#case">Case</a><small>Parametric, 3D printed</small></span></label></li>
<li><label><input type="checkbox" id="ph5"><span class="n">05</span><span class="t"><a href="#assembly">Assembly &amp; test</a><small>Solder, test, close up</small></span></label></li>
</ul>
</header>
