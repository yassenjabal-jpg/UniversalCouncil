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


def validate_motion_driver_timing(
    folder: Path,
    mode: str,
    expected_candidate: str,
    timeline: list[dict],
    target_seconds: float,
) -> None:
    path = folder / "motion-driver-timing.json"
    if not path.exists():
        raise SystemExit(f"{mode} real-time motion-driver timing evidence is missing")

    driver = load(path)
    if driver.get("evidence_type") != "WPF_REALTIME_MOTION_DRIVER_TIMING":
        raise SystemExit(f"{mode} motion-driver evidence type drifted")
    if str(driver.get("candidate_sha", "")).lower() != expected_candidate:
        raise SystemExit(f"{mode} motion-driver timing is not bound to the exact candidate SHA")
    if driver.get("clock") != "STOPWATCH_REALTIME_WPF_DRIVER":
        raise SystemExit(f"{mode} motion-driver clock drifted")
    if driver.get("timing_authority") is not True or driver.get("capture_observer") is not False:
        raise SystemExit(f"{mode} motion-driver timing authority drifted")
    if driver.get("scheduler") != "DEDICATED_STOPWATCH_WORKER_TO_DISPATCHER_SEND":
        raise SystemExit(f"{mode} motion-driver scheduler drifted")
    if driver.get("dispatcher_timer_timing_authority") is not False:
        raise SystemExit(f"{mode} motion-driver restored DispatcherTimer timing authority")
    if driver.get("scheduler_thread_priority") != "ABOVE_NORMAL_BEST_EFFORT":
        raise SystemExit(f"{mode} motion-driver scheduler priority evidence drifted")
    if driver.get("lateness_semantics") != "DISPATCH_START_MINUS_TARGET":
        raise SystemExit(f"{mode} motion-driver lateness semantics drifted")
    if driver.get("execution_duration_reported_separately") is not True:
        raise SystemExit(f"{mode} motion-driver stopped separating execution duration")
    if driver.get("mode") != mode or driver.get("reduced_motion") is not (mode == "reduced"):
        raise SystemExit(f"{mode} motion-driver mode drifted")
    if driver.get("mp4_reference") is not False:
        raise SystemExit(f"{mode} P1 timing was replaced by focused MP4 timing")

    target = float(driver.get("target_duration_seconds", 0))
    actual = float(driver.get("actual_duration_seconds", 0))
    if abs(target - target_seconds) > 0.001:
        raise SystemExit(f"{mode} motion-driver target duration drifted")
    if abs(actual - target) > 1.25:
        raise SystemExit(
            f"{mode} real WPF timing exceeded tolerance "
            f"({actual:.3f}s actual vs {target:.3f}s target)"
        )
    if float(driver.get("max_step_lateness_ms", 999999)) > 100:
        raise SystemExit(f"{mode} real WPF semantic timing missed cadence by more than 100ms")

    driver_steps = driver.get("steps")
    if not isinstance(driver_steps, list) or not driver_steps:
        raise SystemExit(f"{mode} motion-driver semantic timeline is missing")
    for item in driver_steps:
        for key in ("ActualSeconds", "CompletedSeconds", "LatenessMs", "ExecutionMs"):
            if key not in item:
                raise SystemExit(f"{mode} motion-driver step timing field is missing: {key}")
        if float(item["CompletedSeconds"]) < float(item["ActualSeconds"]):
            raise SystemExit(f"{mode} motion-driver step completed before dispatch start")
        if float(item["ExecutionMs"]) < 0:
            raise SystemExit(f"{mode} motion-driver step execution duration is invalid")
    computed_max_execution = max(float(item["ExecutionMs"]) for item in driver_steps)
    if abs(float(driver.get("max_step_execution_ms", -1)) - computed_max_execution) > 0.01:
        raise SystemExit(f"{mode} motion-driver max execution duration evidence drifted")
    driver_bindings = [(int(item.get("Frame", -1)), item.get("Name")) for item in driver_steps]
    manifest_bindings = [(int(item.get("frame", -1)), item.get("Name")) for item in timeline]
    if driver_bindings != manifest_bindings:
        raise SystemExit(f"{mode} motion-driver and visual evidence semantic timelines diverged")


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
    pipeline = timing.get("pipeline")
    render_target_pipeline = "RENDERTARGETBITMAP_BGRA_TO_LOSSLESS_X264RGB_THEN_PNG"
    wgc_pipeline = "PERSISTENT_WINDOWS_GRAPHICS_CAPTURE_HWND_BGRA_TO_LOSSLESS_X264RGB_THEN_PNG"
    if pipeline not in {render_target_pipeline, wgc_pipeline}:
        raise SystemExit(f"{mode} recorder pipeline is not governed")

    if timing.get("background_encoder") != "FFMPEG_LIBX264RGB_LOSSLESS_INTERMEDIATE":
        raise SystemExit(f"{mode} background lossless recorder drifted")
    if timing.get("png_encoding_on_wpf_capture_thread") is not False:
        raise SystemExit(f"{mode} recorder reintroduced PNG encoding on the WPF capture thread")
    if timing.get("png_extraction_after_capture") is not True:
        raise SystemExit(f"{mode} PNG extraction moved back into the capture window")
    if timing.get("intermediate_codec") != "LIBX264RGB_CRF0_ULTRAFAST":
        raise SystemExit(f"{mode} lossless intermediate codec drifted")
    if int(timing.get("encoder_queue_capacity_frames", 0)) != 60:
        raise SystemExit(f"{mode} recorder queue capacity drifted")
    if timing.get("synchronous_layout_per_frame") is not False:
        raise SystemExit(f"{mode} recorder reintroduced synchronous layout per frame")
    if int(timing.get("png_compression_level", -1)) != 1:
        raise SystemExit(f"{mode} post-capture PNG compression level drifted")

    target_capture = float(timing.get("target_capture_duration_seconds", 0))
    actual_capture = float(timing.get("actual_capture_duration_seconds", 0))
    if target_capture <= 0 or actual_capture <= 0:
        raise SystemExit(f"{mode} capture timing diagnostics are incomplete")

    if pipeline == render_target_pipeline:
        if timing.get("capture_surface_cache") != "REFERENCE_HOST_AND_CONTEXT_DRAWER_BITMAP_CACHE":
            raise SystemExit(f"{mode} governed WPF capture cache drifted")
        if timing.get("timing_authority") != "COMPANION_MOTION_DRIVER":
            raise SystemExit(f"{mode} RenderTargetBitmap observer claimed real-time timing authority")
        if timing.get("observer_effect") != "RENDER_CAPTURE_DIAGNOSTIC_NOT_REALTIME_AUTHORITY":
            raise SystemExit(f"{mode} RenderTargetBitmap observer-effect label drifted")
        validate_motion_driver_timing(
            folder,
            mode,
            expected_candidate,
            timeline,
            target_capture,
        )
    else:
        if timing.get("capture_surface") != "ACTUAL_COMMAND_CENTER_HWND":
            raise SystemExit(f"{mode} WGC evidence did not capture the actual Command Center HWND")
        if timing.get("fallback_used") is not False:
            raise SystemExit(f"{mode} WGC evidence used a fallback capture surface")
        if timing.get("silent_dxgi_fallback") is not False:
            raise SystemExit(f"{mode} WGC evidence enabled silent DXGI fallback")
        if int(timing.get("source_width", 0)) != int(manifest.get("width", 0)):
            raise SystemExit(f"{mode} WGC source width does not match governed output")
        if int(timing.get("source_height", 0)) != int(manifest.get("height", 0)):
            raise SystemExit(f"{mode} WGC source height does not match governed output")
        if int(timing.get("source_frame_errors", -1)) != 0:
            raise SystemExit(f"{mode} WGC source reported frame errors")
        if float(timing.get("first_frame_latency_ms", 0)) <= 0:
            raise SystemExit(f"{mode} WGC first-frame latency evidence is missing")
        if int(timing.get("unique_sampled_source_frames", 0)) <= 1:
            raise SystemExit(f"{mode} WGC source did not refresh beyond the first frame")
        if int(timing.get("fresh_source_sample_count", 0)) <= 1:
            raise SystemExit(f"{mode} WGC evidence did not sample fresh source frames")
        if abs(actual_capture - target_capture) > 1.25:
            raise SystemExit(
                f"{mode} WGC recorder time dilation exceeded tolerance "
                f"({actual_capture:.3f}s actual vs {target_capture:.3f}s target)"
            )
        if float(timing.get("max_capture_lateness_ms", 999999)) > 100:
            raise SystemExit(f"{mode} WGC recorder missed the sampling cadence by more than 100ms")

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
    parser.add_argument("--wpf-only", action="store_true")
    args = parser.parse_args()
    root = Path(args.evidence_root).resolve()

    validate_motion(root, "full", 20.0)
    validate_motion(root, "reduced", 20.0)
    if not args.wpf_only:
        validate_android(root)
    scope = "WPF-only host evidence" if args.wpf_only else "P1 exit evidence"
    print(f"Al-Murtakaz {scope} validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
