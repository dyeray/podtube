class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


ytdl_opts = {"format": "best[protocol=https]/best[protocol=http]", "logger": MyLogger()}
