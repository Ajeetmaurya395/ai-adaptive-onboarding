import json
import os
from pathlib import Path
from typing import Any

from huggingface_hub import hf_hub_download, snapshot_download


class DataLoader:
    """Resolve data assets from local storage or Hugging Face Hub."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.local_data_dir = self.project_root / "data"
        self.cache_dir = Path(
            os.getenv("CACHE_DIR")
            or os.getenv("DATA_CACHE_DIR")
            or "/tmp/ai_onboarding/data"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_source = os.getenv("DATA_SOURCE", "local").strip().lower()
        self.repo_id = os.getenv("HF_DATASET_REPO", "").strip()
        self.repo_type = os.getenv("HF_DATASET_REPO_TYPE", "dataset").strip() or "dataset"
        self.token = os.getenv("HF_TOKEN")

    def _local_path(self, relative_path: str) -> Path:
        return self.local_data_dir / relative_path

    def _cache_path(self, relative_path: str) -> Path:
        return self.cache_dir / relative_path

    def _ensure_repo_configured(self) -> None:
        if not self.repo_id:
            raise FileNotFoundError(
                "HF_DATASET_REPO is not configured for cloud asset loading."
            )

    def _download_file(self, relative_path: str) -> Path:
        self._ensure_repo_configured()
        downloaded_path = hf_hub_download(
            repo_id=self.repo_id,
            filename=relative_path,
            repo_type=self.repo_type,
            cache_dir=str(self.cache_dir),
            token=self.token,
        )
        return Path(downloaded_path)

    def _download_directory(self, relative_path: str) -> Path:
        self._ensure_repo_configured()
        snapshot_path = snapshot_download(
            repo_id=self.repo_id,
            repo_type=self.repo_type,
            cache_dir=str(self.cache_dir),
            allow_patterns=[f"{relative_path}/**", relative_path],
            token=self.token,
        )
        candidate = Path(snapshot_path) / relative_path
        if candidate.exists():
            return candidate
        raise FileNotFoundError(
            f"Directory '{relative_path}' was not found in Hugging Face repo '{self.repo_id}'."
        )

    def get_file_path(self, relative_path: str) -> Path:
        local_path = self._local_path(relative_path)
        if not self.data_source == "cloud" and local_path.exists():
            return local_path

        cache_path = self._cache_path(relative_path)
        if cache_path.exists():
            return cache_path

        if self.data_source == "cloud" or not local_path.exists():
            try:
                return self._download_file(relative_path)
            except Exception:
                if local_path.exists():
                    return local_path
                raise

        raise FileNotFoundError(
            f"Data file '{relative_path}' was not found in {self.local_data_dir}."
        )

    def get_directory_path(self, relative_path: str) -> Path:
        local_path = self._local_path(relative_path)
        if not self.data_source == "cloud" and local_path.exists():
            return local_path

        cache_path = self._cache_path(relative_path)
        if cache_path.exists():
            return cache_path

        if self.data_source == "cloud" or not local_path.exists():
            try:
                return self._download_directory(relative_path)
            except Exception:
                if local_path.exists():
                    return local_path
                raise

        raise FileNotFoundError(
            f"Data directory '{relative_path}' was not found locally or in cache."
        )

    def load_json(self, relative_path: str, default: Any) -> Any:
        try:
            path = self.get_file_path(relative_path)
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default


data_loader = DataLoader()
