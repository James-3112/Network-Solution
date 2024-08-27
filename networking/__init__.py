import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] | %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

__version__ = "0.1.0"
__author__ = 'James Turner'

print(f"""\033[93mWARNING Networking is in Alpha {__version__}, 
Do not use in a production environment until full release \033[0m""")