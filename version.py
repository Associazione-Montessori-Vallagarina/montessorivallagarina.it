import subprocess
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig


def on_config(config: MkDocsConfig) -> MkDocsConfig:
    repository = Path(config.config_file_path).parent
    commit_id = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    config.copyright = f"<small>{commit_id}</small>"
    return config
