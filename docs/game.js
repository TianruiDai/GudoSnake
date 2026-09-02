const canvas = document.querySelector("#gameCanvas");
const ctx = canvas.getContext("2d");
const overlay = document.querySelector("#gameOverlay");
const overlayTitle = document.querySelector("#overlayTitle");
const overlayMessage = document.querySelector("#overlayMessage");
const overlayButton = document.querySelector("#overlayButton");
const scoreValue = document.querySelector("#scoreValue");
const bestValue = document.querySelector("#bestValue");
const roundState = document.querySelector("#roundState");
const audioStatus = document.querySelector("#audioStatus");
const soundCount = document.querySelector("#soundCount");
const volumeRange = document.querySelector("#volumeRange");
const volumeValue = document.querySelector("#volumeValue");
const gudoImage = new Image();
gudoImage.src = "assets/monster.jpg";

const GRID = 32;
const CELL = canvas.width / GRID;
const COLORS = {
  background: "#121229",
  grid: "#282448",
  gridBright: "#3b3565",
  lime: "#b7ff4a",
  cyan: "#41efdf",
  pink: "#ff4ba7",
  orange: "#ffad4e",
  ink: "#f2f0ff",
};

const soundFiles = [
  "sounds/click/HELP/HELP.mp3",
  "sounds/click/NO/NO.mp3",
  "sounds/click/NO/NO2.mp3",
  "sounds/click/NO/fart-meme-sound.mp3",
  "sounds/click/YES/YES.mp3",
  "sounds/click/YES/anime-ahh.mp3",
  "sounds/click/YES/anime-wow-sound-effect.mp3",
  "sounds/click/YES/eeeeeee-gangnam-style.mp3",
  "sounds/click/YES/gunshotjbudden.mp3",
  "sounds/click/YES/m-e-o-w.mp3",
  "sounds/click/YES/mamboman-bo-shi-ge-ju-matikanetannhauser.mp3",
  "sounds/click/YES/man-snoring-meme_ctrllNn.mp3",
  "sounds/click/win/anime-wow-sound-effect.mp3",
  "sounds/click/win/bababooey-sound-effect.mp3",
  "sounds/click/win/deg-deg_4M6Cojn.mp3",
  "sounds/click/win/faaah.mp3",
  "sounds/click/win/galaxy-brain-meme.mp3",
  "sounds/click/win/gu-gu-ga-ga_Hyvo7id.mp3",
  "sounds/click/win/hb128.mp3",
  "sounds/click/win/hehehehhehehehhehehheheehehe.mp3",
  "sounds/click/win/michael-jackson-hee-hee.mp3",
  "sounds/click/win/no-batidao-zxkai.mp3",
  "sounds/click/win/scheming-weasel-faster-1-mp3cutn-mp3cut.mp3",
  "sounds/click/win/tiki-tiki.mp3",
  "sounds/click/win/vine-boom-sound-effect_KT89XIq.mp3",
  "sounds/click/win/yang-guang-cai-hong-xiao-bai-ma.mp3",
  "sounds/click/win/youre-beautiful-groan-tube.mp3",
  "sounds/click/win/yt1s_wU4BGgD.mp3",
  "sounds/click/win/yuan-shou-de-fen-nu.mp3",
];

let snake = [];
let direction = { x: 1, y: 0 };
let food = { x: 0, y: 0 };
let gudo = { x: 0, y: 0 };
let score = 0;
let best = Number(localStorage.getItem("gudoSnakeBest") || 0);
let status = "idle";
let deathReason = "";
let moveTimer = 0;
let gudoTimer = 0;
let flashTimer = 0;
let lastFrame = 0;
let particles = [];
let volume = 0.75;
let activeAudio = null;

soundCount.textContent = String(soundFiles.length).padStart(2, "0");
bestValue.textContent = String(best).padStart(3, "0");

function randomInt(max) {
  return Math.floor(Math.random() * max);
}

function gudoCells(position = gudo) {
  return [
    position,
    { x: position.x + 1, y: position.y },
    { x: position.x, y: position.y + 1 },
    { x: position.x + 1, y: position.y + 1 },
  ];
}

