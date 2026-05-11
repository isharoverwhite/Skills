#!/usr/bin/env python3
"""Render AGENTS.md from the bundled template."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    skill_dir = Path(__file__).resolve().parents[1]
    default_template = skill_dir / "references" / "agents-md-template.vi.md"

    parser = argparse.ArgumentParser(description="Render AGENTS.md from template placeholders.")
    parser.add_argument(
        "--template",
        default=str(default_template),
        help="Path to template file (default: bundled Vietnamese template)",
    )
    parser.add_argument("--output", default="AGENTS.md", help="Output AGENTS.md path")
    parser.add_argument("--project-name", default="FutureBoxes v2", help="Project name")
    parser.add_argument("--main-agent", default="main", help="Main coordinator agent name")
    parser.add_argument("--ba-agent", default="agent-ba", help="Business analyst agent name")
    parser.add_argument("--uiux-agent", default="agent-uiux", help="UI/UX agent name")
    parser.add_argument("--react-agent", default="agent-react", help="React developer agent name")
    parser.add_argument("--status-file", default="PROJECT_STATUS.md", help="Project status file")
    parser.add_argument(
        "--comm-log-file",
        default="AGENT_COMMUNICATION.log",
        help="Inter-agent communication log file",
    )
    return parser.parse_args()


def resolve_path(path_arg: str, base_dir: Path) -> Path:
    path = Path(path_arg).expanduser()
    if path.is_absolute():
        return path

    direct = Path.cwd() / path
    if direct.exists():
        return direct

    return base_dir / path


def render_template(content: str, replacements: dict[str, str]) -> str:
    rendered = content
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", rendered)))
    if unresolved:
        unresolved_str = ", ".join(unresolved)
        raise ValueError(f"Unresolved placeholders: {unresolved_str}")

    return rendered


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    template_path = resolve_path(args.template, skill_dir)

    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return 1

    replacements = {
        "PROJECT_NAME": args.project_name,
        "MAIN_AGENT": args.main_agent,
        "BA_AGENT": args.ba_agent,
        "UIUX_AGENT": args.uiux_agent,
        "REACT_AGENT": args.react_agent,
        "STATUS_FILE": args.status_file,
        "COMM_LOG_FILE": args.comm_log_file,
    }

    try:
        template_content = template_path.read_text(encoding="utf-8")
        rendered = render_template(template_content, replacements)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except OSError as exc:
        print(f"[ERROR] Unable to read template: {exc}")
        return 1

    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        print(f"[ERROR] Unable to write output: {exc}")
        return 1

    print(f"[OK] Wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
