import streamlit as st
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="GPTune – AI Playlist Generator", page_icon="🎵", layout="centered")

# --- HEADER ---
st.title("🧠🎵 GPTune")
st.subheader("Playlists from the Mind, Delivered to Spotify")

# --- PLACEHOLDER FOR IMAGES ---
# st.image("logo.png", width=120)
# st.image("einstein_dancing.gif", width=300)

# --- INFO SECTION ---
with st.expander("ℹ️ What’s This?", expanded=True):
    st.markdown("""
    **GPTune** is a simple tool that lets you generate Spotify playlists using the power of AI.  
    Describe your mood, vibe, or favorite artist, and it’ll spin up a playlist and send it directly to your Spotify account.

    **How to Use**  
    1. Select your vibe or paste a list  
    2. Log in to your Spotify account  
    3. Hit “Create Playlist” — and done

    ---
    **Note from the Creator**  
    This is a weekend project built by Terence Reis. Hope you’ll enjoy it.  
    _If you don’t… well, did you catch the part about it being a weekend project?_ 😅
    """)

# --- PROMPT BUILDER ---
st.header("🎶 Generate a Playlist")
col1, col2 = st.columns(2)

with col1:
    mood = st.selectbox("Mood", ["Gritty", "Melancholic", "Upbeat", "Chill"])
    genre = st.selectbox("Genre", ["Outlaw Country", "Indie Rock", "Jazz", "Ambient"])

with col2:
    artist = st.text_input("Anchor Artist", "Lucinda Williams")
    num_songs = st.slider("Number of Songs", 10, 30, 20)

if st.button("Generate Playlist 🎶"):
    fake_playlist = """Lucinda Williams – Drunken Angel
Waylon Jennings – Honky Tonk Heroes
Townes Van Zandt – Pancho and Lefty
Steve Earle – Copperhead Road
Ray Wylie Hubbard – Snake Farm
"""
    st.session_state["generated_playlist"] = fake_playlist
    st.success("✅ Playlist generated!")

# --- OR MANUAL INPUT ---
st.markdown("---")
st.subheader("📋 Paste Your Own Playlist")
playlist_input = st.text_area(
    "Format: Artist – Track",
    value=st.session_state.get("generated_playlist", ""),
    height=200
)

# --- AUTH & PLAYLIST CREATION ---
st.markdown("---")
st.subheader("🔐 Connect & Create")
playlist_name = st.text_input("Playlist Name", "Outlaw Starter Pack")

if st.button("Authenticate with Spotify"):
    st.success("🔐 Authenticated as user123 (fake-token-xyz)")

if st.button("➕ Create Playlist on Spotify"):
    with st.spinner("Creating playlist on Spotify..."):
        import time
        time.sleep(2)
    st.success("🎉 Playlist 'Outlaw Starter Pack' created successfully!")