function sameCell(a, b) {
  return a.x === b.x && a.y === b.y;
}

function snakeHas(cell) {
  return snake.some((segment) => sameCell(segment, cell));
}

function gudoHas(cell, position = gudo) {
  return gudoCells(position).some((gudoCell) => sameCell(gudoCell, cell));
}

function resetGame() {
  const center = Math.floor(GRID / 2);
  snake = Array.from({ length: 4 }, (_, index) => ({
    x: center - index,
    y: center,
  }));
  direction = { x: 1, y: 0 };
  score = 0;
  status = "playing";
  deathReason = "";
  moveTimer = 0;
  gudoTimer = 0;
  flashTimer = 0;
  particles = [];
  placeGudo();
  placeFood();
  updateHud();
  overlay.hidden = true;
}

function placeGudo() {
  do {
    gudo = {
      x: randomInt(GRID - 1),
      y: randomInt(GRID - 1),
    };
  } while (gudoCells().some(snakeHas));
}

function placeFood() {
  do {
    food = { x: randomInt(GRID), y: randomInt(GRID) };
  } while (snakeHas(food) || gudoHas(food));
}

function playRandomSound() {
  if (activeAudio) {
    activeAudio.pause();
    activeAudio.currentTime = 0;
  }
  const sound = new Audio(soundFiles[randomInt(soundFiles.length)]);
  sound.volume = volume;
  activeAudio = sound;
  sound.play().catch(() => {
    audioStatus.textContent = "CLICK START TO ARM AUDIO";
  });
}

function unlockAudio() {
  audioStatus.textContent = "29 TRACKS ARMED / RANDOM";
  const silentSound = new Audio(soundFiles[0]);
  silentSound.volume = 0.001;
  silentSound
    .play()
    .then(() => {
      silentSound.pause();
      silentSound.currentTime = 0;
    })
    .catch(() => {});
}

function createParticles(cell) {
  for (let index = 0; index < 16; index += 1) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 35 + Math.random() * 75;
    particles.push({
      x: (cell.x + 0.5) * CELL,
      y: (cell.y + 0.5) * CELL,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 0.35 + Math.random() * 0.4,
      size: 2 + randomInt(4),
    });
  }
}

function updateParticles(delta) {
  particles = particles.filter((particle) => {
    particle.life -= delta;
    particle.x += particle.vx * delta;
    particle.y += particle.vy * delta;
    particle.vy += 75 * delta;
    return particle.life > 0;
  });
}

function distanceToHead(position) {
  return Math.abs(position.x - snake[0].x) + Math.abs(position.y - snake[0].y);
}

function moveGudo() {
  const choices = [
    { x: 0, y: -1 },
    { x: 0, y: 1 },
    { x: -1, y: 0 },
    { x: 1, y: 0 },
  ].sort(() => Math.random() - 0.5);
  const validMoves = choices
    .map((step) => ({ x: gudo.x + step.x, y: gudo.y + step.y }))
    .filter(
      (candidate) =>
        candidate.x >= 0 &&
        candidate.y >= 0 &&
        candidate.x <= GRID - 2 &&
        candidate.y <= GRID - 2 &&
        !gudoCells(candidate).some(snakeHas) &&
        !gudoHas(food, candidate),
    )
    .map((candidate) => ({
      candidate,
      distance: distanceToHead(candidate),
    }))
    .sort((a, b) => a.distance - b.distance);

  if (validMoves.length === 0) {
    return;
  }
  if (Math.random() < 0.72) {
    const bestDistance = validMoves[0].distance;
    const pursuitMoves = validMoves.filter(
      (move) => move.distance <= bestDistance + 1,
    );
    gudo = pursuitMoves[randomInt(pursuitMoves.length)].candidate;
  } else {
    gudo = validMoves[randomInt(validMoves.length)].candidate;
  }
}

function endRun(reason) {
  status = "gameover";
  deathReason = reason;
  playRandomSound();
  showOverlay(reason, "Impact sound deployed. The face wins this round.", "RESTART");
  updateHud();
}

