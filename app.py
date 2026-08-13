import base64
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🎛️ Streamlit Multi-Stem Player (Tone.js)")

st.subheader("1. Upload Stem Audio")

# Membuat 4 Kolom Upload untuk 4 Track
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
        # Mengambil nama file atau fallback ke label track
        track_name = default_names[i]
        
        # Konversi file audio ke Base64 Data URI
        bytes_data = uploaded_file.read()
        b64_str = base64.b64encode(bytes_data).decode()
        mime_type = uploaded_file.type if uploaded_file.type else "audio/mp3"
        
        stems_data[track_name] = f"data:{mime_type};base64,{b64_str}"

st.markdown("---")
st.subheader("2. Stem Mixer & Playback")

if not stems_data:
    st.info("👈 Silakan upload minimal 1 file audio di slot atas untuk mengaktifkan player.")
else:
    # Serialize data Python ke JSON String aman untuk JavaScript
    stems_json = json.dumps(stems_data)
    
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
          gap: 15px;
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
          grid-template-columns: 160px 1fr 60px 60px;
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
        <span id="status">Buffering tracks...</span>
      </div>

      <div id="stemsContainer"></div>
    </div>

    <script>
      const stemSources = {stems_json};
      const players = {{}};
      const channels = {{}};
      const totalTracks = Object.keys(stemSources).length;

      const container = document.getElementById('stemsContainer');

      // Inisialisasi Tone.Channel & Tone.Player per Track
      Object.keys(stemSources).forEach(trackName => {{
        const channel = new Tone.Channel({{ volume: 0, mute: false, solo: false }}).toDestination();
        
        const player = new Tone.Player({{
          url: stemSources[trackName],
          onload: checkAllLoaded
        }}).connect(channel);

        player.sync().start(0);

        players[trackName] = player;
        channels[trackName] = channel;

        // UI Slider & Controls
        const row = document.createElement('div');
        row.className = 'stem-row';
        row.innerHTML = `
          <strong>${{trackName}}</strong>
          <input type="range" id="vol-${{trackName}}" min="-40" max="6" value="0" step="1">
          <button id="mute-${{trackName}}" class="btn-toggle">Mute</button>
          <button id="solo-${{trackName}}" class="btn-toggle">Solo</button>
        `;
        container.appendChild(row);

        // Event Listeners
        document.getElementById(`vol-${{trackName}}`).oninput = (e) => {{
          channels[trackName].volume.value = parseFloat(e.target.value);
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

      let loadedCount = 0;
      function checkAllLoaded() {{
        loadedCount++;
        if (loadedCount === totalTracks) {{
          document.getElementById('playBtn').disabled = false;
          document.getElementById('playBtn').innerText = 'Play All';
          document.getElementById('status').innerText = 'Ready (' + totalTracks + ' Tracks Loaded)';
        }}
      }}

      // Playback Controls
      const playBtn = document.getElementById('playBtn');
      playBtn.onclick = async () => {{
        await Tone.start();
        
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

    # Hitung tinggi iframe secara dinamis berdasarkan jumlah track yang diupload
    calculated_height = 130 + (len(stems_data) * 55)
    components.html(tone_js_code, height=calculated_height)
