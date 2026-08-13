import base64
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🎛️ Multi-Stem Player dengan Waveform & Playhead (Tone.js)")

# 1. Upload Audio (Dynamic Sequential Upload)
st.subheader("1. Upload Stem Audio")

stems_data = {}
i = 0

# Loop dinamis: Menampilkan slot upload baru persis di bawah slot yang sudah terisi
while True:
    uploaded_file = st.file_uploader(
        f"Upload Track {i+1}", 
        type=["mp3", "wav", "ogg", "flac"], 
        key=f"uploader_{i}"
    )
    
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        b64_str = base64.b64encode(bytes_data).decode()
        mime_type = uploaded_file.type if uploaded_file.type else "audio/mp3"
        
        # Menggunakan nama asli file yang diupload sebagai nama track
        track_name = f"Track {i+1}: {uploaded_file.name}"
        stems_data[track_name] = f"data:{mime_type};base64,{b64_str}"
        
        i += 1
    else:
        # Hentikan loop pada slot kosong pertama
        break

# 2. Mixer Controls Component dengan Waveform Canvas & Playhead
if stems_data:
    st.markdown("---")
    st.subheader("2. Multi-Track Waveform Mixer")
    
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
        .stem-card {{ 
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 16px;
          background: #21262d; 
          padding: 16px; 
          border-radius: 8px;
          border: 1px solid #30363d;
        }}
        .track-header {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: bold;
        }}
        .waveform-wrapper {{
          position: relative;
          width: 100%;
          height: 60px;
          background: #161b22;
          border-radius: 6px;
          overflow: hidden;
          cursor: pointer;
          border: 1px solid #30363d;
        }}
        canvas {{
          width: 100%;
          height: 100%;
          display: block;
        }}
        .playhead {{
          position: absolute;
          top: 0;
          left: 0%;
          width: 2px;
          height: 100%;
          background-color: #f85149;
          box-shadow: 0 0 4px rgba(248, 81, 73, 0.8);
          pointer-events: none;
          z-index: 10;
        }}
        .slider-wrapper {{ 
          display: flex; 
          align-items: center; 
          gap: 12px; 
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
        .btn-toggle:hover {{ filter: brightness(1.2); }}
        .btn-toggle.active-mute {{ background: #da3633; border-color: #f85149; color: white; }}
        .btn-toggle.active-solo {{ background: #d29922; border-color: #f1e05a; color: #0d1117; }}
        .time-display {{
          font-family: monospace;
          font-size: 14px;
          color: #58a6ff;
          margin-left: 10px;
        }}
      </style>
    </head>
    <body>
    <div class="player-card">
      <div class="transport-bar">
        <button id="playBtn" class="btn-main" disabled>Menganalisis Waveform...</button>
        <button id="stopBtn" class="btn-main btn-stop">Stop</button>
        <span id="timeDisplay" class="time-display">00:00 / 00:00</span>
      </div>
      <div id="stemsContainer"></div>
    </div>

    <script>
      const stemSources = {stems_json};
      const channels = {{}};
      const players = {{}};
      const container = document.getElementById('stemsContainer');
      let maxDuration = 0;

      Object.keys(stemSources).forEach(trackName => {{
        const channel = new Tone.Channel({{ volume: 0, mute: false, solo: false }}).toDestination();
        const player = new Tone.Player(stemSources[trackName]).connect(channel);
        
        player.sync().start(0);
        channels[trackName] = channel;
        players[trackName] = player;

        const card = document.createElement('div');
        card.className = 'stem-card';
        card.innerHTML = `
          <div class="track-header">
            <span>${{trackName}}</span>
          </div>
          <div class="waveform-wrapper" id="wrap-${{trackName}}">
            <canvas id="wave-${{trackName}}"></canvas>
            <div class="playhead" id="playhead-${{trackName}}"></div>
          </div>
          <div class="slider-wrapper">
            <input type="range" id="vol-${{trackName}}" min="-40" max="6" value="0" step="1">
            <span class="vol-label" id="val-${{trackName}}">0 dB</span>
          </div>
          <div class="controls-bottom">
            <button id="mute-${{trackName}}" class="btn-toggle">MUTE</button>
            <button id="solo-${{trackName}}" class="btn-toggle">SOLO</button>
          </div>
        `;
        container.appendChild(card);

        const wrapper = document.getElementById(`wrap-${{trackName}}`);
        wrapper.onclick = (e) => {{
          if (maxDuration > 0) {{
            const rect = wrapper.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const pct = clickX / rect.width;
            Tone.Transport.seconds = pct * maxDuration;
            updatePlayheadPosition(pct * 100);
          }}
        }};

        document.getElementById(`vol-${{trackName}}`).oninput = (e) => {{
          const val = parseFloat(e.target.value);
          channels[trackName].volume.value = val;
          document.getElementById(`val-${{trackName}}`).innerText = (val > 0 ? "+" : "") + val + " dB";
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

      function drawWaveform(player, canvas) {{
        const ctx = canvas.getContext('2d');
        const buffer = player.buffer.get();
        if (!buffer) return;

        const rawData = buffer.getChannelData(0);
        const samples = canvas.width;
        const blockSize = Math.floor(rawData.length / samples);
        const amp = canvas.height / 2;

        ctx.fillStyle = '#238636';
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < samples; i++) {{
          let min = 1.0;
          let max = -1.0;
          for (let j = 0; j < blockSize; j++) {{
            const datum = rawData[(i * blockSize) + j];
            if (datum < min) min = datum;
            if (datum > max) max = datum;
          }}
          ctx.fillRect(i, (1 + min) * amp, 1, Math.max(1, (max - min) * amp));
        }}
      }}

      function formatTime(seconds) {{
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
      }}

      function updatePlayheadPosition(pct) {{
        Object.keys(stemSources).forEach(trackName => {{
          const ph = document.getElementById(`playhead-${{trackName}}`);
          if (ph) ph.style.left = `${{Math.min(pct, 100)}}%`;
        }});
      }}

      Tone.loaded().then(() => {{
        let maxDur = 0;
        Object.keys(players).forEach(name => {{
          const dur = players[name].buffer.duration;
          if (dur > maxDur) maxDur = dur;

          const canvas = document.getElementById(`wave-${{name}}`);
          if (canvas) {{
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = 60;
            drawWaveform(players[name], canvas);
          }}
        }});

        maxDuration = maxDur;
        const playBtn = document.getElementById('playBtn');
        playBtn.disabled = false;
        playBtn.innerText = 'Play All';
        document.getElementById('timeDisplay').innerText = `00:00 / ${{formatTime(maxDuration)}}`;
      }});

      function renderLoop() {{
        if (Tone.Transport.state === 'started' && maxDuration > 0) {{
          const curTime = Tone.Transport.seconds;
          const pct = (curTime / maxDuration) * 100;
          updatePlayheadPosition(pct);
          document.getElementById('timeDisplay').innerText = `${{formatTime(curTime)}} / ${{formatTime(maxDuration)}}`;
        }}
        requestAnimationFrame(renderLoop);
      }}
      requestAnimationFrame(renderLoop);

      const playBtn = document.getElementById('playBtn');
      playBtn.onclick = async () => {{
        await Tone.start();
        if (Tone.Transport.state === 'started') {{ 
          Tone.Transport.pause(); 
          playBtn.innerText = 'Play All';
        }} else {{ 
          Tone.Transport.start(); 
          playBtn.innerText = 'Pause';
        }}
      }};

      document.getElementById('stopBtn').onclick = () => {{ 
        Tone.Transport.stop(); 
        playBtn.innerText = 'Play All';
        updatePlayheadPosition(0);
        if (maxDuration > 0) {{
          document.getElementById('timeDisplay').innerText = `00:00 / ${{formatTime(maxDuration)}}`;
        }}
      }};
    </script>
    </body>
    </html>
    """
    
    components.html(tone_js_code, height=140 + (len(stems_data) * 250))
else:
    st.info("👈 Silakan upload file audio pada slot Track 1 di atas.")
