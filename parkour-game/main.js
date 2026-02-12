// Ancient Dash: Rooftop Run
// Self-contained Three.js parkour playground tuned for young players.

// ---------------------------
// Basic setup
// ---------------------------
const canvas = document.getElementById('game');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
renderer.shadowMap.enabled = true;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0xd6c6a2, 0.0075);

const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 500);
let cameraYaw = 0;
let cameraPitch = 0.25;
let cameraDistance = 10;

// ---------------------------
// Audio helpers (lightweight WebAudio beeps)
// ---------------------------
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playTone(freq = 440, duration = 0.15, type = 'sine', vol = 0.2) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.frequency.value = freq;
  osc.type = type;
  gain.gain.value = vol;
  osc.connect(gain).connect(audioCtx.destination);
  osc.start();
  gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
  osc.stop(audioCtx.currentTime + duration);
}

// ---------------------------
// Lighting & background
// ---------------------------
const hemi = new THREE.HemisphereLight(0xfff6e8, 0x8c6b3e, 0.85);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffe7b2, 0.9);
sun.position.set(30, 50, 10);
sun.castShadow = true;
sun.shadow.camera.top = 40;
sun.shadow.camera.bottom = -40;
sun.shadow.camera.left = -40;
sun.shadow.camera.right = 40;
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);

