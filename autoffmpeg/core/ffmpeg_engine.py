def build_ffmpeg_command(input_path, output_path, settings):
    return [
        settings.ffmpeg_path,
        "-y",
        "-i", input_path,
        *settings.video_flags,
        "-c:a", "copy",
        output_path
    ]
