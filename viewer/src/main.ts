import "@fontsource/instrument-sans/400.css";
import "@fontsource/instrument-sans/500.css";
import "@fontsource/instrument-sans/600.css";
import "@fontsource/instrument-sans/700.css";
import "@fontsource/syne/600.css";
import "@fontsource/syne/700.css";
import "@fontsource/syne/800.css";
import "./style.css";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";

type Product = {
  id: string;
  title: string;
  blurb: string;
  stl: string;
  scad: string;
  reference: string;
  boardHint: string;
};

const products: Product[] = [
  {
    id: "square",
    title: "Köşe sabitleme aparatı",
    blurb:
      "Gövde 70×22, et 3, kanal 18. Kulak et devamı (basamaksız); yanaklar X’te kalın.",
    stl: "/models/corner-assembly-square.stl?v=17",
    scad: "../models/corner-assembly-square.scad",
    reference: "/reference/reel1-kose-gonye.jpg",
    boardHint:
      "70×22 · et 3 · kulak et devamı · delik Ø3 · 36 mm · vida Ø2.5",
  },
  {
    id: "plain",
    title: "Kulaksız köşe aparatı",
    blurb: "Birincinin aynı gövdesi — yanak ve kulak yok. Sadece köşeyi tutar.",
    stl: "/models/corner-plain.stl?v=17",
    scad: "../models/corner-plain.scad",
    reference: "/reference/reel2-kanal-jig.jpg",
    boardHint: "70×22 mm · et 3 mm · kanal 18 mm · kulak yok",
  },
];

const app = document.querySelector<HTMLDivElement>("#app")!;
app.innerHTML = `
  <div class="shell">
    <header class="top">
      <h1 class="brand">Köşe<span>.</span></h1>
      <p class="lede">
        İki 18&nbsp;mm sunta/MDF köşe aparatı: kulaklı ve kulaksız.
        Gövde 70×22&nbsp;mm, et 3&nbsp;mm, U kanal 18&nbsp;mm.
      </p>
    </header>
    <div class="stage">
      <aside class="side">
        <p class="section-label">Ürünler</p>
        <div class="picker" id="picker"></div>
        <div class="ref"><img id="ref-img" alt="Reel referans karesi" /></div>
        <p class="meta" id="meta"></p>
        <div class="actions">
          <a class="btn btn-primary" id="dl-stl" download>STL indir</a>
          <a class="btn btn-ghost" id="dl-scad" download>OpenSCAD</a>
        </div>
      </aside>
      <section class="viewport">
        <div id="canvas-host"></div>
        <div class="status" id="status">Model yükleniyor…</div>
        <div class="hud">
          <span>Sürükle: döndür · kaydır: kaydır · tekerlek: yakınlaş</span>
          <span id="hud-name"></span>
        </div>
      </section>
    </div>
  </div>
`;

const picker = document.querySelector("#picker")!;
const refImg = document.querySelector<HTMLImageElement>("#ref-img")!;
const meta = document.querySelector("#meta")!;
const dlStl = document.querySelector<HTMLAnchorElement>("#dl-stl")!;
const dlScad = document.querySelector<HTMLAnchorElement>("#dl-scad")!;
const statusEl = document.querySelector<HTMLDivElement>("#status")!;
const hudName = document.querySelector("#hud-name")!;
const host = document.querySelector<HTMLDivElement>("#canvas-host")!;

products.forEach((p, i) => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = `pick${i === 0 ? " active" : ""}`;
  btn.dataset.id = p.id;
  btn.innerHTML = `<h2>${p.title}</h2><p>${p.blurb}</p>`;
  btn.addEventListener("click", () => selectProduct(p.id));
  picker.appendChild(btn);
});

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x14120f, 220, 520);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 2000);
camera.position.set(140, 110, 160);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
host.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(30, 20, 20);
controls.minDistance = 40;
controls.maxDistance = 420;

