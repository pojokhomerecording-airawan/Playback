import base64
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🎛️ Streamlit Multi-Stem Player (with Volume Control)")

# 1. Bagian Upload Audio
st.subheader("1. Upload Stem Audio")
cols = st.columns(4)
default_names = ["Track 1 (Vocal)", "Track 2 (Drums)", "Track 3 (Bass)", "Track 4 (Other)"]
stems_data = {}

for i, col in enumerate(cols):
    uploaded_file = col.file_uploader(f"Upload {default_names[i]}", type=["mp3", "wav", "ogg"], key=f"uploader_{i}")
    if uploaded_file is not None:
        track_name = default_names[i]
        b64_str = base64.b64encode(uploaded_file.read()).decode()
        stems_data[track_name] = f"data:{uploaded_file.type};base64,{b64_str}"

# 2. Bagian Player
if stems_data:
    st.markdown("---")
    st.subheader("2. Stem Mixer")
    stems_json = json.dumps(stems_data)
    
    tone_js_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.49/Tone.js"></script>
      <style>
        body {{ font-family: sans-serif; background: #0e1117; color: white; padding: 10px; }}
        .player-card {{ background: #161b22; border-radius: 12px; padding: 20px; }}
        .stem-row {{ 
            display: grid; 
            grid-template-columns: 140px 1fr 80px 60px 60px; 
            gap: 15px; align-items: center; margin-bottom: 15px;
            background: #21262d; padding: 10px; border-radius: 8px;
        }}
        .slider-wrapper {{ display: flex; align-items: center; gap: 10px; }}
        input[type=range] {{ flex-grow: 1; }}
        .vol-label {{ font-family: monospace; font-size: 12px; min-width: 40px; color: #888; }}
        .btn {{ background: #238636; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; }}
        .btn-toggle {{ background: #30363d; color: white; border: none; padding: 6px; border-radius: 4px; cursor: pointer; }}
        .active-mute {{ background: #da3633; }}
        .active-solo {{ background: #d29922; color: black; }}
      </style>
    </head>
    <body>
    <div class="player-card">
      <div style="margin-bottom:20px;">
        <button id="playBtn" class="btn" disabled>Loading...</button>
        <button id="stopBtn" class="btn" style="background:#da3633;">Stop</button>
      </div>
      <div id="stemsContainer"></div>
    </div>

    <script>
      const stemSources = {stems_json};
      const channels = {{}};
      const container = document.getElementById('stemsContainer');

      Object.keys(stemSources).forEach(trackName => {{
        const channel = new Tone.Channel({{ volume: 0 }}).toDestination();
        const player = new Tone.Player(stemSources[trackName]).connect(channel);
        player.sync().start(0);
        channels[trackName] = channel;

        const row = document.createElement('div');
        row.className = 'stem-row';
        row.innerHTML = `
          <strong>${{trackName}}</strong>
          <div class="slider-wrapper">
            <input type="range" id="vol-${{trackName}}" min="-40" max="6" value="0" step="1">
            <span class="vol-label" id="val-${{trackName}}">0 dB</span>
          </div>
          <button id="mute-${{trackName}}" class="btn-toggle">Mute</button>
          <button id="solo-${{trackName}}" class="btn-toggle">Solo</button>
        `;
        container.appendChild(row);

        // Logic Volume + Label
        document.getElementById(`vol-${{trackName}}`).oninput = (e) => {{
          const val = parseFloat(e.target.value);
          channels[trackName].volume.value = val;
          document.getElementById(`val-${{trackName}}`).innerText = val + " dB";
        }};

        document.getElementById(`mute-${{trackName}}`).onclick = (e) => {{
          channels[trackName].mute = !channels[trackName].mute;
          e.target.classList.toggle('active-mute', channels[trackName].mute);
        }};

        document.getElementById(`solo-${{trackName}}`).onclick = (e) => {{
          channels[trackName].solo = !channels[trackName].solo;
          e.target.classList.toggle('active-solo', channels[trackName].solo);
        }};
      }});

      Tone.loaded().then(() => {{
        document.getElementById('playBtn').disabled = false;
        document.getElementById('playBtn').innerText = 'Play All';
      }});

      document.getElementById('playBtn').onclick = async () => {{
        await Tone.start();
        if (Tone.Transport.state === 'started') {{ Tone.Transport.pause(); }} 
        else {{ Tone.Transport.start(); }}
      }};
      document.getElementById('stopBtn').onclick = () => {{ Tone.Transport.stop(); }};
    </script>
    </body>
    </html>
    """
    components.html(tone_js_code, height=300 + (len(stems_data) * 50))
else:
    st.info("Silakan upload minimal satu file audio.")
