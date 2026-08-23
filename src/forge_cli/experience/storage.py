"""Git-native FER report persistence with local atomic writes."""

from __future__ import annotations

import os
from pathlib import Path
import re
import tempfile
import threading
import time
from contextlib import contextmanager
from typing import Any

import yaml

from forge_cli.experience.model import ExperienceInputError, ObservationInput, PositiveEvidenceInput, ensure_safe_text


_REPORT_RE = re.compile(r"^FER-(?P<number>[0-9]{4,})\.yml$")


class ExperienceStorageError(RuntimeError):
    """Raised when FER evidence cannot be durably written."""


class ExperienceStorage:
    def __init__(self, project_root: Path, *, context: dict[str, Any], report_id: str | None = None) -> None:
        self.project_root = project_root
        self.context = dict(context)
        if report_id is not None and re.fullmatch(r"FER-[0-9]{4,}", report_id) is None:
            raise ExperienceStorageError(f"Invalid FER report ID: {report_id}")
        self._report_path: Path | None = (
            self.reports_root / f"{report_id}.yml" if report_id is not None else None
        )
        self._mutex = threading.RLock()

    @property
    def reports_root(self) -> Path:
        return self.project_root / "dogfooding" / "reports"

    def record(self, entry: ObservationInput | PositiveEvidenceInput) -> Path:
        with self._mutex:
            dogfooding_root = self.project_root / "dogfooding"
            if dogfooding_root.is_symlink():
                raise ExperienceStorageError("FER report directory is not a safe directory.")
            self.reports_root.mkdir(parents=True, exist_ok=True)
            if self.reports_root.is_symlink() or not self.reports_root.is_dir():
                raise ExperienceStorageError("FER report directory is not a safe directory.")
            if self._report_path is None:
                self._report_path = self._reserve_report()
            elif self._report_path.is_symlink() or not self._report_path.is_file():
                raise ExperienceStorageError(f"FER report does not exist: {self._report_path}")
            with self._file_lock(self._report_path):
                if self._report_path.stat().st_size > 0:
                    try:
                        document = yaml.safe_load(self._report_path.read_text(encoding="utf-8"))
                    except (OSError, yaml.YAMLError) as error:
                        raise ExperienceStorageError(str(error)) from error
                    if not self._valid_document(document):
                        raise ExperienceStorageError(f"FER report is invalid: {self._report_path}")
                else:
                    document = {
                        "schema": "forge/experience-report@1",
                        "report": self._report_path.stem,
                        "source": dict(self.context),
                        "observations": [],
                        "positive_evidence": [],
                        "follow_up_candidates": [],
                    }
                report_id = self._report_path.stem
                if isinstance(entry, ObservationInput):
                    sequence = len(document["observations"]) + 1
                    document["observations"].append(
                        {
                            "id": f"{report_id}-O{sequence:03d}",
                            "area": entry.area,
                            "classification": entry.classification,
                            "expected": entry.expected,
                            "observed": entry.observed,
                            "evidence": list(entry.evidence),
                            "impact": entry.impact,
                            **({"workaround": entry.workaround} if entry.workaround else {}),
                            **({"follow_up": entry.follow_up} if entry.follow_up else {}),
                        }
                    )
                else:
                    sequence = len(document["positive_evidence"]) + 1
                    document["positive_evidence"].append(
                        {"id": f"{report_id}-P{sequence:03d}", "area": entry.area, "observed": entry.observed}
                    )
                try:
                    self._atomic_write(self._report_path, document)
                except OSError as error:
                    raise ExperienceStorageError(str(error)) from error
            return self._report_path

    @staticmethod
    def _valid_document(document: Any) -> bool:
        if not (
            isinstance(document, dict)
            and document.get("schema") == "forge/experience-report@1"
            and isinstance(document.get("report"), str)
            and isinstance(document.get("source"), dict)
            and isinstance(document.get("observations"), list)
            and isinstance(document.get("positive_evidence"), list)
            and isinstance(document.get("follow_up_candidates"), list)
        ):
            return False
        if not ExperienceStorage._safe_values(document):
            return False
        for observation in document["observations"]:
            if not isinstance(observation, dict) or not all(
                isinstance(observation.get(field), str) and observation[field].strip()
                for field in ("id", "area", "classification", "expected", "observed", "impact")
            ) or observation.get("classification") not in {"forge_problem", "project_problem", "uncertain"}:
                return False
            evidence = observation.get("evidence")
            if not isinstance(evidence, list) or not evidence or not all(isinstance(item, str) and item.strip() for item in evidence):
                return False
        for positive in document["positive_evidence"]:
            if not isinstance(positive, dict) or not all(
                isinstance(positive.get(field), str) and positive[field].strip()
                for field in ("id", "area", "observed")
            ):
                return False
        for candidate in document["follow_up_candidates"]:
            if not isinstance(candidate, dict) or not all(
                isinstance(candidate.get(field), str) and candidate[field].strip()
                for field in ("observation", "type", "summary")
            ):
                return False
        return True

    @staticmethod
    def _safe_values(value: Any) -> bool:
        if isinstance(value, str):
            try:
                ensure_safe_text(value, "report")
            except ExperienceInputError:
                return False
            return True
        if isinstance(value, dict):
            return all(ExperienceStorage._safe_values(key) and ExperienceStorage._safe_values(item) for key, item in value.items())
        if isinstance(value, list):
            return all(ExperienceStorage._safe_values(item) for item in value)
        return True

    @contextmanager
    def _file_lock(self, report_path: Path):
        lock_path = report_path.with_suffix(report_path.suffix + ".lock")
        for _ in range(500):
            try:
                descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(descriptor)
                break
            except FileExistsError:
                time.sleep(0.01)
        else:
            raise ExperienceStorageError(f"Timed out waiting for FER report lock: {report_path}")
        try:
            yield
        finally:
            lock_path.unlink(missing_ok=True)

    def _reserve_report(self) -> Path:
        number = 1
        while True:
            path = self.reports_root / f"FER-{number:04d}.yml"
            try:
                path.open("x", encoding="utf-8").close()
                return path
            except FileExistsError:
                number += 1
            except OSError as error:
                raise ExperienceStorageError(str(error)) from error

    @staticmethod
    def _atomic_write(path: Path, document: dict[str, Any]) -> None:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
            ) as handle:
                temporary = Path(handle.name)
                yaml.safe_dump(document, handle, sort_keys=False, allow_unicode=True)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except (OSError, yaml.YAMLError) as error:
            try:
                temporary.unlink(missing_ok=True)
            except UnboundLocalError:
                pass
            raise ExperienceStorageError(str(error)) from error
