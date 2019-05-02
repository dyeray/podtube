class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


ytdl_opts = {
    'format': '(mp4)[height < 720]',
    'logger': MyLogger()
}
