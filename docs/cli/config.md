# `taupy config`

Inspect and edit your **`taupy.toml`** project configuration from the command-line.

The command is a *group* with three sub-commands:

| Sub-command | Purpose | Example |
|-------------|---------|---------|
| `show`      | Print the whole `taupy.toml` file to stdout. | `taupy config show` |
| `get <key>` | Read a value by *dotted path*.               | `taupy config get dev.port` |
| `set <key> <value>` | Update a value (creates sections on demand). | `taupy config set build.onefile true` |

---

## Usage

```bash
# Show full configuration
taupy config show

# Read a single entry (returns plain value)
taupy config get frontend.type
react

# Change a setting
taupy config set dev.port 9001

# Verify the update
taupy config get dev.port
9001
```

### Value parsing rules
* Booleans: `true` / `false` (case-insensitive)
* Numbers: parsed as `int` or `float` if possible
* Everything else is treated as a string

If the key does not exist, `get` prints an error. `set` will create intermediary tables automatically.

---

## Reference

```
$ taupy config --help
Usage: taupy config [OPTIONS] COMMAND [ARGS]...

  Inspect or edit taupy.toml in the current directory.

Options:
  --help  Show this message and exit.

Commands:
  get   Get a value by dotted path, e.g. build.onefile.
  set   Set a value by dotted path, e.g. dev.port 9000.
  show  Print taupy.toml as-is.
```