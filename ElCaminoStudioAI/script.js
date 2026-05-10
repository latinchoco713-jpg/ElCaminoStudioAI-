const tracks = [
  {
    title: "El Camino - Intro",
    file: "assets/music/el-camino.mp3",
    emotion: "calm",
  },
  {
    title: "Dentro de la tormenta",
    file: "assets/music/soy-tormenta.mp3",
    emotion: "storm",
  },
  {
    title: "Todo esta conectado",
    file: "assets/music/el-camino.mp3",
    emotion: "connected",
  },
];

const audio = document.getElementById("album-audio");
const canvas = document.getElementById("visualizer-canvas");
const canvasContext = canvas.getContext("2d");
const playButtons = Array.from(document.querySelectorAll(".play-button"));
const trackCards = Array.from(document.querySelectorAll(".track-card"));
const energyValues = Array.from(document.querySelectorAll(".energy-value"));
const generateButton = document.getElementById("generate-button");
const stopButton = document.getElementById("stop-button");
const message = document.getElementById("mensaje");
const lyrics = document.getElementById("letra");
const videoAudioInput = document.getElementById("video-audio-input");
const videoGenerateButton = document.getElementById("video-generate-button");
const videoStatus = document.getElementById("video-status");
const videoResult = document.getElementById("video-result");

let currentTrack = null;
let isPlaying = false;
let synth;
let sequence;
let audioContext;
let analyser;
let frequencyData;
let analyserReady = false;
let visualEnergy = 0;
let animationStarted = false;
let beat = false;
let lastBeatTime = 0;
let scene = 0;
const threshold = 160;
const particles = [];

function resizeCanvas() {
  const pixelRatio = window.devicePixelRatio || 1;
  canvas.width = Math.floor(window.innerWidth * pixelRatio);
  canvas.height = Math.floor(window.innerHeight * pixelRatio);
  canvasContext.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  createParticles(100);
}

function createParticles(count = 80) {
  particles.length = 0;

  for (let i = 0; i < count; i += 1) {
    particles.push({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      size: Math.random() * 2,
      speed: Math.random() * 0.5 + 0.2,
      opacity: Math.random() * 0.5 + 0.2,
      drift: (Math.random() - 0.5) * 0.4,
    });
  }
}

function getSceneStyle() {
  if (scene === 0) return "blue";
  if (scene === 1) return "purple";
  return "red";
}

function getVisualizerColor(alpha) {
  const sceneColors = {
    blue: `rgba(0, 150, 255, ${alpha})`,
    purple: `rgba(168, 85, 247, ${alpha})`,
    red: `rgba(255, 45, 85, ${alpha})`,
  };

  if (beat) return sceneColors[getSceneStyle()];

  const colors = {
    calm: sceneColors.blue,
    storm: sceneColors.red,
    connected: sceneColors.purple,
  };

  return colors[tracks[currentTrack]?.emotion || "calm"];
}

function drawVisualizer() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const centerX = width / 2;
  const centerY = height / 2;
  const baseRadius = Math.min(width, height) * 0.22;
  const data = frequencyData || new Uint8Array(128);
  const bars = 96;

  canvasContext.clearRect(0, 0, width, height);
  canvasContext.save();
  canvasContext.globalCompositeOperation = "lighter";

  const glow = canvasContext.createRadialGradient(centerX, centerY, 0, centerX, centerY, baseRadius + visualEnergy * 1.8);
  glow.addColorStop(0, getVisualizerColor(Math.min(0.26, visualEnergy / 420)));
  glow.addColorStop(0.62, getVisualizerColor(Math.min(0.12, visualEnergy / 900)));
  glow.addColorStop(1, "rgba(0, 0, 0, 0)");
  canvasContext.fillStyle = glow;
  canvasContext.fillRect(0, 0, width, height);

  canvasContext.lineWidth = 1.4;
  canvasContext.strokeStyle = getVisualizerColor(isPlaying ? 0.44 : 0.16);
  canvasContext.beginPath();

  for (let i = 0; i <= bars; i += 1) {
    const value = data[i % data.length] || 0;
    const angle = (i / bars) * Math.PI * 2;
    const pulse = isPlaying ? value * 0.34 : Math.sin(Date.now() / 900 + i) * 5;
    const radius = baseRadius + pulse + visualEnergy * 0.18;
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;

    if (i === 0) {
      canvasContext.moveTo(x, y);
    } else {
      canvasContext.lineTo(x, y);
    }
  }

  canvasContext.closePath();
  canvasContext.stroke();

  for (let i = 0; i < bars; i += 1) {
    const value = data[i % data.length] || 0;
    const angle = (i / bars) * Math.PI * 2;
    const barLength = isPlaying ? value * 0.42 : 8;
    const innerRadius = baseRadius + 22;
    const outerRadius = innerRadius + barLength;
    const x1 = centerX + Math.cos(angle) * innerRadius;
    const y1 = centerY + Math.sin(angle) * innerRadius;
    const x2 = centerX + Math.cos(angle) * outerRadius;
    const y2 = centerY + Math.sin(angle) * outerRadius;

    canvasContext.strokeStyle = getVisualizerColor(isPlaying ? 0.18 + value / 620 : 0.08);
    canvasContext.beginPath();
    canvasContext.moveTo(x1, y1);
    canvasContext.lineTo(x2, y2);
    canvasContext.stroke();
  }

  updateParticles(width, height);
  drawParticles();
  drawLightning(width, height);
  canvasContext.restore();
  requestAnimationFrame(drawVisualizer);
}

