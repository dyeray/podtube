class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


ytdl_opts = {
    'format': 'worst',
    'logger': MyLogger()
}
