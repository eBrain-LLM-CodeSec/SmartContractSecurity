"""codex_runtime.py: verify the singularity command construction and proxy
`-c` overrides without spawning any real subprocess (runner is injected).
"""
from pathlib import Path

from a4v.codex_runtime import (
    build_singularity_wrap,
    inject_proxy_config,
    proxy_provider_config_args,
    singularity_codex_invoke_factory,
)


def test_proxy_provider_config_args_shape():
    args = proxy_provider_config_args(base_url="https://openrouter.ai/api/v1", wire_api="responses")
    joined = " ".join(args)
    assert 'model_provider="proxy"' in joined
    assert 'model_providers.proxy.base_url="https://openrouter.ai/api/v1"' in joined
    assert 'model_providers.proxy.wire_api="responses"' in joined
    assert 'model_providers.proxy.env_key="OPENAI_API_KEY"' in joined
    # every override must be preceded by its own "-c" flag
    assert args.count("-c") == 5


def test_proxy_provider_config_args_does_not_double_append_v1():
    args = proxy_provider_config_args(base_url="https://openrouter.ai/api/v1/", wire_api="responses")
    joined = " ".join(args)
    assert joined.count("/v1") == 1


def test_inject_proxy_config_places_overrides_right_after_codex_exec():
    cmd = ["codex", "exec", "--model", "gpt-5.1-codex-max", "hello"]
    configured = inject_proxy_config(cmd)
    assert configured[:2] == ["codex", "exec"]
    assert configured[-1] == "hello"
    assert "-c" in configured[2:-4]  # overrides land between "exec" and the original flags


def test_build_singularity_wrap_binds_only_agent_dir():
    wrapped = build_singularity_wrap(["codex", "exec", "hello"], sif_path=Path("/x/worker.sif"), agent_dir=Path("/audits/foo"))
    assert wrapped[:3] == ["singularity", "exec", "--containall"]
    assert "--no-home" in wrapped
    assert "--bind" in wrapped
    bind_idx = wrapped.index("--bind")
    assert wrapped[bind_idx + 1] == "/audits/foo:/audits/foo"
    assert wrapped[-3:] == ["codex", "exec", "hello"]


def test_build_singularity_wrap_binds_extra_dirs_for_output_path():
    wrapped = build_singularity_wrap(
        ["codex", "exec", "hello"], sif_path=Path("/x/worker.sif"),
        agent_dir=Path("/audits/foo"), extra_binds=[Path("/out/bar")],
    )
    binds = [wrapped[i + 1] for i, tok in enumerate(wrapped) if tok == "--bind"]
    assert "/audits/foo:/audits/foo" in binds
    assert "/out/bar:/out/bar" in binds


class _FakeRunner:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        class R:
            returncode = 0
            stdout = "ok"
        return R()


def test_invoke_wraps_with_singularity_and_injects_proxy_config(tmp_path):
    agent_dir = tmp_path / "agent"
    agent_dir.mkdir()

    fake = _FakeRunner()
    invoke = singularity_codex_invoke_factory(api_key="sk-test", runner=fake)
    ok, out = invoke(["codex", "exec", "hi"], cwd=str(agent_dir), timeout=30)

    assert ok is True
    assert out == "ok"
    assert len(fake.calls) == 1
    cmd = fake.calls[0]
    assert cmd[:3] == ["singularity", "exec", "--containall"]
    assert 'model_provider="proxy"' in " ".join(cmd)
    assert cmd[-1] == "hi"
    sif_idx = next(i for i, tok in enumerate(cmd) if tok.endswith(".sif"))
    assert cmd[sif_idx + 1 : sif_idx + 3] == ["codex", "exec"]


def test_invoke_succeeds_on_nonzero_exit_if_output_file_is_present(tmp_path):
    """A nonzero exit code must not count as failure if -o's output file was
    actually written non-empty (confirmed live: codex can exit 1 on a
    harmless secondary failure -- e.g. read-only skills dir -- even though
    the real turn completed)."""
    agent_dir = tmp_path / "agent"
    agent_dir.mkdir()
    out_path = agent_dir / "result.json"

    def runner(cmd, **kwargs):
        out_path.write_text("OK")
        class R:
            returncode = 1
            stdout = "..."
        return R()

    invoke = singularity_codex_invoke_factory(api_key="sk-test", runner=runner)
    ok, _ = invoke(["codex", "exec", "-o", str(out_path), "hi"], cwd=str(agent_dir), timeout=30)
    assert ok is True


def test_invoke_fails_on_nonzero_exit_with_no_output_file(tmp_path):
    agent_dir = tmp_path / "agent"
    agent_dir.mkdir()
    out_path = agent_dir / "result.json"

    def runner(cmd, **kwargs):
        class R:
            returncode = 1
            stdout = "boom"
        return R()

    invoke = singularity_codex_invoke_factory(api_key="sk-test", runner=runner)
    ok, _ = invoke(["codex", "exec", "-o", str(out_path), "hi"], cwd=str(agent_dir), timeout=30)
    assert ok is False


def test_invoke_passes_api_key_via_env_not_argv(tmp_path, monkeypatch):
    """The API key must travel via SINGULARITYENV_OPENAI_API_KEY, never as a
    literal argv token (which would leak into process listings/logs)."""
    agent_dir = tmp_path / "agent"
    agent_dir.mkdir()

    captured_env = {}

    def runner(cmd, *, env, **kwargs):
        captured_env.update(env)
        class R:
            returncode = 0
            stdout = "ok"
        return R()

    invoke = singularity_codex_invoke_factory(api_key="sk-super-secret", runner=runner)
    ok, _ = invoke(["codex", "exec", "hi"], cwd=str(agent_dir), timeout=30)

    assert ok is True
    assert captured_env["SINGULARITYENV_OPENAI_API_KEY"] == "sk-super-secret"
    assert captured_env["SINGULARITYENV_CODEX_API_KEY"] == "sk-super-secret"
