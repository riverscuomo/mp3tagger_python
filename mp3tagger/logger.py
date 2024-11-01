import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mp3_tagger.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)
