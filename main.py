import streamlit as st
from PIL import Image
from openai import OpenAI
import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser



def parse_playlist(text):
    parsed = []
    lines = text.strip().splitlines()
    for line in lines:
        if "–" in line:  # en dash
            parts = line.split("–", 1)
        elif "-" in line:  # fallback
            parts = line.split("-", 1)
        else:
            continue
        artist = parts[0].strip()
        track = parts[1].strip()
        parsed.append({"artist": artist, "track": track})
    return parsed


# --- PAGE CONFIG ---
st.set_page_config(page_title="Plailista – AI Playlist Generator", page_icon="🎵", layout="centered")

# --- HEADER ---
st.title("🧠🎵 Plailista")
st.subheader("Playlists from the Aether, Delivered to Spotify")

# --- PLACEHOLDER FOR IMAGES ---
# st.image("logo.png", width=120)
# st.image("einstein_dancing.gif", width=300)

# --- INFO SECTION ---
with st.expander("ℹ️ What’s This?", expanded=True):
    st.markdown("""
**Plailista** is a simple tool that lets you generate Spotify playlists using the power of AI.  
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
    prompt = f"""
    Generate a {num_songs}-track playlist in the genre of {genre}, with a {mood} vibe, inspired by the style of {artist}.
    Format it as one line per song in this format: Artist – Track Title
    Only include real songs and artists.

    Here are a few examples:
    Lucinda Williams – Drunken Angel  
    Waylon Jennings – Honky Tonk Heroes  
    Townes Van Zandt – Pancho and Lefty  
    Cowboy Junkies – Misguided Angel  
    Ray Wylie Hubbard – Snake Farm  
    """

    with st.spinner("🎧 Generating playlist..."):
        try:
            client = OpenAI(api_key=st.secrets["openai"]["api_key"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            output = response.choices[0].message.content
            parsed = parse_playlist(output)

            st.session_state["generated_playlist"] = output
            st.session_state["parsed_playlist"] = parsed

            st.success("✅ Playlist generated!")
        except Exception as e:
            st.error(f"OpenAI error: {str(e)}")



# --- OR MANUAL INPUT ---
st.markdown("---")
st.subheader("📋 Paste Your Own Playlist (or edit the example)")

default_example = """Lucinda Williams – Drunken Angel
Waylon Jennings – Honky Tonk Heroes
Townes Van Zandt – Pancho and Lefty
Cowboy Junkies – Misguided Angel
Ray Wylie Hubbard – Snake Farm"""

playlist_input = st.text_area(
    "Format: Artist – Track",
    value=st.session_state.get("generated_playlist", default_example),
    height=200
)


# ---if "parsed_playlist" in st.session_state:
   # st.subheader("🔍 Parsed Playlist (Structured)")
   # st.json(st.session_state["parsed_playlist"]) 


# --- AUTH & PLAYLIST CREATION ---
st.markdown("---")
st.subheader("🔐 Connect & Create")

# --- PLAYLIST NAME INPUT (ALWAYS VISIBLE) ---
playlist_name = st.text_input("Playlist Name", "Outlaw Starter Pack") # This is now always visible

# --- SPOTIFY AUTHENTICATION HANDLING ---
if "sp_oauth" not in st.session_state:
    st.session_state["sp_oauth"] = SpotifyOAuth(
        client_id=st.secrets["spotify"]["client_id"],
        client_secret=st.secrets["spotify"]["client_secret"],
        redirect_uri=st.secrets["spotify"]["redirect_uri"],
        scope="playlist-modify-public"
    )

code = st.query_params.get("code")

if code:
    try:
        token_info = st.session_state["sp_oauth"].get_access_token(code)
        st.session_state["token_info"] = token_info
        st.session_state["sp"] = spotipy.Spotify(auth=token_info['access_token'])
        st.query_params.clear() # Clear the code from the URL
        st.rerun() # Rerun to remove the code from the URL and update the UI
    except Exception as e:
        st.error(f"Error getting Spotify token: {e}")
        st.session_state["token_info"] = None
        st.session_state["sp"] = None
elif "token_info" in st.session_state:
    is_token_valid = st.session_state["sp_oauth"].validate_token(st.session_state["token_info"])
    if is_token_valid:
        st.session_state["sp"] = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])
        st.success(f"🔐 Authenticated as {st.session_state['sp'].current_user()['display_name']}") # Show success immediately
    else:
        # Display the AUTHENTICATE BUTTON when token is invalid/expired
        auth_url = st.session_state["sp_oauth"].get_authorize_url()
        if st.button("🔐 Authenticate with Spotify"): # <<< The button element
            st.webbrowser.open(auth_url) # Open the URL in a new browser tab/window
            st.info("Please complete authentication in the new tab.") # Optional info message
else:
    # Display the AUTHENTICATE BUTTON when no token info is present
    auth_url = st.session_state["sp_oauth"].get_authorize_url()
    if st.button("🔐 Authenticate with Spotify"): # <<< The button element
        st.webbrowser.open(auth_url) # Open the URL in a new browser tab/window
        st.info("Please complete authentication in the new tab.") # Optional info message


# --- CREATE PLAYLIST ON SPOTIFY BUTTON (ALWAYS VISIBLE, BUT WILL ERROR IF NOT AUTHENTICATED) ---
# This entire block is now outside the "if sp in st.session_state" check.
# Clicking this when not authenticated will indeed raise an error as requested.
if st.button("➕ Create Playlist on Spotify"):
    if "parsed_playlist" not in st.session_state or not st.session_state["parsed_playlist"]:
        st.warning("Please generate a playlist or paste one above before creating it on Spotify.")
    else:
        with st.spinner("Creating playlist on Spotify..."):
            try:
                # --- THIS IS WHERE THE ERROR WILL OCCUR IF NOT AUTHENTICATED ---
                # st.session_state["sp"] will be None or not exist, causing an error
                user = st.session_state["sp"].current_user() # This line will fail if not authenticated
                user_id = user['id']
                playlist = st.session_state["sp"].user_playlist_create(user_id, playlist_name, public=True)
                st.success(f"🎉 Playlist '{playlist_name}' created successfully!")

                track_uris = []
                for item in st.session_state["parsed_playlist"]:
                    search_query = f"track:{item['track']} artist:{item['artist']}"
                    results = st.session_state["sp"].search(q=search_query, type="track", limit=1)
                    if results and results['tracks']['items']:
                        track_uris.append(results['tracks']['items'][0]['uri'])
                    else:
                        st.warning(f"Could not find track: {item['artist']} - {item['track']}")

                if track_uris:
                    chunk_size = 100
                    for i in range(0, len(track_uris), chunk_size):
                        chunk = track_uris[i:i + chunk_size]
                        st.session_state["sp"].playlist_add_items(playlist['id'], chunk)
                    st.success(f"Added {len(track_uris)} songs to '{playlist_name}'!")
                else:
                    st.warning("No songs were found to add to the playlist.")

            except Exception as e:
                # This catches the error if you click the button when not authenticated
                st.error(f"Error creating playlist: {e}. Please ensure you are authenticated with Spotify.")
                # You might want to also re-display the auth button here if an error occurs
                if "sp" not in st.session_state or st.session_state["sp"] is None:
                    auth_url = st.session_state["sp_oauth"].get_authorize_url()
                    if st.button("🔐 Authenticate with Spotify (after error)"):
                         st.webbrowser.open(auth_url)
                         st.info("Please complete authentication in the new tab.")


# --- Authentication status message (re-added for clarity, replaces the final else block) ---
# This message will dynamically appear/disappear based on auth status
if "sp" in st.session_state and st.session_state["sp"] is not None:
    try:
        # Check if user object is still valid
        user_display_name = st.session_state["sp"].current_user()['display_name']
        st.success(f"🔐 Authenticated as {user_display_name}")
    except Exception as e:
        # If user data cannot be retrieved, token might be expired/invalid
        st.error(f"Authentication session expired or invalid. Please re-authenticate: {e}")
        st.session_state["token_info"] = None
        st.session_state["sp"] = None
        st.rerun()
else:
    st.info("Please authenticate with Spotify to fully utilize features.")