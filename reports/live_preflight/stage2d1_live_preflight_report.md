# Stage 2D.1 Live Preflight Report

- Stage: `Stage 2D.1 read-only live preflight completed`
- Mode: `read_only_live_preflight`

## Sanitized JSON

```json
{
  "approval_scope": {
    "computer_use_approved": false,
    "dependency_install_approved": false,
    "feishu_send_approved": false,
    "live_write_approved": false,
    "read_only_live_preflight": true,
    "service_restart_approved": false
  },
  "feishu_gateway": {
    "gateway_config_candidate_paths": [
      "~/.hermes/config.yaml",
      "~/.hermes/.env",
      "~/.hermes/skills"
    ],
    "public_capability_summary": {
      "all_required_capabilities_present": true,
      "detailed_key_names_public": false,
      "missing_required_capabilities": [],
      "required_capabilities_checked": true
    },
    "real_message_sent": false
  },
  "final_trading_notice": "Final trading is manually decided by the user.",
  "hermes": {
    "command_checks": {
      "hermes_gateway_status": {
        "available": true,
        "command": "hermes gateway status",
        "raw_output_written": false,
        "succeeded": true
      },
      "hermes_version": {
        "available": true,
        "command": "hermes --version",
        "raw_output_written": false,
        "succeeded": true
      },
      "which_hermes": {
        "command": "command -v hermes",
        "found": true
      }
    },
    "config_paths": [
      "~/.hermes",
      "~/.hermes/config.yaml",
      "~/.hermes/.env",
      "~/.hermes/SOUL.md",
      "~/.hermes/memories",
      "~/.hermes/skills"
    ],
    "launchctl_summary": {
      "candidate_detected": false,
      "labels_public": false,
      "raw_launchctl_output_written": false,
      "running_candidate_detected": false
    },
    "listening_ports_summary": {
      "command_names_public": false,
      "listening_candidate_detected": false,
      "ports_public": false,
      "raw_lsof_output_written": false
    },
    "path_status": [
      {
        "exists": true,
        "is_dir": true,
        "is_file": false,
        "label": "~/.hermes"
      },
      {
        "exists": true,
        "is_dir": false,
        "is_file": true,
        "label": "~/.hermes/config.yaml"
      },
      {
        "exists": true,
        "is_dir": false,
        "is_file": true,
        "label": "~/.hermes/.env"
      },
      {
        "exists": true,
        "is_dir": false,
        "is_file": true,
        "label": "~/.hermes/SOUL.md"
      },
      {
        "exists": true,
        "is_dir": true,
        "is_file": false,
        "label": "~/.hermes/memories"
      },
      {
        "exists": true,
        "is_dir": true,
        "is_file": false,
        "label": "~/.hermes/skills"
      }
    ],
    "process_summary": {
      "keyword_match_detected": true,
      "process_names_public": false,
      "raw_process_output_written": false
    },
    "public_capability_summary": {
      "config_file_has_settings": true,
      "config_file_present": true,
      "detailed_key_names_public": false,
      "env_file_has_settings": true,
      "env_file_present": true,
      "gateway_status_command_succeeded": true,
      "skills_dir_present": true
    }
  },
  "installable_points": {
    "configs/hermes/feishu_loop_notifier_skill.md": true,
    "configs/hermes/feishu_review_command_skill.md": true,
    "ops/review_gate/review_gate.example.json": true,
    "~/.hermes/.env": true,
    "~/.hermes/config.yaml": true,
    "~/.hermes/skills": true
  },
  "local_private_detail_policy": {
    "allowed_private_path": "local_private/stage2d1_live_preflight_private.json",
    "detailed_key_names_public": false,
    "detailed_key_names_written": false,
    "local_private_gitignored": true
  },
  "mode": "read_only_live_preflight",
  "raw_command_output_written": false,
  "safety_flags": {
    "auto_trading_surface": false,
    "computer_use_executed": false,
    "dependencies_installed": false,
    "feishu_gateway_modified": false,
    "feishu_message_sent": false,
    "hermes_modified": false,
    "openclaw_modified": false,
    "real_config_modified": false,
    "secret_values_written": false,
    "secrets_touched": false,
    "services_restarted": false
  },
  "secret_values_written": false,
  "stage": "Stage 2D.1 read-only live preflight completed"
}
```

No secret values, raw command output, absolute local paths, service restarts, dependency installs, Feishu sends, or Computer Use actions are included.

Final trading is manually decided by the user.
