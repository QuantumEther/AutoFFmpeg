class Settings:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"
        self.video_flags = [
            "-c:v", "hevc_nvenc",
            "-preset","p7",
            "-profile:v","main",
            "-rc","vbr",
            "-cq","23",
            "-spatial-aq","1",
            "-aq-strength","15",
            "-temporal-aq","1",
            "-g","10",
            "-keyint_min","10",
            "-rc-lookahead","20",
        ]
