import base64
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🎛️ Multi-Stem Player (Tone.js)")

# 1. Upload Audio
st.subheader("1. Upload Stem Audio")
cols = st.columns(4)
default_names = ["Track 1 (Vocal)", "Track 2 (Drums)", "Track 3 (Bass)", "Track 4 (Other)"]
stems_data = {}

for i, col in enumerate(cols):
    uploaded_file = col.file_uploader(
        f"Upload {default_names[i]}", 
        type=["mp3", "wav", "ogg", "flac"], 
        key=f"uploader_{i}"
    )
    if uploaded_file is not None:
        track_name = default_names[i]
        b64_str = base64.b64encode(uploaded_file.read()).decode()
        stems_data[track_name] = f"data:{uploaded_file.type};base64,{b64_str}"

# 2. Mixer Controls Component
if stems_data:
    st.markdown("---")
    st.subheader("2. Multi-Track Mixer Controls")
    
    stems_json = json.dumps(stems_data)
    
    tone_js_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
      <style>
        body {{ 
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
          background: #0e1117; 
          color: white; 
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
          gap: 12px;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 1px solid #30363d;
        }}
        .stem-row {{ 
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: 14px;
          background: #21262d; 
          padding: 14px 16px; 
          border-radius: 8px;
          border: 1px solid #30363d;
        }}
        .player-top {{
          display: flex;
          align-items: center;
          gap: 15px;
        }}
        .track-title {{
          width: 140px;
          flex-shrink: 0;
          font-weight: bold;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }}
        .slider-wrapper {{ 
          display: flex; 
          align-items: center; 
          gap: 12px; 
          flex-grow: 1;
        }}
        input[type=range] {{ 
          flex-grow: 1; 
          accent-color: #238636;
          cursor: pointer;
        }}
        .vol-label {{ 
          font-family: monospace; 
          font-size: 13px; 
          width: 55px; 
          text-align: right;
          color: #8b949e; 
        }}
        .controls-bottom {{
          display: flex;
          gap: 10px;
          margin-left: 155px; /* Sejajar dengan slider */
        }}
        .btn-main {{ 
          background: #238636; 
          color: white; 
          border: none; 
          padding: 10px 20px; 
          border-radius: 6px; 
          font-weight: bold; 
          cursor: pointer; 
        }}
        .btn-main:disabled {{ 
          background: #343942; 
          color: #8b949e;
          cursor: not-allowed; 
        }}
        .btn-stop {{ 
          background: #da3633; 
        }}
        .btn-toggle {{ 
          background: #30363d; 
          color: white; 
          border: 1px solid #8b949e; 
          padding: 6px 16px; 
          border-radius: 6px; 
          font-weight: 600;
          font-size: 12px;
          cursor: pointer; 
          min-width: 70px;
          text-align: center;
          transition: all 0.15s ease;
        }}
        .btn-toggle:hover {{
          filter: brightness(1.2);
        }}
        .btn-toggle.active-mute {{ 
          background: #da3633; 
          border-color: #f85149;
          color: white; 
        }}
        .btn-toggle.active-solo {{ 
          background: #d29922; 
          border-color: #f1e05a;
          color: #0d1117; 
        }}
        .status-text {{
          font-size: 14px;
          color: #8b949e;
          margin-left: 10px;
        }}
      </style>
    </head>
    <body>
    <div class="player-card">
      <div class="transport-bar">
        <button id="playBtn" class="btn-main" disabled>Memuat Audio...</button>
        <button id="stopBtn" class="btn-main btn-stop">Stop</button>
        <span id="status" class="status-text">Memproses file...</span>
      </div>
      <div id="stemsContainer"></div>
    </div>

    <script>
      const stemSources = {stems_json};
      const channels = {{}};
      const container = document.getElementById('stemsContainer');

      Object.keys(stemSources).forEach(trackName => {{
        const channel = new Tone.Channel({{ volume: 0, mute: false, solo: false }}).toDestination();
        const player = new Tone.Player(stemSources[trackName]).connect(channel);
        
        player.sync().start(0);
        channels[trackName] = channel;

        // Render Baris Track
        const row = document.createElement('div');
        row.className = 'stem-row';
        row.innerHTML = `
          <div class="player-top">
            <span class="track-title">${{trackName}}</span>
            <div class="slider-wrapper">
              <input type="range" id="vol-${{trackName}}" min="-40" max="6" value="0" step="1">
              <span class="vol-label" id="val-${{trackName}}">0 dB</span>
            </div>
          </div>
          <div class="controls-bottom">
            <button id="mute-${{trackName}}" class="btn-toggle">MUTE</button>
            <button id="solo-${{trackName}}" class="btn-toggle">SOLO</button>
          </div>
        `;
        container.appendChild(row);

        // Event Volume Slider
        document.getElementById(`vol-${{trackName}}`).oninput = (e) => {{
          const val = parseFloat(e.target.value);
          channels[trackName].volume.value = val;
          document.getElementById(`val-${{trackName}}`).innerText = (val > 0 ? "+" : "") + val + " dB";
        }};

        // Event Mute
        document.getElementById(`mute-${{trackName}}`).onclick = (e) => {{
          channels[trackName].mute = !channels[trackName].mute;
          e.target.classList.toggle('active-mute', channels[trackName].mute);
        }};

        // Event Solo
        document.getElementById(`solo-${{trackName}}`).onclick = (e) => {{
          channels[trackName].solo = !channels[trackName].solo;
          e.target.classList.toggle('active-solo', channels[trackName].solo);
        }};
      }});

      // Aktifkan Play Button jika semua audio siap
      Tone.loaded().then(() => {{
        const playBtn = document.getElementById('playBtn');
        playBtn.disabled = false;
        playBtn.innerText = 'Play All';
        document.getElementById('status').innerText = 'Siap diputar (' + Object.keys(stemSources).length + ' Track)';
      }});

      // Transport Control
      const playBtn = document.getElementById('playBtn');
      playBtn.onclick = async () => {{
        await Tone.start();
        if (Tone.Transport.state === 'started') {{ 
          Tone.Transport.pause(); 
          playBtn.innerText = 'Play All';
          document.getElementById('status').innerText = 'Di-pause';
        }} else {{ 
          Tone.Transport.start(); 
          playBtn.innerText = 'Pause';
          document.getElementById('status').innerText = 'Memutar...';
        }}
      }};

      document.getElementById('stopBtn').onclick = () => {{ 
        Tone.Transport.stop(); 
        playBtn.innerText = 'Play All';
        document.getElementById('status').innerText = 'Dihentikan (Stop)';
      }};
    </script>
    </body>
    </html>
    """
    
    # Penyesuaian tinggi iframe karena struktur bertingkat
    components.html(tone_js_code, height=140 + (len(stems_data) * 95))
else:
    st.info("👈 Silakan upload file audio di minimal satu slot track di atas.")