function stepSnake() {
  const newHead = {
    x: snake[0].x + direction.x,
    y: snake[0].y + direction.y,
  };
  const eating = sameCell(newHead, food);
  const wallHit =
    newHead.x < 0 ||
    newHead.y < 0 ||
    newHead.x >= GRID ||
    newHead.y >= GRID;
  const body = eating ? snake : snake.slice(0, -1);
  const selfHit = body.some((segment) => sameCell(segment, newHead));
  const gudoHit = gudoHas(newHead);

  if (wallHit || selfHit || gudoHit) {
    endRun(wallHit ? "WALL IMPACT" : gudoHit ? "GUDO GOT YOU" : "SELF DESTRUCT");
    return;
  }

  snake.unshift(newHead);
  if (eating) {
    score += 1;
    best = Math.max(best, score);
    localStorage.setItem("gudoSnakeBest", String(best));
    createParticles(food);
    playRandomSound();
    flashTimer = 0.3;
    placeFood();
  } else {
    snake.pop();
  }
  updateHud();
}

function updateHud() {
  scoreValue.textContent = String(score).padStart(3, "0");
  bestValue.textContent = String(best).padStart(3, "0");
  roundState.textContent =
    status === "playing"
      ? "ACTIVE"
      : status === "paused"
        ? "PAUSED"
        : status === "gameover"
          ? "GAME OVER"
          : "STANDBY";
}

function showOverlay(title, message, buttonText) {
  overlayTitle.textContent = title;
  overlayMessage.textContent = message;
  overlayButton.textContent = buttonText;
  overlay.hidden = false;
}

function togglePause() {
  if (status === "playing") {
    status = "paused";
    showOverlay("PAUSED", "The face is still watching.", "RESUME");
  } else if (status === "paused") {
    status = "playing";
    overlay.hidden = true;
  }
  updateHud();
}

function drawBackground() {
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, "#121229");
  gradient.addColorStop(1, "#19152f");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let x = 0; x < GRID; x += 1) {
    for (let y = 0; y < GRID; y += 1) {
      if ((x + y) % 2 === 0) {
        ctx.fillStyle = "rgba(255, 255, 255, 0.018)";
        ctx.fillRect(x * CELL, y * CELL, CELL, CELL);
      }
    }
  }
  for (let index = 0; index <= GRID; index += 1) {
    ctx.strokeStyle = index % 4 === 0 ? COLORS.gridBright : COLORS.grid;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(index * CELL, 0);
    ctx.lineTo(index * CELL, canvas.height);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, index * CELL);
    ctx.lineTo(canvas.width, index * CELL);
    ctx.stroke();
  }
  ctx.strokeStyle = COLORS.cyan;
  ctx.lineWidth = 2;
  ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);
}

