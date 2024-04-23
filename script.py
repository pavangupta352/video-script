import os
import time
import obspython as obs

# asd
videos_directory = "/home/ratio/www/video"
source_name = "ass"

last_played_video = ""
last_check = 0


def play_video(video_path):
    global last_played_video
    source = obs.obs_get_source_by_name(source_name)
    if source:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "local_file", video_path)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
        last_played_video = video_path
        print(f"Now playing: {video_path}")


def get_latest_video(videos_directory):
    try:
        # Get a list of files ending with '.mp4'
        files = [f for f in os.listdir(videos_directory) if f.endswith(".mp4")]
        if not files:
            return None
        # Sort files by modification time in descending order
        files.sort(key=lambda x: os.path.getmtime(
            os.path.join(videos_directory, x)), reverse=True)
        return os.path.join(videos_directory, files[0])
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None


def script_tick(seconds):
    global last_check
    current_time = time.time()
    # Check for a new video every 10 seconds
    if current_time - last_check > 10:
        latest_video = get_latest_video(videos_directory)
        if latest_video and latest_video != last_played_video:
            play_video(latest_video)
        last_check = current_time


def script_description():
    return "Automatically plays new videos added to a specified folder in a Media Source."


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "videos_directory", "Videos Directory",
                                obs.OBS_PATH_DIRECTORY, None, videos_directory)
    obs.obs_properties_add_text(
        props, "source_name", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    return props


def script_update(settings):
    global videos_directory, source_name
    videos_directory = obs.obs_data_get_string(settings, "videos_directory")
    source_name = obs.obs_data_get_string(settings, "source_name")
