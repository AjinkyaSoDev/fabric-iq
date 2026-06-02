# Fabric IQ — Known Issues & Fixes

## 1. `%pip` magic disabled in Fabric pipelines

**Error:**
```
MagicUsageError: %pip magic command is disabled.
```

**Cause:** Microsoft Fabric disables IPython magic commands (`%pip`, `%conda`) when a notebook runs inside a Data Factory pipeline or scheduled run.

**Fix:** Replace `%pip install` cells with `subprocess`:
```python
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faker", "pandas", "pyarrow"], check=True)
```

**Reference:** https://learn.microsoft.com/en-us/fabric/data-engineering/library-management#inline-installation

---

## 2. `ModuleNotFoundError: No module named 'synth'`

**Error:**
```
tests/test_generators.py:7: in <module>
    from synth.generators import traffic, water
E   ModuleNotFoundError: No module named 'synth'
```

**Cause:** pytest inserts the *test file's* directory (`tests/`) onto `sys.path` by default, not the repo root. The `synth` package lives at the repo root.

**Fix:** Ensure `conftest.py` exists at the repo root (even empty). pytest will then add that directory to `sys.path`.

```python
# conftest.py (repo root) — content can be just this comment
"""Ensures the repository root is on sys.path so tests can import the synth package."""
```

---

## 3. Notebook not found in pipeline

**Symptom:** Pipeline fails saying it cannot find the notebook.

**Fix:** Ensure all 4 notebooks are added as **Notebook activity inputs** in the `GGM_Synthetic_TrafficWater` pipeline. They must be in the same Fabric workspace and have the `FabricIQ` Lakehouse attached.

---

## 4. PowerShell execution policy blocks `run-demo.ps1`

**Error:**
```
run-demo.ps1 cannot be loaded because running scripts is disabled on this system.
```

**Fix:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run-demo.ps1
```
