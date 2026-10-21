from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
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
    expected_candidate = os.environ.get("CANDIDATE_SHA", "").strip().lower()

    if not re.fullmatch(r"[0-9a-f]{40}", expected_candidate):
        raise SystemExit("CANDIDATE_SHA is missing or invalid in evidence gate")
    if str(manifest.get("candidate_sha", "")).lower() != expected_candidate:
        raise SystemExit(f"{mode} motion evidence is not bound to the exact candidate SHA")
    if str(integrity.get("candidate_sha", "")).lower() != expected_candidate:
        raise SystemExit(f"{mode} video integrity is not bound to the exact candidate SHA")
    if manifest.get("source_surface") != "ACTUAL_WPF":
        raise SystemExit(f"{mode} motion evidence is not labeled as actual WPF")
    for forbidden_flag in ("optical_flow", "frame_interpolation", "post_produced_animation"):
        if manifest.get(forbidden_flag) is not False:
            raise SystemExit(f"{mode} evidence enabled forbidden processing: {forbidden_flag}")
        if integrity.get(forbidden_flag) is not False:
            raise SystemExit(f"{mode} video integrity enabled forbidden processing: {forbidden_flag}")
    if manifest.get("unedited") is not True or integrity.get("unedited") is not True:
        raise SystemExit(f"{mode} evidence is not declared unedited")

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
    frame_rate = int(manifest["frame_rate"])
    if frame_rate < 20:
        raise SystemExit(f"{mode} motion capture frame rate is below the CI floor")
    if int(integrity.get("frame_rate", 0)) != frame_rate:
        raise SystemExit(f"{mode} video/frame rate binding drifted")
    if manifest.get("raw_frames_included") is not True:
        raise SystemExit(f"{mode} raw-frame evidence flag is missing")
    if manifest.get("semantic_event_timestamps") is not True:
        raise SystemExit(f"{mode} semantic event timestamps are missing")

    for frame in manifest["frames"]:
        raw = folder / "frames" / frame["File"]
        if not raw.exists():
            raise SystemExit(f"{mode} raw frame missing: {frame['File']}")
        if sha256(raw) != frame["Sha256"]:
            raise SystemExit(f"{mode} raw frame hash mismatch: {frame['File']}")

    timeline = manifest.get("steps")
    if not isinstance(timeline, list) or not timeline:
        raise SystemExit(f"{mode} evidence timeline is missing")
    for step in timeline:
        for key in (
            "evidence_step_id",
            "frame",
            "second",
            "occurred_at_seconds",
            "event_type",
            "semantic_object",
            "Name",
        ):
            if key not in step:
                raise SystemExit(f"{mode} evidence timeline missing field: {key}")

    timing = manifest.get("capture_timing")
    if not isinstance(timing, dict):
        raise SystemExit(f"{mode} capture timing evidence is missing")
    if timing.get("clock") != "STOPWATCH_REALTIME_WPF":
        raise SystemExit(f"{mode} capture clock is not real-time WPF")
    if timing.get("pipeline") != "RENDERTARGETBITMAP_BGRA_TO_BACKGROUND_FFMPEG_PNG":
        raise SystemExit(f"{mode} recorder pipeline is not the governed background encoder")
    if timing.get("background_encoder") != "FFMPEG_LOSSLESS_PNG":
        raise SystemExit(f"{mode} background frame encoder drifted")
    if timing.get("png_encoding_on_wpf_capture_thread") is not False:
        raise SystemExit(f"{mode} recorder reintroduced PNG encoding on the WPF capture thread")
    if int(timing.get("encoder_queue_capacity_frames", 0)) != 60:
        raise SystemExit(f"{mode} recorder queue capacity drifted")
    if timing.get("capture_surface_cache") != "REFERENCE_HOST_AND_CONTEXT_DRAWER_BITMAP_CACHE":
        raise SystemExit(f"{mode} governed WPF capture cache drifted")
    if timing.get("synchronous_layout_per_frame") is not False:
        raise SystemExit(f"{mode} recorder reintroduced synchronous layout per frame")
    if int(timing.get("png_compression_level", -1)) != 1:
        raise SystemExit(f"{mode} background PNG compression level drifted")
    target_capture = float(timing.get("target_capture_duration_seconds", 0))
    actual_capture = float(timing.get("actual_capture_duration_seconds", 0))
    if abs(actual_capture - target_capture) > 1.25:
        raise SystemExit(
            f"{mode} recorder time dilation exceeded tolerance "
            f"({actual_capture:.3f}s actual vs {target_capture:.3f}s target)"
        )
    if float(timing.get("max_capture_lateness_ms", 999999)) > 100:
        raise SystemExit(f"{mode} recorder missed the WPF sampling cadence by more than 100ms")

    visibility = manifest.get("motion_visibility")
    if not isinstance(visibility, dict):
        raise SystemExit(f"{mode} motion visibility metrics are missing")

    changed_frames = int(visibility.get("changed_frame_count", 0))
    longest_run = int(visibility.get("longest_changed_run", 0))
    motion_runs = int(visibility.get("motion_run_count", 0))

    fps_scale = frame_rate / 20.0
    if mode == "full":
        minimum_changed_frames = math.ceil(60 * fps_scale)
        minimum_continuous_run = math.ceil(6 * fps_scale)
        if changed_frames < minimum_changed_frames:
            raise SystemExit(
                "full motion capture does not contain enough visibly changing frames "
                f"({changed_frames} < {minimum_changed_frames} at {frame_rate}fps)"
            )
        if longest_run < minimum_continuous_run:
            raise SystemExit("full motion capture still looks like state jumps rather than animation")
        if motion_runs < 8:
            raise SystemExit("full motion capture does not prove enough separate semantic motion events")
    else:
        minimum_changed_frames = math.ceil(8 * fps_scale)
        maximum_continuous_run = math.ceil(3 * fps_scale)
        if changed_frames < minimum_changed_frames:
            raise SystemExit("reduced motion capture lost required discrete state-transition feedback")
        if motion_runs < 8:
            raise SystemExit("reduced motion capture does not prove semantic parity across transitions")
        if longest_run > maximum_continuous_run:
            raise SystemExit("reduced motion capture retained travel/loop motion that should be removed")

    video = folder / integrity["file"]
    if not video.exists():
        raise SystemExit(f"{mode} encoded video missing")
    if sha256(video) != integrity["sha256"]:
        raise SystemExit(f"{mode} encoded video hash mismatch")
    if float(integrity["duration_seconds"]) < minimum_seconds - 0.25:
        raise SystemExit(f"{mode} encoded video duration is below floor")

    step_names = {item["Name"] for item in manifest["steps"]}
    navigation_required = {
        "Navigate Home -> Project Workspace",
        "Navigate Project -> Software Autopilot",
        "Navigate Autopilot -> Studio Project",
        "Navigate Studio -> Decision Mode",
        "Navigate Decision -> Recovery/Fork",
        "Navigate Recovery -> Pulse Story",
        "Navigate Pulse -> Work Receipt",
        "Navigate Receipt -> Home",
    }
    required = set(navigation_required)
    if mode == "full":
        required |= {
            "Activate Evidence role and open context",
            "Exercise non-authoritative Request Changes intent",
            "Exercise non-authoritative Fork intent",
            "Open Handoff Pulse context",
        }
    else:
        required.add("Exercise non-authoritative Fork intent")
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
