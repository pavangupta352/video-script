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
last_check = 0
idle_video_list = []  # List to manage idle videos playback
is_playing = False  # Flag to check if a video is currently playing

def play_video(video_path, idle=False):
    global last_played_video, is_playing
    source = obs.obs_get_source_by_name(source_name)
    if source:
        is_playing = True  # Set the flag to indicate that a video is now playing
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "local_file", video_path)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        if not idle:  # Only update last played video if it's not an idle video
            last_played_video = video_path
        print(f"[newscript.py] Now playing: {video_path}")

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

def play_random_idle_video():
    global idle_video_list, is_playing
    try:
        if not idle_video_list:
            idle_video_list = [f for f in os.listdir(idle_videos_directory) if f.endswith(".mp4")]
            random.shuffle(idle_video_list)  # Shuffle to ensure random playback
        
        if idle_video_list:
            video_path = os.path.join(idle_videos_directory, idle_video_list.pop())
            play_video(video_path, idle=True)
            return True
    except Exception as e:
        print(f"Error playing random idle video: {e}")
    return False

def on_media_ended(calldata):
    global is_playing
    is_playing = False  # Reset the flag when media ends

def script_tick(seconds):
    global last_check, last_played_video, is_playing
    current_time = time.time()

    if not is_playing:
        # Check for a new video every 10 seconds
        if current_time - last_check > 10:
            latest_video = get_latest_video(videos_directory)
            if latest_video and latest_video != last_played_video:
                play_video(latest_video)
            elif not latest_video or latest_video == last_played_video:  # No new video found or waiting for new ones
                if not play_random_idle_video():
                    last_played_video = ""  # Reset if no idle video is available to play
            last_check = current_time

def script_description():
    return "Automatically plays new videos added to a specified folder or random videos from another folder when idle."

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def script_unload():
    obs.obs_frontend_remove_event_callback(on_event)

def on_event(event):
    if event == obs.OBS_FRONTEND_EVENT_MEDIA_PLAYING:
        source = obs.obs_frontend_get_current_scene_as_source()
        if source:
            scene = obs.obs_scene_from_source(source)
            scene_item = obs.obs_scene_find_source(scene, source_name)
            if scene_item:
                video_source = obs.obs_sceneitem_get_source(scene_item)
                signal_handler = obs.obs_source_get_signal_handler(video_source)
                obs.signal_handler_connect(signal_handler, "media_ended", on_media_ended)

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
