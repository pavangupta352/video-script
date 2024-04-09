import os
import time
import obspython as obs
import random

# Primary directory where new videos will be added
videos_directory = "/home/ratio/www/video"
# Secondary directory with a selection of videos to play randomly
secondary_videos_directory = "/home/ratio/www/bible_quotes_video"
source_name = "ass"  # OBS Source name

last_played_video = ""
last_check = 0
# Store previously played videos to avoid immediate repeats
previously_played_videos = []


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
        files = [f for f in os.listdir(videos_directory) if f.endswith(".mp4")]
        if not files:
            return None
        files.sort(key=lambda x: os.path.getmtime(
            os.path.join(videos_directory, x)), reverse=True)
        return os.path.join(videos_directory, files[0])
    except Exception as e:
        print(f"Error getting latest video: {e}")
        return None


def play_random_video(secondary_videos_directory):
    global previously_played_videos
    try:
        files = [f for f in os.listdir(secondary_videos_directory) if f.endswith(
            ".mp4") and os.path.join(secondary_videos_directory, f) not in previously_played_videos]
        if not files:  # If all videos have been played, reset the history
            previously_played_videos = []
            files = [f for f in os.listdir(
                secondary_videos_directory) if f.endswith(".mp4")]
        if files:
            chosen_file = random.choice(files)
            previously_played_videos.append(os.path.join(
                secondary_videos_directory, chosen_file))
            return os.path.join(secondary_videos_directory, chosen_file)
    except Exception as e:
        print(f"Error selecting random video: {e}")
    return None


def script_tick(seconds):
    global last_check, last_played_video
    current_time = time.time()
    # Check for a new video every 10 seconds
    if current_time - last_check > 10:
        latest_video = get_latest_video(videos_directory)
        if latest_video and latest_video != last_played_video:
            play_video(latest_video)
        else:
            # No new video in the primary directory, play random from the secondary
            random_video = play_random_video(secondary_videos_directory)
            if random_video and random_video != last_played_video:
                play_video(random_video)
        last_check = current_time


def script_description():
    return "Automatically plays new videos from a specified folder, or random videos from another folder when idle."


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "videos_directory", "Primary Videos Directory",
                                obs.OBS_PATH_DIRECTORY, None, videos_directory)
    obs.obs_properties_add_path(props, "secondary_videos_directory", "Secondary Videos Directory for Random Playback",
                                obs.OBS_PATH_DIRECTORY, None, secondary_videos_directory)
    obs.obs_properties_add_text(
        props, "source_name", "Media Source Name", obs.OBS_TEXT_DEFAULT)
    return props


def script_update(settings):
    global videos_directory, secondary_videos_directory, source_name
    videos_directory = obs.obs_data_get_string(settings, "videos_directory")
    secondary_videos_directory = obs.obs_data_get_string(
        settings, "secondary_videos_directory")
    source_name = obs.obs_data_get_string(settings, "source_name")
