import os
import subprocess
from pathlib import Path


PROJECT_PATH = Path(os.getenv("PROJECT_PATH", Path(__file__).resolve().parent))
DATASET_ID = os.getenv("KAGGLE_DATASET_ID", "ayaali2002/gbDataset")
NOTEBOOK_ID = os.getenv("KAGGLE_NOTEBOOK_ID", "ayaali2002/final-nb")
KAGGLE_TIMEOUT = int(os.getenv("KAGGLE_TIMEOUT", "300"))


def run_command(*args: str) -> str:
    result = subprocess.run(
        ["kaggle", *args],
        cwd=PROJECT_PATH,
        check=True,
        capture_output=True,
        text=True,
        timeout=KAGGLE_TIMEOUT,
    )
    return result.stdout


def run_workflow() -> dict[str, str]:
    dataset_path = PROJECT_PATH / "dataset"
    notebook_path = PROJECT_PATH / "notebook"
    output_path = PROJECT_PATH / "nb_output"
    output_path.mkdir(parents=True, exist_ok=True)

    return {
        "dataset": run_command("datasets", "metadata", "-p", str(dataset_path), DATASET_ID),
        "notebook_push": run_command("kernels", "push", "-p", str(notebook_path)),
        "status": run_command("kernels", "status", NOTEBOOK_ID),
        "output": run_command("kernels", "output", NOTEBOOK_ID, "-p", str(output_path)),
    }
