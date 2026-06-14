#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

FINAL_STATUS = "XIAOJIAO_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH_PASS"
MARKER = "ALL_1012E_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH_CHECKS_OK"
PACKAGE = "docs/audit_packages/xiaojiao_business_surface_denoise_1012E.zip"
MANIFEST = "docs/audit_packages/xiaojiao_business_surface_denoise_1012E_manifest.json"

EXPECTED_FILES = [
    "frontend/xiaojiao-preview.html",
    "docs/foundation/xiaojiao_business_surface_denoise_1012E.md",
    "docs/foundation/xiaojiao_business_surface_denoise_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/visible_text_audit_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/home_surface_after_denoise_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/lesson_focus_after_denoise_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/material_folder_after_denoise_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/candidate_review_after_denoise_1012E.json",
    "samples/xiaojiao_business_surface_denoise_1012E/hands_on_review_checklist_1012E.json",
    "scripts/validate_xiaojiao_business_surface_denoise_1012E.py",
    "docs/audit/xiaojiao_business_surface_denoise_1012E_result.json",
    "docs/audit/xiaojiao_business_surface_denoise_1012E_report.md",
    MANIFEST,
]

VISIBLE_REQUIRED = [
    "今天先处理这一课",
    "四年级 1 班《色彩的感觉》",
    "课时设计",
    "学习单",
    "评价量规",
    "资源参考",
    "轻记录",
    "本课材料夹",
    "这是一版候选稿",
    "你确认后，才会放入本课材料。",
    "需要长任务？打开旧工作台",
]

