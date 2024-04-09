import os
import time
import random
import obspython as obs

videos_directory = "/home/ratio/www/video"  # Primary directory for new videos
newvideos_directory = "/home/ratio/www/newvideos"  # Directory with 96 videos to play randomly
source_name = "ass"

last_played_video = ""
last_check = 0
idle_since = None  # Keep track of idle time

def play_video(video_path):
    global last_played_video, idle_since
    source = obs.obs_get_source_by_name(source_name)
    if source:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "local_file", video_path)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        last_played_video = video_path
        idle_since = None  # Reset idle time since we're playing a new video
        print(f"Now playing: {video_path}")

def get_latest_video(directory):
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".mp4")]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        return os.path.join(directory, files[0])
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None

def get_random_video(directory, exclude_video=None):
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".mp4") and f != exclude_video]
        if not files:
            return None
        random_file = random.choice(files)
        return os.path.join(directory, random_file)
    except Exception as e:
        print(f"Error getting random video: {e}")
        return None

def script_tick(seconds):
    global last_check, idle_since
    current_time = time.time()

    # Check for a new video in the primary directory every 10 seconds
    if current_time - last_check > 10:
        latest_video = get_latest_video(videos_directory)
        if latest_video and latest_video != last_played_video:
            play_video(latest_video)  # New video found, play it
        else:
            if idle_since is None:
                idle_since = current_time
            elif current_time - idle_since > 10:  # Play a random video after being idle for 10 seconds
                random_video = get_random_video(newvideos_directory, exclude_video=os.path.basename(last_played_video))
                if random_video:
                    play_video(random_video)
        last_check = current_time

def script_description():
    return "Automatically plays new videos from the primary directory or random videos from a secondary directory when idle."

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "videos_directory", "Primary Videos Directory", obs.OBS_PATH_DIRECTORY, None, videos_directory)
    obs.obs_properties_add_path(props, "newvideos_directory", "Secondary Videos Directory", obs.OBS_PATH_DIRECTORY, None, newvideos_directory)
    obs.obs_properties_add_text(props, "source_name", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    return props

def script_update(settings):
    global videos_directory, newvideos_directory, source_name
    videos_directory = obs.obs_data_get_string(settings, "videos_directory")
    newvideos_directory = obs.obs_data_get_string(settings, "newvideos_directory")
    source_name = obs.obs_data_get_string(settings, "source_name")