function updateParticles(width, height) {
  const intensity = Math.min(1, visualEnergy / 255);

  particles.forEach((particle) => {
    particle.y -= particle.speed + intensity * 2;
    particle.x += (Math.random() - 0.5) * 0.5;

    if (particle.y < 0) {
      particle.y = height;
      particle.x = Math.random() * width;
    }

    if (particle.x < -12) particle.x = width + 12;
    if (particle.x > width + 12) particle.x = -12;
  });
}

function drawParticles() {
  const intensity = Math.min(1, visualEnergy / 255);

  canvasContext.save();
  canvasContext.globalCompositeOperation = "lighter";

  particles.forEach((particle) => {
    canvasContext.beginPath();
    canvasContext.arc(particle.x, particle.y, particle.size + intensity * 2, 0, Math.PI * 2);
    canvasContext.fillStyle = `rgba(150, 200, 255, ${Math.min(1, particle.opacity + intensity)})`;
    canvasContext.fill();
  });

  canvasContext.restore();
}
function detectBeat(dataArray) {
  const max = Math.max(...dataArray);
  const now = Date.now();

  if (max > threshold && now - lastBeatTime > 250) {
    lastBeatTime = now;
    beat = true;
    scene = (scene + 1) % 3;
    document.body.dataset.scene = getSceneStyle();
    document.body.classList.add("is-beat");

    setTimeout(() => {
      beat = false;
      document.body.classList.remove("is-beat");
    }, 100);
  }
}

function drawBeatPulse(width, height) {
  if (!beat) return;

  canvasContext.save();
  canvasContext.globalCompositeOperation = "lighter";
  canvasContext.shadowBlur = 60;
  canvasContext.shadowColor = "cyan";
  canvasContext.fillStyle = "rgba(0, 150, 255, 0.18)";
  canvasContext.fillRect(0, 0, width, height);
  canvasContext.restore();
}

function drawLightning(width, height) {
  if (!isPlaying) return;

  const intensity = Math.min(1, visualEnergy / 255);
  const bolts = Math.floor(intensity * 8) + (beat ? 2 : 0);

  canvasContext.save();
  canvasContext.shadowBlur = beat ? 60 : 30;
  canvasContext.shadowColor = "cyan";
  canvasContext.lineCap = "round";
  canvasContext.lineJoin = "round";

  for (let i = 0; i < bolts; i += 1) {
    canvasContext.beginPath();

    let x = Math.random() * width;
    let y = 0;

    canvasContext.moveTo(x, y);

    for (let j = 0; j < 10; j += 1) {
      x += (Math.random() - 0.5) * 80;
      y += height / 10;
      canvasContext.lineTo(x, y);
    }

    canvasContext.strokeStyle = `rgba(0, 150, 255, ${Math.min(1, 0.6 + intensity)})`;
    canvasContext.lineWidth = 2 + intensity * 4;
    canvasContext.stroke();
  }

  canvasContext.restore();
}

function ensureAnimation() {
  if (animationStarted) return;
  animationStarted = true;
  resizeCanvas();
  drawVisualizer();
}

function setEmotion(emotion) {
  document.body.classList.remove("emotion-calm", "emotion-storm", "emotion-connected");
  document.body.classList.add(`emotion-${emotion}`);
}

function setEnergy(energy) {
  visualEnergy = energy;

  const rounded = Math.round(energy);
  const alpha = Math.min(0.85, energy / 300).toFixed(3);
  const size = Math.round(36 + energy / 3);

  document.body.style.setProperty("--energy-alpha", alpha);
  document.body.style.setProperty("--energy-size", `${size}%`);
  energyValues.forEach((value) => {
    value.textContent = rounded;
  });
}

