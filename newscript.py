import os
import time
import random
import obspython as obs

# Primary directory where new videos are added
videos_directory = "/home/ratio/www/video"
# Secondary directory for random videos during idle times
idle_videos_directory = "/home/ratio/www/newvideos"
source_name = "ass"

last_played_video = ""
last_played_time = 0
video_duration = 0
idle_video_list = []  # List to manage idle videos playback

def get_video_duration(video_path):
    try:
        # Use ffprobe to get the video duration
        # Ensure ffprobe is installed and in your PATH
        result = os.popen(f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{video_path}\"").read()
        return float(result.strip())
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return 0

def play_video(video_path, idle=False):
    global last_played_video, last_played_time, video_duration
    source = obs.obs_get_source_by_name(source_name)
    if source:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "local_file", video_path)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        video_duration = get_video_duration(video_path)
        last_played_time = time.time()
        if not idle:  # Only update last played video if it's not an idle video
            last_played_video = video_path
        print(f"[newscript.py] Now playing: {video_path}")

def get_latest_video(directory, last_video):
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".mp4")]
        files = [os.path.join(directory, f) for f in files]
        files = [f for f in files if os.path.isfile(f) and f != last_video]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return files[0]
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None

def play_random_idle_video():
    global idle_video_list
    try:
        if not idle_video_list:
            idle_video_list = [os.path.join(idle_videos_directory, f) for f in os.listdir(idle_videos_directory) if f.endswith(".mp4")]
            random.shuffle(idle_video_list)  # Shuffle to ensure random playback
        
        if idle_video_list:
            video_path = idle_video_list.pop()
            play_video(video_path, idle=True)
            return True
    except Exception as e:
        print(f"Error playing random idle video: {e}")
    return False

def script_tick(seconds):
    global last_played_time, video_duration, last_played_video
    current_time = time.time()
    
    # Check if the current video has finished playing
    if current_time - last_played_time >= video_duration:
        latest_video = get_latest_video(videos_directory, last_played_video)
        if latest_video:
            play_video(latest_video)
        else:
            play_random_idle_video()

def script_description():
    return "Automatically plays new videos added to a specified folder or random videos from another folder when idle."

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "videos_directory", "Videos Directory", obs.OBS_PATH_DIRECTORY, None, videos_directory)
    obs.obs_properties_add_path(props, "idle_videos_directory", "Idle Videos Directory", obs.OBS_PATH_DIRECTORY, None, idle_videos_directory)
    obs.obs_properties_add_text(props, "source_name", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    return props

def script_update(settings):
    global videos_directory, idle_videos_directory, source_name
    videos_directory = obs.obs_data_get_string(settings, "videos_directory")
    idle_videos_directory = obs.obs_data_get_string(settings, "idle_videos_directory")
    source_name = obs.obs_data_get_string(settings, "source_name")
