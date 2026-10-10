#!/usr/bin/env python3
"""Manage the routed hans-ppt project lifecycle.

Usage:
  python workflow_state.py init WORK --route generate|beautify [--profile default|quick]
  python workflow_state.py confirm WORK stage1|stage2
  python workflow_state.py check WORK --for plan|produce|deliver
  python workflow_state.py status WORK

Default projects have two user gates. Quick projects skip both gates but keep
the same source, planning, production, and QA capabilities.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import SKILL_VERSION, load_json, save_json  # noqa: E402

STATE_FILE = "workflow.json"
ROUTES = {"generate", "beautify"}
PROFILES = {"default", "quick"}
TARGETS = {"plan", "produce", "deliver"}
PRODUCTION_INPUTS = ("deck.json", "style.json", "plan.json", "design_spec.md")
ROUTE_INPUTS = {
    "generate": ("analysis.json",),
    "beautify": ("source_text.json", "deck.draft.json"),
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def state_path(work):
    return Path(work) / STATE_FILE


def load_state(work):
    path = state_path(work)
    if not path.exists():
        raise FileNotFoundError(
            f"缺少 {path}；先运行 workflow_state.py init，旧工作目录可显式使用 --legacy-workspace"
        )
    data = load_json(path)
    if data.get("schema_version") != 1:
        raise ValueError(f"不支持的 workflow schema：{data.get('schema_version')}")
    if data.get("route") not in ROUTES or data.get("profile") not in PROFILES:
        raise ValueError("workflow.json 的 route/profile 无效")
    return data


def init_state(work, route, profile):
    work = Path(work)
    path = state_path(work)
    if path.exists():
        raise FileExistsError(f"{path} 已存在；不要覆盖正在进行的项目")
    work.mkdir(parents=True, exist_ok=True)
    for name in ("sources", "assets", "prompts", "out", "validation"):
        (work / name).mkdir(exist_ok=True)
    gate = "skipped" if profile == "quick" else "pending"
    state = {
        "schema_version": 1,
        "skill_version": SKILL_VERSION,
        "route": route,
        "profile": profile,
        "phase": "plan",
        "gates": {"stage1": gate, "stage2": gate},
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    save_json(state, path)
    return state


def production_fingerprint(work):
    work = Path(work)
    missing = [name for name in PRODUCTION_INPUTS if not (work / name).exists()]
    if missing:
        raise FileNotFoundError("缺少生产输入：" + ", ".join(missing))
    return {
        name: hashlib.sha256((work / name).read_bytes()).hexdigest()
        for name in PRODUCTION_INPUTS
    }


def missing_route_inputs(work, route):
    work = Path(work)
    return [name for name in ROUTE_INPUTS[route] if not (work / name).exists()]


def confirm(work, gate):
    state = load_state(work)
    if state["profile"] == "quick":
        raise ValueError("Quick 模式没有确认门；其门禁在初始化时已标记为 skipped")
    missing = missing_route_inputs(work, state["route"])
    if gate == "stage1" and missing:
        raise FileNotFoundError("Stage 1 前缺少路线输入：" + ", ".join(missing))
    if gate == "stage2" and state["gates"].get("stage1") != "confirmed":
        raise ValueError("必须先完成 Stage 1 沟通契约确认")
    if gate == "stage2":
        state["stage2_fingerprint"] = production_fingerprint(work)
    state["gates"][gate] = "confirmed"
    state["phase"] = "solution" if gate == "stage1" else "produce"
    state[f"{gate}_confirmed_at"] = now_iso()
    state["updated_at"] = now_iso()
    save_json(state, state_path(work))
    return state


def readiness(work, target):
    work = Path(work)
    try:
        state = load_state(work)
    except (FileNotFoundError, ValueError) as exc:
        return False, str(exc)

    gates = state["gates"]
    missing = missing_route_inputs(work, state["route"])
    if missing:
        return False, "缺少路线输入：" + ", ".join(missing)
    if state["profile"] == "default" and gates.get("stage1") != "confirmed":
        return False, "Stage 1 尚未确认：先确认受众、目标、观众结果、交付场景和视觉来源"
    if target in {"produce", "deliver"} and state["profile"] == "default" and gates.get("stage2") != "confirmed":
        return False, "Stage 2 尚未确认：先确认完整页面方案、视觉方向、媒体与备注策略"

    required = []
    if target in {"produce", "deliver"}:
        required = list(PRODUCTION_INPUTS)
    missing = [name for name in required if not (work / name).exists()]
    if missing:
        return False, "缺少生产输入：" + ", ".join(missing)
    if target in {"produce", "deliver"} and state["profile"] == "default":
        current = production_fingerprint(work)
        if state.get("stage2_fingerprint") != current:
            return False, "Stage 2 确认后生产输入发生变化；请重新展示完整方案并再次确认 Stage 2"

    if target == "deliver":
        pptx = work / "out" / "beautified.pptx"
        report = work / "out" / "qa_report.json"
        missing = [str(p.relative_to(work)) for p in (pptx, report) if not p.exists()]
        if missing:
            return False, "缺少交付产物：" + ", ".join(missing)
        try:
            errors = int(load_json(report).get("counts", {}).get("ERROR", 0))
        except Exception as exc:  # noqa: BLE001
            return False, f"无法读取 QA 报告：{exc}"
        if errors:
            return False, f"QA 仍有 {errors} 个 ERROR；修复后重新运行 pipeline.py"
    return True, "ready"


def require_ready(work, target):
    ok, message = readiness(work, target)
    if not ok:
        raise RuntimeError(message)
    return load_state(work)


def mark_complete(work):
    state = load_state(work)
    state["phase"] = "complete"
    state["completed_at"] = now_iso()
    state["updated_at"] = now_iso()
    save_json(state, state_path(work))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("work")
    p.add_argument("--route", required=True, choices=sorted(ROUTES))
    p.add_argument("--profile", default="default", choices=sorted(PROFILES))

    p = sub.add_parser("confirm")
    p.add_argument("work")
    p.add_argument("gate", choices=["stage1", "stage2"])

    p = sub.add_parser("check")
    p.add_argument("work")
    p.add_argument("--for", dest="target", required=True, choices=sorted(TARGETS))

    p = sub.add_parser("status")
    p.add_argument("work")

    a = ap.parse_args()
    try:
        if a.command == "init":
            state = init_state(a.work, a.route, a.profile)
            print(f"initialized {state_path(a.work)} ({state['route']} / {state['profile']})")
        elif a.command == "confirm":
            state = confirm(a.work, a.gate)
            print(f"{a.gate} confirmed ({state['route']} / {state['profile']})")
        elif a.command == "check":
            ok, message = readiness(a.work, a.target)
            print(message)
            return 0 if ok else 1
        else:
            state = load_state(a.work)
            print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
