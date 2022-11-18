import logging

class TwitchRecorderLogHandler(logging.Handler):
    def __init__(self, target_widget):
        super(TwitchRecorderLogHandler, self).__init__()
        self.target_widget = target_widget
    
    def emit(self, record):
        self.target_widget.append(record.getMessage())