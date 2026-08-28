"""Shared write discipline for the exam pipeline scripts.

Three rules, enforced here so every script applies them identically:

1. Outputs are refused when they already exist. Two runs sharing a directory
   is how one run's artifacts silently become another's evidence; the caller
   passes --overwrite to say the clobber is deliberate.
2. Writes are atomic: full text to a temp file beside the destination, fsync,
   then rename. An interrupted run leaves the old file or the new one, never
   a torn half that a later pipeline step could read as complete.
3. Every run writes a manifest recording the sha256 of its input and of each
   output, so any artifact can be tied back to the exact seed it came from.
"""
import hashlib
import json
import os
import tempfile


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path, text):
    dest_dir = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(
        prefix=os.path.basename(path) + ".", suffix=".tmp", dir=dest_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def preexisting(paths, overwrite):
    """The outputs this run may not clobber (empty when --overwrite)."""
    if overwrite:
        return []
    return [p for p in paths if os.path.exists(p)]


def write_run_manifest(path, tool, input_path, output_paths, extra=None):
    payload = {
        "tool": tool,
        "input": {"path": input_path, "sha256": sha256_file(input_path)},
        "outputs": [{"path": p, "sha256": sha256_file(p)}
                    for p in output_paths],
    }
    if extra:
        payload.update(extra)
    atomic_write(path, json.dumps(payload, indent=2) + "\n")