VISIBLE_FORBIDDEN = [
    "home_light_entry",
    "single_lesson_focus",
    "lesson_material_folder",
    "candidate_review_surface",
    "legacy_deep_task_entry",
    "material_folder_enabled=true",
    "business_progress_enabled=true",
    "review_queue_enabled=true",
    "teacher_review_required=true",
    "formal_apply_performed=false",
    "old_strong_agent_page_preserved=true",
    "legacy_agent_as_default=false",
    "work_objecthandout",
    "stub_only",
    "preview stub",
    "later_phase_reserved",
    "live sandbox provider candidate",
    "local fallback",
    "backend sandbox",
    "成本待配置",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def visible_text(html_text: str) -> str:
    text = re.sub(r"<!--.*?-->", " ", html_text, flags=re.S)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def check_js(root: Path, html_text: str):
    scripts = "\n".join(re.findall(r"<script[^>]*>([\s\S]*?)</script>", html_text, flags=re.I))
    probe = "new Function(process.env.XIAOJIAO_SCRIPT_TEXT); console.log('JS_SYNTAX_OK');"
    try:
        result = subprocess.run(
            ["node", "-e", probe],
            cwd=root,
            env={**os.environ, "XIAOJIAO_SCRIPT_TEXT": scripts},
            text=True,
            capture_output=True,
            timeout=20,
        )
    except FileNotFoundError:
        return False, "node_not_found"
    except subprocess.TimeoutExpired:
        return False, "node_timeout"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def load_json(path: Path):
    return json.loads(read_text(path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    checks = []

    def add(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    html_path = root / "frontend/xiaojiao-preview.html"
    add("preview_html_exists", html_path.exists(), "frontend/xiaojiao-preview.html")
    html_text = read_text(html_path) if html_path.exists() else ""
    js_ok, js_detail = check_js(root, html_text) if html_text else (False, "missing_html")
    add("js_syntax_check", js_ok, js_detail)
    teacher_text = visible_text(html_text)

    for term in VISIBLE_REQUIRED:
        add("visible_required:" + term, term in teacher_text, term)
    for term in VISIBLE_FORBIDDEN:
        add("visible_forbidden_removed:" + term, term not in teacher_text, term)

    for rel_path in EXPECTED_FILES:
        add("expected_file:" + rel_path, (root / rel_path).exists(), rel_path)
        if rel_path.endswith(".json") and (root / rel_path).exists():
            try:
                load_json(root / rel_path)
                add("json_parse:" + rel_path, True, rel_path)
            except Exception as exc:
                add("json_parse:" + rel_path, False, str(exc))

    foundation = load_json(root / "docs/foundation/xiaojiao_business_surface_denoise_1012E.json") if (root / "docs/foundation/xiaojiao_business_surface_denoise_1012E.json").exists() else {}
    flags = foundation.get("flags", {})
    expected_flags = {
        "visible_engineering_labels_removed": True,
        "business_model_applied": True,
        "material_folder_enabled": True,
        "review_gate_enabled": True,
        "legacy_entry_enabled": True,
        "preview_route_only": True,
        "default_route_changed": False,
        "formal_apply_performed": False,
        "real_database_written": False,
        "memory_written": False,
        "Feishu_written": False,
        "new_live_provider_call": False,
    }
    for key, value in expected_flags.items():
        add("flag:" + key, flags.get(key) is value, str(flags.get(key)))
    add("foundation_final_status", foundation.get("final_status") == FINAL_STATUS, foundation.get("final_status", ""))
    add("foundation_marker", foundation.get("marker") == MARKER, foundation.get("marker", ""))

    package_files = [root / p for p in EXPECTED_FILES if (root / p).exists()]
    secret_pattern = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+|secret\s*[:=]\s*['\"][^'\"]+|token\s*[:=]\s*['\"][^'\"]+)", re.I)
    secret_hits = []
    absolute_hits = []
    absolute_patterns = [
        re.compile(r"[A-Za-z]:" + r"\\\\"),
        re.compile("/" + "Users" + r"/[^\s'\"]+"),
        re.compile("/" + "mnt" + r"/[^\s'\"]+"),
    ]
    for path in package_files:
        text = read_text(path)
        if secret_pattern.search(text):
            secret_hits.append(path.relative_to(root).as_posix())
        if any(pattern.search(text) for pattern in absolute_patterns):
            absolute_hits.append(path.relative_to(root).as_posix())
    add("no_api_key_leakage", not secret_hits, ",".join(secret_hits))
    add("no_token_secret_key_files", not any(re.search(r"(token|secret|key)", p.name, re.I) for p in package_files), "package filenames")
    add("no_absolute_paths", not absolute_hits, ",".join(absolute_hits))

    manifest_path = root / MANIFEST
    zip_path = root / PACKAGE
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest_entries = sorted(manifest.get("entries", []))
    add("manifest_final_status", manifest.get("final_status") == FINAL_STATUS, manifest.get("final_status", ""))
    add("manifest_marker", manifest.get("marker") == MARKER, manifest.get("marker", ""))

    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as zf:
            zip_entries = sorted(zf.namelist())
        zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        add("zip_exists", True, PACKAGE)
        add("no_backslash_zip_entries", not any("\\" in entry for entry in zip_entries), str(zip_entries))
        add("zip_sha256_matches_manifest", manifest.get("zip_sha256") == zip_sha, zip_sha)
    else:
        zip_entries = []
        add("zip_exists", False, PACKAGE)

    manifest_minus_zip = sorted(set(manifest_entries) - set(zip_entries))
    zip_minus_manifest = sorted(set(zip_entries) - set(manifest_entries))
    add("manifest_minus_zip=[]", bool(manifest_entries) and not manifest_minus_zip, json.dumps(manifest_minus_zip, ensure_ascii=False))
    add("zip_minus_manifest=[]", zip_path.exists() and not zip_minus_manifest, json.dumps(zip_minus_manifest, ensure_ascii=False))

    ok = all(item["ok"] for item in checks)
    result = {
        "stage": "1012E_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH",
        "ok": ok,
        "final_status": FINAL_STATUS if ok else "XIAOJIAO_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH_FAIL",
        "marker": MARKER if ok else "CHECKS_NOT_OK",
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
