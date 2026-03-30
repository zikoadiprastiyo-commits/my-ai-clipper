import streamlit as st
import yt_dlp
import os
import subprocess
import whisper

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Clipper Pro", page_icon="🎬")
st.title("🎬 Smart AI Clipper")
st.write("Cari bagian video yang menarik secara otomatis menggunakan AI.")

# --- DAFTAR KATA KUNCI VIRAL (HOOK) ---
HOOK_KEYWORDS = ["gila", "rahasia", "tips", "jangan", "pernah", "ternyata", "kaget", "parah", "trik", "penting", "akhirnya", "bohong"]

# --- LOAD AI ---
@st.cache_resource
def load_model():
    return whisper.load_model("tiny")

model = load_model()

# --- FUNGSI DOWNLOAD & POTONG ---
def cut_video(url, start, end, output_filename):
    # Perintah FFmpeg untuk memotong video langsung dari URL tanpa download full
    # Ini jauh lebih cepat dan hemat storage laptop
    cmd = [
        'ffmpeg', '-y', 
        '-ss', str(start), 
        '-to', str(end), 
        '-i', url, 
        '-c:v', 'libx264', '-c:a', 'aac', # Re-encoding agar file stabil
        '-strict', 'experimental',
        output_filename
    ]
    subprocess.run(cmd)

# --- INPUT LINK ---
video_url = st.text_input("Tempel Link YouTube Anda di sini:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Mulai Analisis AI"):
    if video_url:
        with st.spinner("Sedang memproses... (Langkah 1: Download Audio)"):
            try:
                # 1. Download Audio saja untuk transkrip
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'audio_temp.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                
                # 2. AI Transkrip
                st.info("AI sedang membaca isi video...")
                result = model.transcribe("audio_temp.mp3")
                
                # 3. Tampilkan Hasil
                st.subheader("🔥 Hasil Viral Hook Scanner:")
                
                for segment in result['segments']:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    text_lower = text.lower()
                    
                    is_hook = any(word in text_lower for word in HOOK_KEYWORDS)
                    
                    # Logika Tampilan (Viral vs Biasa)
                    if is_hook:
                        container = st.error # Box Merah untuk Viral
                        label_prefix = "🚨 POTENSI VIRAL"
                    else:
                        container = st.expander # Dropdown untuk Biasa
                        label_prefix = "📝 Kalimat"

                    # Eksekusi Tampilan
                    with container(f"{label_prefix}: [{start:.2f}s - {end:.2f}s]"):
                        st.write(f"**{text}**")
                        
                        # TOMBOL DOWNLOAD KLIP OTOMATIS
                        if st.button(f"Gunting Klip ({start:.0f}s)", key=f"btn_{start}"):
                            with st.spinner("Sedang menggunting video..."):
                                output_name = f"clip_{int(start)}.mp4"
                                # Ambil link video asli dari YouTube via yt-dlp untuk dipotong ffmpeg
                                with yt_dlp.YoutubeDL({'format': 'best'}) as ydl:
                                    info = ydl.extract_info(video_url, download=False)
                                    real_video_url = info['url']
                                
                                cut_video(real_video_url, start, end, output_name)
                                
                                if os.path.exists(output_name):
                                    with open(output_name, "rb") as f:
                                        st.download_button("📥 Klik di sini untuk Simpan MP4", f, file_name=output_name)
                                    st.success("Klip siap didownload!")

            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                if os.path.exists("audio_temp.mp3"):
                    os.remove("audio_temp.mp3")
    else:
        st.warning("Silakan masukkan link YouTube dulu ya!")

st.info("Setelah klik 'Gunting Klip', tunggu sebentar sampai tombol download muncul.")