# passtk

CLI password generator/manager. Single-file Python application.

## Commands

```bash
uv sync                              # Install dependencies
uv run tox                           # Full verification (compile + functional + lint)
uv run python -m py_compile passtk/passtk.py   # Syntax check only
uv run python passtk/passtk.py -u -l 2 -n 8    # Functional test (generates password, no save)
uv run flake8 passtk/                          # Lint only
```

## Architecture

- **All logic in one file**: `passtk/passtk.py` (~501 lines)
- **Entry point**: `passtk.passtk:main` (registered in `pyproject.toml` `[project.scripts]`)
- **No test suite**: Verification is manual via tox (compile + functional + lint)
- **No CI/CD**: All testing is local

### Key classes

| Class | Purpose |
|-------|---------|
| `Color` | Terminal color output |
| `Cryptor` | AES-256-CBC encryption with PBKDF2 (backward compatible with legacy ECB) |
| `Password` | Password generation with configurable complexity levels (1-4) |

### Data storage

Passwords stored encrypted in `~/.passtk`. Master password collected via `getpass`.

## Conventions

- **Python 3.6+** (tested on 3.13)
- **flake8**: max-line-length=120, ignores E121,E123,E126,E226,E24,E704,E402
- **Version must be synchronized** between `pyproject.toml` and `setup.py` on release
- **Encryption backward compatibility**: `Cryptor.decrypt()` auto-detects V1 (ECB) vs V2 (CBC) format — never remove legacy ECB decryption support

## Key constraints

- `pycryptodome` is the sole external dependency — avoid adding new ones
- Modifying `Cryptor` requires careful backward-compatibility testing with existing `~/.passtk` files
- Functional test (`-u -l 2 -n 8`) is interactive if `~/.passtk` doesn't exist (it prompts for master password)
- Level 3 uses safe special characters (`!@#$%^&*`), level 4 uses full `string.punctuation`
- `--special-chars` / `-s` overrides level's default special character set (ignored at level 1-2)
- Empty special character set (after `--exclude-ambiguous` filtering) causes error exit

## References

- `DEVELOPMENT.md` — developer quick-start guide
- `CHANGELOG.md` — version history (2013–2022)
- `TODO` — planned features (vim edit mode)