function drawFood(time) {
  const centerX = (food.x + 0.5) * CELL;
  const centerY = (food.y + 0.5) * CELL;
  const pulse = 1 + Math.sin(time * 7) * 0.15;
  const glow = ctx.createRadialGradient(centerX, centerY, 2, centerX, centerY, 28);
  glow.addColorStop(0, "rgba(255, 75, 167, 0.5)");
  glow.addColorStop(1, "rgba(255, 75, 167, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(centerX, centerY, 28, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = COLORS.pink;
  ctx.beginPath();
  ctx.arc(centerX, centerY, 7 * pulse, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#ffd2ec";
  ctx.beginPath();
  ctx.arc(centerX - 2, centerY - 2, 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = COLORS.lime;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(centerX, centerY - 7);
  ctx.lineTo(centerX + 4, centerY - 11);
  ctx.stroke();
}

function drawSnake() {
  snake.forEach((segment, index) => {
    const isHead = index === 0;
    const fade = Math.max(0.38, 1 - index / Math.max(10, snake.length * 1.3));
    const x = segment.x * CELL + 2;
    const y = segment.y * CELL + 2;
    ctx.fillStyle = isHead
      ? COLORS.lime
      : `rgb(${Math.round(45 * fade)}, ${Math.round(216 * fade + 20)}, ${Math.round(184 * fade + 25)})`;
    ctx.shadowColor = isHead ? COLORS.lime : COLORS.cyan;
    ctx.shadowBlur = isHead ? 16 : 4;
    ctx.beginPath();
    ctx.roundRect(x, y, CELL - 4, CELL - 4, 6);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = isHead ? "#efffb6" : "#5cffe0";
    ctx.lineWidth = 1;
    ctx.stroke();

    if (isHead) {
      const eyeX = x + (direction.x > 0 ? 14 : direction.x < 0 ? 5 : 9);
      const eyeY = y + (direction.y > 0 ? 14 : direction.y < 0 ? 5 : 9);
      ctx.fillStyle = "#080812";
      ctx.beginPath();
      ctx.arc(eyeX, eyeY, 2, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function drawGudo(time) {
  const x = gudo.x * CELL;
  const y = gudo.y * CELL;
  const jitter = Math.sin(time * 19) * 2;
  ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
  ctx.fillRect(x - 4, y - 4, CELL * 2 + 8, CELL * 2 + 8);
  ctx.strokeStyle = COLORS.orange;
  ctx.lineWidth = 2;
  ctx.strokeRect(x - 4, y - 4, CELL * 2 + 8, CELL * 2 + 8);
  if (gudoImage.complete) {
    ctx.drawImage(gudoImage, x + jitter, y, CELL * 2, CELL * 2);
  }
  ctx.strokeStyle = COLORS.pink;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x - 4, y - 4);
  ctx.lineTo(x + CELL * 2 + 4, y + CELL * 2 + 4);
  ctx.moveTo(x + CELL * 2 + 4, y - 4);
  ctx.lineTo(x - 4, y + CELL * 2 + 4);
  ctx.stroke();
}

function drawParticles() {
  particles.forEach((particle) => {
    ctx.globalAlpha = Math.max(0, particle.life * 1.7);
    ctx.fillStyle = COLORS.pink;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

function render(time) {
  drawBackground();
  drawFood(time);
  drawGudo(time);
  drawSnake();
  drawParticles();
  if (flashTimer > 0) {
    ctx.fillStyle = `rgba(255, 75, 167, ${flashTimer * 0.18})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
}

function frame(timestamp) {
  const delta = Math.min(0.1, (timestamp - lastFrame) / 1000 || 0);
  lastFrame = timestamp;
  if (status === "playing") {
    const turbo = window.pressedKeys.has("Shift");
    const snakeInterval = turbo ? 0.065 : 0.11;
    moveTimer += delta;
    gudoTimer += delta;
    while (moveTimer >= snakeInterval) {
      moveTimer -= snakeInterval;
      stepSnake();
      if (status !== "playing") {
        break;
      }
    }
    if (status === "playing" && gudoTimer >= 0.48) {
      gudoTimer = 0;
      moveGudo();
    }
    updateParticles(delta);
    flashTimer = Math.max(0, flashTimer - delta);
  }
  render(timestamp / 1000);
  window.requestAnimationFrame(frame);
}

window.pressedKeys = new Set();
window.addEventListener("keydown", (event) => {
  window.pressedKeys.add(event.key);
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(event.key)) {
    event.preventDefault();
  }
  if (event.key === " " && status !== "gameover" && status !== "idle") {
    togglePause();
    return;
  }
  if (event.key.toLowerCase() === "r") {
    unlockAudio();
    resetGame();
    return;
  }
  if (status !== "playing") {
    return;
  }
  const requested = {
    w: { x: 0, y: -1 },
    ArrowUp: { x: 0, y: -1 },
    s: { x: 0, y: 1 },
    ArrowDown: { x: 0, y: 1 },
    a: { x: -1, y: 0 },
    ArrowLeft: { x: -1, y: 0 },
    d: { x: 1, y: 0 },
    ArrowRight: { x: 1, y: 0 },
  }[event.key];
  if (requested && (requested.x !== -direction.x || requested.y !== -direction.y)) {
    direction = requested;
  }
});

window.addEventListener("keyup", (event) => {
  window.pressedKeys.delete(event.key);
});

overlayButton.addEventListener("click", () => {
  unlockAudio();
  if (status === "paused") {
    togglePause();
  } else {
    resetGame();
  }
});

volumeRange.addEventListener("input", () => {
  volume = Number(volumeRange.value) / 100;
  volumeValue.textContent = `${volumeRange.value}%`;
});

updateHud();
requestAnimationFrame(frame);
