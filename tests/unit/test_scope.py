from pathlib import Path

from a4v.scope import filter_function_nodes_by_scope, in_scope_files_for_subproject, parse_scope_files

README = """
# 2023-07-pooltogether

# Scope

| Contract | SLOC | Purpose |
| ----------- | ----------- | ----------- |
| [claimer/src/Claimer.sol](https://github.com/x/claimer/src/Claimer.sol) | 86 | Incentivizes prize claims |
| [vault/src/interfaces/IVaultHooks.sol](https://github.com/x/vault/src/interfaces/IVaultHooks.sol) | 20 | Hooks interface |
| [vault/src/Vault.sol](https://github.com/x/vault/src/Vault.sol) | 540 | Vault |
| [vault/src/VaultFactory.sol](https://github.com/x/vault/src/VaultFactory.sol) | 43 | Factory |

## Out of Scope

1. The Liquidator is out of scope.
"""


def test_parse_scope_files():
    files = parse_scope_files(README)
    assert files == [
        "claimer/src/Claimer.sol",
        "vault/src/interfaces/IVaultHooks.sol",
        "vault/src/Vault.sol",
        "vault/src/VaultFactory.sol",
    ]


def test_stops_at_out_of_scope_section():
    files = parse_scope_files(README)
    assert not any("Liquidator" in f for f in files)


def test_in_scope_files_for_subproject_strips_prefix():
    vault_scope = in_scope_files_for_subproject(README, "vault")
    assert vault_scope == {"src/interfaces/IVaultHooks.sol", "src/Vault.sol", "src/VaultFactory.sol"}
    claimer_scope = in_scope_files_for_subproject(README, "claimer")
    assert claimer_scope == {"src/Claimer.sol"}


def test_filter_function_nodes_by_scope(tmp_path):
    checkout = tmp_path / "vault"
    (checkout / "src").mkdir(parents=True)
    (checkout / "lib" / "openzeppelin").mkdir(parents=True)
    vault_sol = checkout / "src" / "Vault.sol"
    vault_sol.write_text("contract Vault {}")
    oz_sol = checkout / "lib" / "openzeppelin" / "ERC20.sol"
    oz_sol.write_text("contract ERC20 {}")

    node_files = {
        "fn::Vault.withdraw(uint256)": str(vault_sol),
        "fn::ERC20.transfer(address,uint256)": str(oz_sol),
    }
    in_scope = in_scope_files_for_subproject(README, "vault")
    kept = filter_function_nodes_by_scope(list(node_files.keys()), node_files, checkout, in_scope)
    assert kept == ["fn::Vault.withdraw(uint256)"]