function startEnergyLoop() {
  if (!analyser || !frequencyData) return;

  analyser.getByteFrequencyData(frequencyData);

  const total = frequencyData.reduce((sum, value) => sum + value, 0);
  const average = total / frequencyData.length;

  detectBeat(frequencyData);
  setEnergy(isPlaying ? average : average * 0.65);
  requestAnimationFrame(startEnergyLoop);
}

function initAnalyzer() {
  if (analyserReady) {
    audioContext.resume();
    return;
  }

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;

  if (!AudioContextClass) {
    message.textContent = "Este navegador no soporta analisis de audio.";
    return;
  }

  audioContext = new AudioContextClass();
  const source = audioContext.createMediaElementSource(audio);

  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  frequencyData = new Uint8Array(analyser.frequencyBinCount);

  source.connect(analyser);
  analyser.connect(audioContext.destination);

  analyserReady = true;
  startEnergyLoop();
}

function updateTrackUI() {
  playButtons.forEach((button, index) => {
    const active = currentTrack === index && isPlaying;
    button.setAttribute("aria-label", `${active ? "Pausar" : "Reproducir"} ${tracks[index].title}`);
    button.querySelector(".icon").className = `icon ${active ? "icon-pause" : "icon-play"}`;
  });

  trackCards.forEach((card, index) => {
    card.classList.toggle("is-active", currentTrack === index);
  });
}

function playTrack(index) {
  const track = tracks[index];

  if (currentTrack === index && isPlaying) {
    audio.pause();
    isPlaying = false;
    updateTrackUI();
    return;
  }

  initAnalyzer();

  currentTrack = index;
  isPlaying = true;
  setEmotion(track.emotion);
  audio.src = track.file;
  audio.play().catch(() => {
    isPlaying = false;
    updateTrackUI();
    message.textContent = "No pude reproducir ese audio. Revisa que el archivo exista.";
  });
  updateTrackUI();
}

function generarMelodia() {
  if (!window.Tone) {
    message.textContent = "Tone.js no cargo. Revisa la conexion e intentalo otra vez.";
    return;
  }

  detenerMusica();

  if (!synth) {
    synth = new Tone.Synth({
      oscillator: { type: "triangle" },
      envelope: { attack: 0.02, decay: 0.12, sustain: 0.25, release: 0.8 },
    }).toDestination();
  }

  Tone.start();

  const palettes = {
    calm: ["C4", "E4", "G4", "B4", "A4", "G4", "E4", "D4"],
    storm: ["D3", "F4", "A3", "C5", "Bb3", "G4", "E4", "D4"],
    connected: ["A3", "C4", "E4", "G4", "B4", "E5", "D5", "A4"],
  };

  const emotion = tracks[currentTrack]?.emotion || "calm";

  sequence = new Tone.Sequence((time, note) => {
    synth.triggerAttackRelease(note, "8n", time);
  }, palettes[emotion], "4n");

  sequence.loop = true;
  sequence.start(0);
  Tone.Transport.start();

  message.textContent = "Melodia generada desde la emocion actual.";
  lyrics.innerHTML = "<p>En el camino de la vida, la musica nos guia.</p>";
}

function detenerMusica() {
  if (sequence) {
    sequence.stop();
    sequence.dispose();
    sequence = null;
  }

  if (window.Tone) {
    Tone.Transport.stop();
  }
}

async function generarVideo() {
  const file = videoAudioInput.files[0];

  if (!file) {
    videoStatus.textContent = "Selecciona un audio primero.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  videoGenerateButton.disabled = true;
  videoStatus.textContent = "Generando video... esto puede tardar.";
  videoResult.hidden = true;

  try {
    const response = await fetch("/generate-video", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "No se pudo generar el video.");
    }

    videoStatus.textContent = `Video listo. Estilo: ${data.style || "cinematico"}.`;
    videoResult.href = data.video_url;
    videoResult.hidden = false;
  } catch (error) {
    videoStatus.textContent = error.message;
  } finally {
    videoGenerateButton.disabled = false;
  }
}

window.addEventListener("resize", resizeCanvas);
playButtons.forEach((button) => {
  button.addEventListener("click", () => playTrack(Number(button.dataset.index)));
});

generateButton.addEventListener("click", generarMelodia);
stopButton.addEventListener("click", detenerMusica);
videoGenerateButton.addEventListener("click", generarVideo);
audio.addEventListener("ended", () => {
  isPlaying = false;
  setEnergy(0);
  updateTrackUI();
});

ensureAnimation();