const hemi = new THREE.HemisphereLight(0xf4efe6, 0x2a241c, 1.15);
scene.add(hemi);
const key = new THREE.DirectionalLight(0xffffff, 1.35);
key.position.set(80, 120, 60);
scene.add(key);
const fill = new THREE.DirectionalLight(0xb8f000, 0.35);
fill.position.set(-60, 40, -40);
scene.add(fill);

const grid = new THREE.GridHelper(240, 24, 0x4a4032, 0x2a241c);
grid.position.y = -0.01;
scene.add(grid);

const loader = new STLLoader();
let currentMesh: THREE.Mesh | null = null;
let loadToken = 0;

function fitCamera(object: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(object);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = maxDim * 2.4;
  controls.target.copy(center);
  camera.position.set(center.x + dist * 0.75, center.y + dist * 0.55, center.z + dist * 0.85);
  camera.near = Math.max(0.1, dist / 100);
  camera.far = dist * 20;
  camera.updateProjectionMatrix();
  controls.update();
}

function setStatus(text: string | null) {
  if (!text) {
    statusEl.hidden = true;
    statusEl.textContent = "";
    return;
  }
  statusEl.hidden = false;
  statusEl.textContent = text;
}

async function loadModel(product: Product) {
  const token = ++loadToken;
  setStatus("Model yükleniyor…");
  if (currentMesh) {
    scene.remove(currentMesh);
    currentMesh.geometry.dispose();
    (currentMesh.material as THREE.Material).dispose();
    currentMesh = null;
  }

  try {
    const geometry = await loader.loadAsync(product.stl);
    if (token !== loadToken) return;
    geometry.computeVertexNormals();
    geometry.center();
    // Mesh is already Z-up (top plate on +Z, channels open along arms).

    const material = new THREE.MeshStandardMaterial({
      color: 0xb8f000,
      metalness: 0.05,
      roughness: 0.38,
      flatShading: false,
    });
    currentMesh = new THREE.Mesh(geometry, material);
    scene.add(currentMesh);
    // View from outside the L corner so the channel + flap read clearly
    fitCamera(currentMesh);
    if (currentMesh) {
      const box = new THREE.Box3().setFromObject(currentMesh);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const dist = Math.max(size.x, size.y, size.z) * 2.2;
      controls.target.copy(center);
      camera.position.set(center.x + dist * 0.45, center.y - dist * 0.95, center.z + dist * 1.05);
      controls.update();
    }
    setStatus(null);
  } catch {
    if (token !== loadToken) return;
    setStatus("Model yüklenemedi. STL dosyasını kontrol et.");
  }
}

function selectProduct(id: string) {
  const product = products.find((p) => p.id === id) ?? products[0];
  picker.querySelectorAll(".pick").forEach((el) => {
    el.classList.toggle("active", (el as HTMLElement).dataset.id === product.id);
  });
  refImg.src = product.reference;
  refImg.alt = `${product.title} — reel referansı`;
  meta.innerHTML = `<strong>${product.title}</strong><br>${product.boardHint}<br>Kaynak: görünen geometriden yeniden çizim (ölçüler ayarlanabilir).`;
  dlStl.href = product.stl;
  dlStl.download = (product.stl.split("/").pop() ?? "model.stl").split("?")[0];
  // OpenSCAD lives outside public/; link to GitHub-style raw path via repo models/
  dlScad.href = product.stl.replace("/models/", "/models/").replace(".stl", ".scad");
  // Serve scad copies from public too
  dlScad.href = product.stl.replace(".stl", ".scad");
  dlScad.download = (product.stl.split("/").pop() ?? "model.stl").replace(".stl", ".scad");
  hudName.textContent = product.title;
  void loadModel(product);
}

function resize() {
  const { clientWidth: w, clientHeight: h } = host;
  camera.aspect = w / Math.max(h, 1);
  camera.updateProjectionMatrix();
  renderer.setSize(w, h, false);
}

window.addEventListener("resize", resize);
resize();

function tick() {
  controls.update();
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();

selectProduct(products[0].id);
