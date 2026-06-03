from pathlib import Path
from urllib.request import urlretrieve


PREPROCESSED_URL = "https://data.recsys.synerise.com/dataset/challenge_dataset.tar.gz"
RAW_URL = "https://data.recsys.synerise.com/dataset/synerise_dataset.tar.gz"


def download_dataset(destination: Path, raw: bool = False) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    url = RAW_URL if raw else PREPROCESSED_URL
    archive_path = destination / Path(url).name
    if not archive_path.exists():
        urlretrieve(url, archive_path)
    return archive_path
