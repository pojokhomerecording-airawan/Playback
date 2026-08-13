import base64
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🎛️ Streamlit Multi-Stem Player (Tone.js)")

# Helper konversi file audio lokal ke Base64 (aman untuk hosting)
def get_audio_b64(file_path):
    with open(file_path, "rb") as f:
        return f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

# CONTOH DATA:
# Ganti path file ini dengan file stem milikmu atau URL eksternal
stems_data = {
    "Vocal": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Drums": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Bass": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

# Menyusun HTML + Tone.js Component
tone_js_code = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #0e1117;
      color: #ffffff;
      margin: 0;
      padding: 10px;
    }}
    .player-card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 20px;
    }}
    .transport-bar {{
      display: flex;
      gap: 10px;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #30363d;
    }}
    .btn {{
      background: #238636;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      font-weight: bold;
      cursor: pointer;
    }}
    .btn:disabled {{ background: #343942; cursor: not-allowed; }}
    .btn-stop {{ background: #da3633; }}
    .stem-row {{
      display: grid;
      grid-template-columns: 120px 1fr 60px 60px;
      gap: 15px;
      align-items: center;
      margin-bottom: 12px;
      background: #21262d;
      padding: 10px 15px;
      border-radius: 8px;
    }}
    .btn-toggle {{
      background: #30363d;
      color: white;
      border: none;
      padding: 6px;
      border-radius: 4px;
      cursor: pointer;
    }}
    .btn-toggle.active-mute {{ background: #da3633; }}
    .btn-toggle.active-solo {{ background: #d29922; color: black; }}
    input[type=range] {{ width: 100%; }}
  </style>
</head>
<body>

<div class="player-card">
  <div class="transport-bar">
    <button id="playBtn" class="btn" disabled>Loading Audio...</button>
    <button id="stopBtn" class="btn btn-stop">Stop</button>
    <span id="status">Buffering stems...</span>
  </div>

  <div id="stemsContainer"></div>
</div>

<script>
  const stemSources = {stems_data};
  const players = {{}};
  const channels = {{}};

  const container = document.getElementById('stemsContainer');

  // 1. Inisialisasi Tone.Channel & Tone.Player untuk setiap stem
  Object.keys(stemSources).forEach(trackName => {{
    // Channel untuk mengontrol Mute, Solo, dan Volume (dalam dB)
    const channel = new Tone.Channel({{ volume: 0, mute: false, solo: false }}).toDestination();
    
    // Player yang di-bind ke Channel
    const player = new Tone.Player({{
      url: stemSources[trackName],
      onload: checkAllLoaded
    }}).connect(channel);

    // Kunci player ke master timeline Tone.Transport
    player.sync().start(0);

    players[trackName] = player;
    channels[trackName] = channel;

    // Render UI Slider & Button per Stem
    const row = document.createElement('div');
    row.className = 'stem-row';
    row.innerHTML = `
      <strong>${{trackName}}</strong>
      <input type="range" id="vol-${{trackName}}" min="-40" max="6" value="0" step="1">
      <button id="mute-${{trackName}}" class="btn-toggle">Mute</button>
      <button id="solo-${{trackName}}" class="btn-toggle">Solo</button>
    `;
    container.appendChild(row);

    // Event Listener Volume Slider
    document.getElementById(`vol-${{trackName}}`).oninput = (e) => {{
      channels[trackName].volume.value = parseFloat(e.target.value);
    }};

    // Event Listener Mute
    document.getElementById(`mute-${{trackName}}`).onclick = (e) => {{
      channels[trackName].mute = !channels[trackName].mute;
      e.target.classList.toggle('active-mute', channels[trackName].mute);
    }};

    // Event Listener Solo
    document.getElementById(`solo-${{trackName}}`).onclick = (e) => {{
      channels[trackName].solo = !channels[trackName].solo;
      e.target.classList.toggle('active-solo', channels[trackName].solo);
    }};
  }});

  let loadedCount = 0;
  function checkAllLoaded() {{
    loadedCount++;
    if (loadedCount === Object.keys(stemSources).length) {{
      document.getElementById('playBtn').disabled = false;
      document.getElementById('playBtn').innerText = 'Play All';
      document.getElementById('status').innerText = 'Ready';
    }}
  }}

  // 2. Transport Control (Play/Pause/Stop)
  const playBtn = document.getElementById('playBtn');
  playBtn.onclick = async () => {{
    await Tone.start(); // Membuka AudioContext browser
    
    if (Tone.Transport.state === 'started') {{
      Tone.Transport.pause();
      playBtn.innerText = 'Play All';
      document.getElementById('status').innerText = 'Paused';
    }} else {{
      Tone.Transport.start();
      playBtn.innerText = 'Pause';
      document.getElementById('status').innerText = 'Playing...';
    }}
  }};

  document.getElementById('stopBtn').onclick = () => {{
    Tone.Transport.stop();
    playBtn.innerText = 'Play All';
    document.getElementById('status').innerText = 'Stopped';
  }};
</script>

</body>
</html>
"""

components.html(tone_js_code, height=350)
