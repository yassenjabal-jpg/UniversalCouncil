from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_motion(root: Path, mode: str, minimum_seconds: float) -> None:
    folder = root / mode
    manifest_path = folder / "motion-evidence-manifest.json"
    integrity_path = folder / "motion-video-integrity.json"
    if not manifest_path.exists() or not integrity_path.exists():
        raise SystemExit(f"missing {mode} motion evidence manifest/integrity")

    manifest = load(manifest_path)
    integrity = load(integrity_path)
    expected_reduced = mode == "reduced"

    if manifest["evidence_type"] != "WPF_P1_CRITICAL_PATH_MOTION":
        raise SystemExit(f"{mode} evidence type drifted")
    if manifest["reduced_motion"] is not expected_reduced:
        raise SystemExit(f"{mode} reduced-motion flag drifted")
    if manifest["runtime_authority"] or manifest["stage8_opened"]:
        raise SystemExit(f"{mode} motion evidence inflated authority")
    if manifest["encoded_duration_seconds"] < minimum_seconds:
        raise SystemExit(f"{mode} motion capture is below duration floor")
    if manifest["frame_count"] != len(manifest["frames"]):
        raise SystemExit(f"{mode} frame manifest is incomplete")

    video = folder / integrity["file"]
    if not video.exists():
        raise SystemExit(f"{mode} encoded video missing")
    if sha256(video) != integrity["sha256"]:
        raise SystemExit(f"{mode} encoded video hash mismatch")
    if float(integrity["duration_seconds"]) < minimum_seconds - 0.25:
        raise SystemExit(f"{mode} encoded video duration is below floor")

    step_names = {item["Name"] for item in manifest["steps"]}
    required = {
        "Navigate Home -> Project Workspace",
        "Navigate Project -> Decision Mode",
        "Navigate Decision -> Recovery/Fork",
        "Navigate Recovery -> Work Receipt",
    }
    if mode == "full":
        required |= {
            "Activate Evidence role and open context",
            "Open Evidence reasoning context",
            "Exercise non-authoritative Request Changes intent",
            "Exercise non-authoritative Fork intent",
            "Navigate Recovery -> Pulse Story",
            "Open Handoff Pulse context",
        }
    if not required.issubset(step_names):
        raise SystemExit(f"{mode} critical-path steps are incomplete")


def validate_android(root: Path) -> None:
    folder = root / "android"
    manifest_path = folder / "android-evidence-manifest.json"
    integrity_path = folder / "android-video-integrity.json"
    if not manifest_path.exists() or not integrity_path.exists():
        raise SystemExit("missing Android evidence manifest/integrity")

    manifest = load(manifest_path)
    integrity = load(integrity_path)
    if manifest["evidence_type"] != "ANDROID_SEMANTIC_COMPANION_P1_PROTOTYPE":
        raise SystemExit("Android evidence type drifted")
    if manifest["platform_target"] != "Android" or not manifest["prototype_fixture"]:
        raise SystemExit("Android evidence is not truthfully labeled as prototype")
    if manifest["runtime_authority"] or manifest["stage8_opened"] or manifest["live_host_dispatch"]:
        raise SystemExit("Android prototype inflated runtime authority")
    if manifest["implementation_surface"] != "mobile web semantic prototype under Android touch emulation":
        raise SystemExit("Android implementation surface label drifted")

    video = folder / integrity["file"]
    if not video.exists() or sha256(video) != integrity["sha256"]:
        raise SystemExit("Android capture hash mismatch")
    if float(integrity["duration_seconds"]) < 12:
        raise SystemExit("Android interaction capture is too short to prove the governed path")

    names = [item["name"] for item in manifest["steps"]]
    required_fragments = [
        "Notification deep-link",
        "Inspect Evidence",
        "Request Changes",
        "Open Project",
        "bounded Pause",
        "Open Pulse",
        "Enable Reduced Motion",
    ]
    for fragment in required_fragments:
        if not any(fragment in name for name in names):
            raise SystemExit(f"Android capture missing step: {fragment}")

    final_state = manifest["final_state"]
    if final_state.get("runtimeAuthority") is not False or final_state.get("stage8Opened") is not False:
        raise SystemExit("Android final state inflated authority")
    if final_state.get("reducedMotion") is not True:
        raise SystemExit("Android capture did not demonstrate Reduced Motion")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", required=True)
    args = parser.parse_args()
    root = Path(args.evidence_root).resolve()

    validate_motion(root, "full", 20.0)
    validate_motion(root, "reduced", 20.0)
    validate_android(root)
    print("Al-Murtakaz P1 exit evidence validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
