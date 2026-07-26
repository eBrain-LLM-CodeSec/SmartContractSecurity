"""Direct singularity-based Codex invoker.

Runs `codex exec` inside the already-built `evmbench-worker.sif` image
without going through the RabbitMQ/instancer job-dispatch machinery --
auditor.py needs a fresh `codex exec` call per candidate anyway (no session
resume), so there is no need for the full job-queue lifecycle just to get a
Codex process talking to a model.

Mirrors the provider shape from `backend/docker/worker/init.py:
_write_codex_proxy_config` (`model_providers.proxy` reading the key from
`OPENAI_API_KEY`), but injects it via `codex exec -c key=value` overrides
instead of a `~/.codex/config.toml` file. That file-based approach is what
the Docker/Singularity worker path uses, and it works there because
`AGENT_DIR` (where the config gets written) *is* the container's `$HOME`
inside that flow. Confirmed live on this cluster's Singularity build that
doesn't hold here: `SINGULARITYENV_HOME` is rejected outright ("Overriding
HOME ... is not permitted" -- also noted in singularity.py's own comment),
and even `--no-home` doesn't reset `$HOME` to the image's baked-in default --
it resolves to the *host* user's real home dir (confirmed: `echo $HOME` ->
`/home/md5344` inside the container), which is unrelated to any per-audit
directory we control and must never be written to (it holds this user's own
real `.codex/` session state). `-c` overrides sidestep the whole problem --
no config file, no dependence on `$HOME` resolution at all.

`wire_api="responses"` is not a free choice: codex-cli 0.104.0 (the version
baked into this .sif, confirmed via `codex --version`) removed `wire_api =
"chat"` outright (hard config-parse error) -- see evmbench CLAUDE.md Run 4.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

WORKER_SIF = Path("/scratch/md5344/evmbench/containers/evmbench-worker.sif")
DEFAULT_OAI_PROXY_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_WIRE_API = "responses"


def proxy_provider_config_args(base_url: str = DEFAULT_OAI_PROXY_BASE_URL,
                                wire_api: str = DEFAULT_WIRE_API) -> list[str]:
    """`-c key=value` overrides equivalent to writing a config.toml with a
    custom `model_providers.proxy` provider reading the key from
    `OPENAI_API_KEY` -- see module docstring for why this, not a file, is
    used to carry the provider config here."""
    base_url = base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"
    overrides = {
        "model_provider": "proxy",
        "model_providers.proxy.name": "proxy",
        "model_providers.proxy.base_url": base_url,
        "model_providers.proxy.wire_api": wire_api,
        "model_providers.proxy.env_key": "OPENAI_API_KEY",
    }
    args = []
    for key, value in overrides.items():
        args += ["-c", f'{key}="{value}"']
    return args


def build_singularity_wrap(cmd: list[str], *, sif_path: Path, agent_dir: Path,
                            extra_binds: list[Path] | None = None) -> list[str]:
    """Wraps an already-built `codex exec ...` argv (see auditor.build_codex_cmd)
    in a `singularity exec` call, bind-mounting `agent_dir` (the audit's own
    checkout tree) plus any `extra_binds` (e.g. the `-o` output file's
    directory, which usually lives under agent4vul's own out/<id>/ tree, a
    sibling of agent_dir, not a descendant) read-write. `--containall
    --no-home` keeps the container from transparently exposing the host's
    real home/scratch tree the way a bare `singularity exec` does by default.
    """
    binds = []
    seen = set()
    for d in [agent_dir, *(extra_binds or [])]:
        d = d.resolve()
        if d in seen:
            continue
        seen.add(d)
        binds += ["--bind", f"{d}:{d}"]
    return [
        "singularity", "exec", "--containall", "--no-home",
        "--pwd", str(agent_dir.resolve()),
        *binds,
        str(sif_path),
        *cmd,
    ]


def inject_proxy_config(cmd: list[str], base_url: str = DEFAULT_OAI_PROXY_BASE_URL,
                         wire_api: str = DEFAULT_WIRE_API) -> list[str]:
    """Inserts the proxy provider's `-c` overrides right after `codex exec`
    (cmd[:2]), before the rest of auditor.build_codex_cmd's flags/prompt."""
    return cmd[:2] + proxy_provider_config_args(base_url=base_url, wire_api=wire_api) + cmd[2:]


def singularity_codex_invoke_factory(*, api_key: str, sif_path: Path = WORKER_SIF,
                                      base_url: str = DEFAULT_OAI_PROXY_BASE_URL,
                                      wire_api: str = DEFAULT_WIRE_API,
                                      runner=subprocess.run):
    """Returns a callable matching auditor.CodexInvoker's protocol
    `(cmd, *, cwd, timeout) -> (ok, output)`, backed by a real `singularity
    exec` subprocess. `runner` is an injectable seam (defaults to
    subprocess.run) so tests can verify the exact command construction
    without spawning anything.
    """

    def invoke(cmd: list[str], *, cwd: str, timeout: int) -> tuple[bool, str]:
        agent_dir = Path(cwd)
        env = {
            **os.environ,
            "SINGULARITYENV_OPENAI_API_KEY": api_key,
            "SINGULARITYENV_CODEX_API_KEY": api_key,
        }

        out_path = _extract_output_path(cmd)
        extra_binds = [out_path.parent] if out_path is not None else None

        configured_cmd = inject_proxy_config(cmd, base_url=base_url, wire_api=wire_api)
        exec_wrapped = build_singularity_wrap(configured_cmd, sif_path=sif_path, agent_dir=agent_dir,
                                               extra_binds=extra_binds)
        try:
            proc = runner(exec_wrapped, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, ""

        # Confirmed live: codex can exit nonzero on a harmless secondary
        # failure (e.g. trying to persist skills state under a read-only
        # path) even though the actual turn completed and -o's output file
        # was written correctly -- same reason run_codex_detect.sh itself
        # checks "is the output file non-empty", not the exit code, as the
        # real success signal. Mirror that here.
        out_path = _extract_output_path(cmd)
        if out_path is not None and out_path.exists() and out_path.stat().st_size > 0:
            return True, proc.stdout
        return proc.returncode == 0, proc.stdout

    return invoke


def _extract_output_path(cmd: list[str]) -> Path | None:
    if "-o" not in cmd:
        return None
    idx = cmd.index("-o")
    if idx + 1 >= len(cmd):
        return None
    return Path(cmd[idx + 1])
