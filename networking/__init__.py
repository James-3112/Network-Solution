import logging

class LoggingFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'class_name'): record.class_name = record.class_name
        else: record.class_name = 'Unknown'
        return super().format(record)

class Logger(logging.getLoggerClass()):
    def __init__(self, name):
        super().__init__(name)
        self.class_name = 'Unknown'
    
    def set_class_name(self, class_name):
        self.class_name = class_name

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)
        record.class_name = self.class_name
        return record

# Define the formatter with class name support
formatter = LoggingFormatter('%(asctime)s | %(class_name)s | [%(levelname)s] | %(message)s')

# Set up the handlers with the custom formatter
file_handler = logging.FileHandler("debug.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Apply the logging configuration
logging.setLoggerClass(Logger)
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

__version__ = "0.1.0"
__author__ = 'James Turner'

print(f"""\033[93mWARNING Networking is in Alpha {__version__}, 
Do not use in a production environment until full release \033[0m""")