const groundMat = new THREE.MeshStandardMaterial({ color: 0xd9c3a5, roughness: 0.9 });
const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), groundMat);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// Sky gradient
const skyGeo = new THREE.SphereGeometry(200, 32, 32);
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide,
  uniforms: {
    topColor: { value: new THREE.Color(0xf7e9c5) },
    bottomColor: { value: new THREE.Color(0xd09c62) },
  },
  vertexShader: `varying vec3 vPos; void main(){ vPos = position; gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `varying vec3 vPos; uniform vec3 topColor; uniform vec3 bottomColor; void main(){ float h = normalize(vPos).y*0.5+0.5; gl_FragColor = vec4(mix(bottomColor, topColor, h),1.0); }`
});
const sky = new THREE.Mesh(skyGeo, skyMat);
scene.add(sky);

// Background pyramids
function addPyramid(x, z, size, color = 0xd4b17a) {
  const geo = new THREE.ConeGeometry(size, size * 0.9, 4);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.8, flatShading: true });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(x, size * 0.45, z);
  mesh.rotation.y = Math.PI / 4;
  mesh.receiveShadow = true;
  mesh.castShadow = true;
  scene.add(mesh);
}
addPyramid(120, -80, 40);
addPyramid(150, 60, 55, 0xcfa86a);
addPyramid(-130, -120, 50, 0xd9b87e);

// Props: palms & tents simple
function makePalm(x, z) {
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.6, 6, 6), new THREE.MeshStandardMaterial({ color: 0x9c6b3c }));
  trunk.position.set(x, 3, z);
  trunk.castShadow = true;
  trunk.receiveShadow = true;
  const leaves = new THREE.Mesh(new THREE.ConeGeometry(3.2, 3, 8), new THREE.MeshStandardMaterial({ color: 0x3d8b4c, flatShading: true }));
  leaves.position.set(0, 3.5, 0);
  leaves.rotation.x = Math.PI;
  trunk.add(leaves);
  scene.add(trunk);
}
for (let i = 0; i < 12; i++) {
  makePalm((Math.random() - 0.5) * 160, (Math.random() - 0.5) * 160);
}

// ---------------------------
// Level geometry
// ---------------------------
const platformData = [];
const checkpointPositions = [];
const platformGeo = new THREE.BoxGeometry(8, 1, 8);
const platformMat = new THREE.MeshStandardMaterial({ color: 0xcba36b, roughness: 0.8, flatShading: true });
const platformMesh = new THREE.InstancedMesh(platformGeo, platformMat, 120);
platformMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
platformMesh.castShadow = true;
platformMesh.receiveShadow = true;
scene.add(platformMesh);

const checkpointGeo = new THREE.CylinderGeometry(0.6, 0.6, 4, 12);
const checkpointMat = new THREE.MeshStandardMaterial({ color: 0xffef8a, emissive: 0xe5c158, emissiveIntensity: 0.8 });
const checkpointMesh = new THREE.InstancedMesh(checkpointGeo, checkpointMat, 45);
checkpointMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(checkpointMesh);

function buildRoute() {
  let idx = 0;
  let x = 0, y = 3, z = 0;
  const directions = [1, -1];
  for (let cp = 0; cp < 45; cp++) {
    const difficulty = Math.floor(cp / 5);
    const gap = 5 + difficulty * 0.8;
    const heightJitter = (Math.sin(cp * 0.4) + Math.random() * 0.3) * (difficulty * 0.5);
    x += gap * (directions[cp % 2]);
    z += 6;
    y = Math.max(2, 3 + heightJitter);
    const platformScale = 1 + Math.max(0, 2 - difficulty * 0.2);
    platformData.push({ x, y, z, w: 7 / platformScale, h: 1, d: 7 / platformScale });
    checkpointPositions.push(new THREE.Vector3(x, y + 3, z));

    const matrix = new THREE.Matrix4().compose(
      new THREE.Vector3(x, y, z),
      new THREE.Quaternion(),
      new THREE.Vector3(platformScale, 1, platformScale)
    );
    platformMesh.setMatrixAt(idx, matrix);

    const cpMatrix = new THREE.Matrix4().compose(
      new THREE.Vector3(x, y + 1.5, z),
      new THREE.Quaternion(),
      new THREE.Vector3(1, 1, 1)
    );
    checkpointMesh.setMatrixAt(idx, cpMatrix);
    idx++;
  }
  platformMesh.instanceMatrix.needsUpdate = true;
  checkpointMesh.instanceMatrix.needsUpdate = true;
}
buildRoute();

// Additional props near path (crates/awnings)
function addPropBox(pos, color = 0xb98a52) {
  const box = new THREE.Mesh(new THREE.BoxGeometry(2, 2, 2), new THREE.MeshStandardMaterial({ color, roughness: 0.7 }));
  box.position.copy(pos);
  box.castShadow = true;
  box.receiveShadow = true;
  scene.add(box);
}
for (let i = 0; i < 30; i++) {
  addPropBox(new THREE.Vector3((Math.random() - 0.5) * 60, 1, i * 8 - 30));
}

// ---------------------------
// Player setup
// ---------------------------
const player = {
  mesh: new THREE.Group(),
  velocity: new THREE.Vector3(),
  onGround: false,
  stamina: 1,
  invulnTime: 0,
};

function buildPlayerModel() {
  const bodyMat = new THREE.MeshStandardMaterial({ color: 0xc98352, flatShading: true });
  const shirtMat = new THREE.MeshStandardMaterial({ color: 0x9b111e, emissive: 0x380404, flatShading: true });
  const shortMat = new THREE.MeshStandardMaterial({ color: 0x1c1c1c, flatShading: true });
  const accentMat = new THREE.MeshStandardMaterial({ color: 0xf8d347, flatShading: true });
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.8, 12, 12), bodyMat);
  head.position.y = 3.2;
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.95, 1.8, 6, 10), shirtMat);
  body.position.y = 1.6;
  const shorts = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.95, 1, 8), shortMat);
  shorts.position.y = 0.4;
  const rcbText = makeTextPlane('RCB', '#f8d347', '#9b111e');
  rcbText.position.set(0, 2.2, 0.95);
  player.mesh.add(head, body, shorts, rcbText);

  const legGeo = new THREE.BoxGeometry(0.6, 1.2, 0.6);
  const armGeo = new THREE.BoxGeometry(0.5, 1.1, 0.5);
  const legMat = shortMat;
  const armMat = new THREE.MeshStandardMaterial({ color: 0xc98352, flatShading: true });
  const leftLeg = new THREE.Mesh(legGeo, legMat);
  const rightLeg = new THREE.Mesh(legGeo, legMat);
  leftLeg.position.set(-0.5, -0.2, 0);
  rightLeg.position.set(0.5, -0.2, 0);
  const leftArm = new THREE.Mesh(armGeo, armMat);
  const rightArm = new THREE.Mesh(armGeo, armMat);
  leftArm.position.set(-1.1, 1.6, 0);
  rightArm.position.set(1.1, 1.6, 0);
  player.mesh.add(leftLeg, rightLeg, leftArm, rightArm);

  const shoes = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.3, 1), accentMat);
  shoes.position.set(0, -0.8, 0.2);
  leftLeg.add(shoes.clone());
  rightLeg.add(shoes.clone());

  player.mesh.castShadow = true;
  player.mesh.receiveShadow = true;
  player.mesh.position.set(0, 6, -8);
  player.mesh.userData.limbs = { leftLeg, rightLeg, leftArm, rightArm };
  scene.add(player.mesh);
}

function makeTextPlane(text, color = '#fff', bg = '#000') {
  const canvas = document.createElement('canvas');
  canvas.width = 256; canvas.height = 128;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = bg; ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.fillStyle = color;
  ctx.font = 'bold 72px Arial';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, canvas.width/2, canvas.height/2);
  const tex = new THREE.Texture(canvas); tex.needsUpdate = true;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true });
  const geo = new THREE.PlaneGeometry(1.6, 0.9);
  return new THREE.Mesh(geo, mat);
}

buildPlayerModel();

// ---------------------------
// Input handling
// ---------------------------
const keys = {};
window.addEventListener('keydown', (e) => {
  keys[e.code] = true;
  if (e.code === 'Escape') togglePause();
});
window.addEventListener('keyup', (e) => { keys[e.code] = false; });

let isPointerLocked = false;
canvas.addEventListener('click', () => {
  if (!isPointerLocked) canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  isPointerLocked = document.pointerLockElement === canvas;
});
document.addEventListener('mousemove', (e) => {
  if (!isPointerLocked) return;
  const sensitivity = 0.0025;
  cameraYaw -= e.movementX * sensitivity;
  cameraPitch -= e.movementY * sensitivity;
  cameraPitch = Math.min(Math.max(cameraPitch, -0.9), 1.0);
});

// ---------------------------
// Game state & UI
// ---------------------------
const overlay = document.getElementById('overlay');
const startScreen = document.getElementById('start-screen');
const pauseScreen = document.getElementById('pause-screen');
const controlsInfo = document.getElementById('controls-info');
const playBtn = document.getElementById('play-btn');
const continueBtn = document.getElementById('continue-btn');
const resetBtn = document.getElementById('reset-btn');
const resetBtn2 = document.getElementById('reset-btn-2');
const resumeBtn = document.getElementById('resume-btn');
const controlsBtn = document.getElementById('controls-btn');
const quitBtn = document.getElementById('quit-btn');
const hud = document.getElementById('hud');
const progressLabel = document.getElementById('progress');
const staminaBar = document.getElementById('stamina-bar');
const arrowUI = document.getElementById('arrow');
const checkpointBanner = document.getElementById('checkpoint-banner');

let paused = true;
let started = false;
let currentCheckpoint = 0;
let respawnPoint = checkpointPositions[0].clone();
let bannerTimer = 0;

function loadProgress() {
  const saved = localStorage.getItem('parkourProgress');
  if (saved) {
    currentCheckpoint = Math.min(44, parseInt(saved, 10));
    respawnPoint = checkpointPositions[currentCheckpoint].clone();
  }
}
function saveProgress() {
  localStorage.setItem('parkourProgress', currentCheckpoint.toString());
}
loadProgress();
updateProgressUI();

function showBanner(text) {
  checkpointBanner.textContent = text;
  checkpointBanner.classList.remove('hidden');
  bannerTimer = 1.3;
}

function togglePause(force) {
  if (!started) return;
  if (force !== undefined) paused = force; else paused = !paused;
  pauseScreen.classList.toggle('hidden', !paused);
  overlay.classList.toggle('hidden', !paused);
  hud.classList.toggle('hidden', paused);
  if (paused) document.exitPointerLock();
}

playBtn.onclick = () => { currentCheckpoint = 0; respawnPoint = checkpointPositions[0].clone(); saveProgress(); startGame(); };
continueBtn.onclick = () => { loadProgress(); startGame(); };
resetBtn.onclick = resetProgress;
resetBtn2.onclick = resetProgress;
resumeBtn.onclick = () => togglePause(false);
controlsBtn.onclick = () => controlsInfo.classList.toggle('hidden');
quitBtn.onclick = () => { paused = true; started = false; overlay.classList.remove('hidden'); startScreen.classList.remove('hidden'); pauseScreen.classList.add('hidden'); hud.classList.add('hidden'); document.exitPointerLock(); };

function startGame() {
  started = true;
  paused = false;
  startScreen.classList.add('hidden');
  pauseScreen.classList.add('hidden');
  overlay.classList.add('hidden');
  hud.classList.remove('hidden');
  player.mesh.position.copy(respawnPoint).add(new THREE.Vector3(0, 2, 0));
  player.velocity.set(0,0,0);
  document.body.requestPointerLock();
}

function resetProgress() {
  localStorage.removeItem('parkourProgress');
  currentCheckpoint = 0;
  respawnPoint = checkpointPositions[0].clone();
  updateProgressUI();
  showBanner('Progress Reset');
}

function updateProgressUI() {
  progressLabel.textContent = `Checkpoint ${currentCheckpoint + 1} / 45`;
}

// ---------------------------
// Hazards & collectibles
// ---------------------------
const hazards = [];
function addHazard(x, y, z, w = 3, d = 3) {
  hazards.push({ x, y, z, w, d });
  const flame = new THREE.Mesh(new THREE.ConeGeometry(0.8, 2, 8), new THREE.MeshStandardMaterial({ color: 0xff7f50, emissive: 0xff9f64, emissiveIntensity: 0.7 }));
  flame.position.set(x, y + 1, z);
  scene.add(flame);
}
for (let i = 8; i < checkpointPositions.length; i += 7) {
  const pos = checkpointPositions[i];
  addHazard(pos.x + 2, pos.y + 0.5, pos.z - 2);
}

const coins = [];
function addCoin(pos) {
  const geo = new THREE.CylinderGeometry(0.5, 0.5, 0.2, 12);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffd166, emissive: 0xffc13b, emissiveIntensity: 0.6 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(pos);
  mesh.rotation.x = Math.PI / 2;
  mesh.castShadow = true;
  scene.add(mesh);
  coins.push({ mesh, collected: false });
}
for (let i = 14; i < checkpointPositions.length; i += 5) {
  const pos = checkpointPositions[i].clone().add(new THREE.Vector3(1.5, 1.2, -1.5));
  addCoin(pos);
}

// ---------------------------
// Enemies: Mummies
// ---------------------------
const mummies = [];
function makeMummy(type, position) {
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.8, 1.8, 6, 8), new THREE.MeshStandardMaterial({ color: 0xe8dec0, roughness: 0.85 }));
  const eyeGeo = new THREE.SphereGeometry(0.15, 6, 6);
  const eyeMat = new THREE.MeshBasicMaterial({ color: 0x222222 });
  const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
  const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
  leftEye.position.set(-0.25, 1.2, 0.9);
  rightEye.position.set(0.25, 1.25, 0.9);
  body.add(leftEye, rightEye);
  body.position.copy(position);
  body.castShadow = true;
  scene.add(body);
  const stats = { speed: 1.5, detect: 9 };
  if (type === 'walker') stats.speed = 1.2;
  if (type === 'sprinter') { stats.speed = 2.4; stats.detect = 12; }
  if (type === 'guard') { stats.speed = 0.9; stats.detect = 6; }
  mummies.push({ mesh: body, type, stats, dir: 1, anchor: position.clone() });
}
makeMummy('walker', checkpointPositions[7].clone().add(new THREE.Vector3(2, -2, 0)));
makeMummy('sprinter', checkpointPositions[20].clone().add(new THREE.Vector3(-2, -1, -2)));
makeMummy('guard', checkpointPositions[33].clone().add(new THREE.Vector3(0, -1, 0)));

// ---------------------------
// Particles for checkpoint confetti
// ---------------------------
const confetti = [];
function spawnConfetti(pos) {
  for (let i = 0; i < 30; i++) {
    const geo = new THREE.SphereGeometry(0.07, 6, 6);
    const mat = new THREE.MeshBasicMaterial({ color: new THREE.Color().setHSL(Math.random(), 0.7, 0.6) });
    const m = new THREE.Mesh(geo, mat);
    m.position.copy(pos);
    scene.add(m);
    confetti.push({ mesh: m, vel: new THREE.Vector3((Math.random()-0.5)*2, Math.random()*3+2, (Math.random()-0.5)*2), life: 1.2 });
  }
}

// ---------------------------
// Utility: collision helpers
// ---------------------------
function isOnPlatform(pos, vel) {
  let grounded = false;
  const radius = 0.9;
  for (const p of platformData) {
    const withinX = pos.x > p.x - p.w && pos.x < p.x + p.w;
    const withinZ = pos.z > p.z - p.d && pos.z < p.z + p.d;
    if (withinX && withinZ) {
      const top = p.y + p.h * 0.5;
      if (pos.y - radius <= top + 0.6 && pos.y - radius >= top - 1.2 && vel.y <= 2) {
        pos.y = top + radius;
        vel.y = Math.max(0, vel.y);
        grounded = true;
        // magnetic landing
        const blend = 0.08;
        pos.x = THREE.MathUtils.lerp(pos.x, THREE.MathUtils.clamp(pos.x, p.x - p.w + 0.5, p.x + p.w - 0.5), blend);
        pos.z = THREE.MathUtils.lerp(pos.z, THREE.MathUtils.clamp(pos.z, p.z - p.d + 0.5, p.z + p.d - 0.5), blend);
      }
    }
  }
  if (pos.y - radius <= 0.5) {
    pos.y = 0.5 + radius;
    vel.y = Math.max(0, vel.y);
    grounded = true;
  }
  return grounded;
}

function checkHazards(pos) {
  for (const h of hazards) {
    if (Math.abs(pos.x - h.x) < h.w && Math.abs(pos.z - h.z) < h.d && Math.abs(pos.y - h.y) < 2) return true;
  }
  return false;
}

function checkCheckpoint(pos) {
  const next = Math.min(44, currentCheckpoint + 1);
  const target = checkpointPositions[next];
  if (!target) return;
  if (pos.distanceTo(target) < 2.8) {
    currentCheckpoint = next;
    respawnPoint = target.clone();
    saveProgress();
    updateProgressUI();
    showBanner(`Checkpoint ${currentCheckpoint + 1}!`);
    spawnConfetti(target.clone().add(new THREE.Vector3(0, 2, 0)));
    playTone(880, 0.18, 'triangle', 0.3);
  }
}

function respawn() {
  player.mesh.position.copy(respawnPoint).add(new THREE.Vector3(0, 2, 0));
  player.velocity.set(0, 0, 0);
  player.invulnTime = 1.2;
  playTone(220, 0.2, 'sawtooth', 0.2);
}

// ---------------------------
// Gameplay loop
// ---------------------------
let lastTime = performance.now();
const fixedStep = 1/60;
let accumulator = 0;

function update(dt) {
  if (bannerTimer > 0) {
    bannerTimer -= dt;
    if (bannerTimer <= 0) checkpointBanner.classList.add('hidden');
  }

  // stamina & sprint
  const sprinting = keys['ShiftLeft'] && player.stamina > 0.08;
  player.stamina += (sprinting ? -dt * 0.6 : dt * 0.35);
  player.stamina = THREE.MathUtils.clamp(player.stamina, 0, 1);
  staminaBar.style.width = `${player.stamina * 100}%`;

  // movement input
  const forward = (keys['KeyW'] ? 1 : 0) - (keys['KeyS'] ? 1 : 0);
  const strafe = (keys['KeyD'] ? 1 : 0) - (keys['KeyA'] ? 1 : 0);
  const dir = new THREE.Vector3(strafe, 0, forward);
  if (dir.lengthSq() > 0) dir.normalize();

  const speed = (sprinting ? 9 : 6);
  const move = dir.clone().multiplyScalar(speed * dt);
  const yaw = cameraYaw;
  const sin = Math.sin(yaw), cos = Math.cos(yaw);
  const worldMove = new THREE.Vector3(
    move.x * cos - move.z * sin,
    0,
    move.x * sin + move.z * cos
  );
  player.mesh.position.add(worldMove);

  // gravity
  player.velocity.y -= 18 * dt;
  player.mesh.position.y += player.velocity.y * dt;
  player.onGround = isOnPlatform(player.mesh.position, player.velocity);
  if (player.onGround) {
    if (player.velocity.y < -12) playTone(160, 0.1, 'triangle', 0.15);
    player.velocity.y = 0;
    if (keys['Space']) {
      player.velocity.y = 10;
      playTone(660, 0.12, 'square', 0.2);
    }
  }

  // limits
  if (player.mesh.position.y < -20) respawn();

  // hazards & checkpoints
  if (checkHazards(player.mesh.position)) respawn();
  checkCheckpoint(player.mesh.position);

  // enemies update
  updateMummies(dt);

  // coins
  for (const coin of coins) {
    if (coin.collected) continue;
    coin.mesh.rotation.z += dt * 4;
    if (coin.mesh.position.distanceTo(player.mesh.position) < 1.5) {
      coin.collected = true;
      coin.mesh.visible = false;
      playTone(1200, 0.15, 'triangle', 0.25);
      showBanner('Shiny Ankh!');
    }
  }

  // particles
  for (const c of confetti) {
    c.life -= dt;
    if (c.life <= 0) { scene.remove(c.mesh); continue; }
    c.mesh.position.addScaledVector(c.vel, dt);
    c.vel.y -= 6 * dt;
  }
  for (let i = confetti.length -1; i >=0; i--) {
    if (confetti[i].life <= 0) confetti.splice(i,1);
  }

  // camera follow
  updateCamera(dt, sprinting);
  animatePlayer(dir.lengthSq(), sprinting, dt);

  // guidance arrow & trail
  updateGuidance();

  if (player.invulnTime > 0) player.invulnTime -= dt;
}

function updateMummies(dt) {
  for (const m of mummies) {
    const playerDist = m.mesh.position.distanceTo(player.mesh.position);
    const targetDir = new THREE.Vector3();
    if (playerDist < m.stats.detect) {
      targetDir.subVectors(player.mesh.position, m.mesh.position).setY(0).normalize();
    } else {
      // simple patrol oscillation
      targetDir.set(Math.sin(performance.now() * 0.001 + m.mesh.position.z), 0, Math.cos(performance.now() * 0.001)).normalize();
    }
    m.mesh.position.addScaledVector(targetDir, m.stats.speed * dt);
    if (playerDist < 1.4 && player.invulnTime <= 0) respawn();
  }
}

function updateCamera(dt, sprinting) {
  const target = player.mesh.position.clone().add(new THREE.Vector3(0, 2.2, 0));
  const offset = new THREE.Vector3(
    Math.sin(cameraYaw) * Math.cos(cameraPitch),
    Math.sin(cameraPitch),
    Math.cos(cameraYaw) * Math.cos(cameraPitch)
  ).multiplyScalar(cameraDistance);
  const desired = target.clone().add(offset);
  camera.position.lerp(desired, 0.12);
  camera.lookAt(target);
  camera.fov = THREE.MathUtils.lerp(camera.fov, sprinting ? 72 : 65, 0.1);
  camera.updateProjectionMatrix();
}

function animatePlayer(moving, sprinting, dt) {
  const limbs = player.mesh.userData.limbs;
  if (!limbs) return;
  const speed = moving ? (sprinting ? 10 : 6) : 0;
  const swing = Math.sin(performance.now() * 0.01 * speed) * (moving ? 0.8 : 0.1);
  limbs.leftArm.rotation.x = swing;
  limbs.rightArm.rotation.x = -swing;
  limbs.leftLeg.rotation.x = -swing;
  limbs.rightLeg.rotation.x = swing;
}

function updateGuidance() {
  const next = Math.min(44, currentCheckpoint + 1);
  const target = checkpointPositions[next];
  if (!target) return;
  const dir = target.clone().sub(player.mesh.position).setY(0).normalize();
  const angle = Math.atan2(dir.x, dir.z);
  const deg = THREE.MathUtils.radToDeg(angle);
  arrowUI.style.transform = `rotate(${deg}deg)`;
}

// ---------------------------
// Game loop runner
// ---------------------------
function loop(now) {
  const delta = Math.min(0.05, (now - lastTime) / 1000);
  lastTime = now;
  accumulator += delta;
  if (!paused) {
    while (accumulator >= fixedStep) {
      update(fixedStep);
      accumulator -= fixedStep;
    }
    updateGuide();
  }
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// ---------------------------
// Guidance visuals (floating orb)
// ---------------------------
const guideGeo = new THREE.SphereGeometry(0.3, 10, 10);
const guideMat = new THREE.MeshBasicMaterial({ color: 0x99e5ff, transparent: true, opacity: 0.7 });
const guide = new THREE.Mesh(guideGeo, guideMat);
scene.add(guide);

// ---------------------------
// UI tutorial hints
// ---------------------------
const tutorialHints = [
  'WASD to move, mouse to look',
  'Space to jump, Shift to sprint',
  'Reach glowing obelisks!',
];

function updateGuide() {
  const next = Math.min(44, currentCheckpoint + 1);
  const target = checkpointPositions[next];
  if (!target) return;
  const pulse = Math.sin(performance.now() * 0.003) * 0.3 + 0.7;
  guide.material.opacity = pulse;
  guide.position.copy(target).add(new THREE.Vector3(0, 2 + pulse, 0));
}

function showTutorials() {
  if (currentCheckpoint < tutorialHints.length) {
    showBanner(tutorialHints[currentCheckpoint]);
  }
}

// ---------------------------
// Window resize
// ---------------------------
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------------------------
// Start screen continue availability
// ---------------------------
continueBtn.disabled = !localStorage.getItem('parkourProgress');

// Show tutorial on first start
showTutorials();
