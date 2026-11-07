"""ARGUS Secure Artifact Management & Integrity Verification.

Provides safe artifact serialization, pre-deserialization SHA-256 verification,
HMAC / Ed25519 cryptographic signatures, and strict rejection of insecure formats
(pickle, joblib).
"""

from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Optional, Union

import numpy as np


class ArtifactSecurityError(Exception):
    """Base exception for all artifact security and integrity failures."""
    pass


class InsecureArtifactError(ArtifactSecurityError):
    """Raised when an insecure serialization format (e.g., pickle, joblib) is used."""
    pass


class MissingManifestError(ArtifactSecurityError):
    """Raised when an artifact lacks an integrity manifest."""
    pass


class ArtifactIntegrityError(ArtifactSecurityError):
    """Raised when an artifact hash does not match its manifest."""
    pass


class SignatureVerificationError(ArtifactSecurityError):
    """Raised when cryptographic signature verification fails."""
    pass


BANNED_EXTENSIONS = {".pkl", ".pickle", ".joblib", ".pydart"}
PICKLE_MAGIC_PREFIXES = [
    b"\x80\x02",
    b"\x80\x03",
    b"\x80\x04",
    b"\x80\x05",
]


def get_git_commit() -> str:
    """Retrieves current git commit hash, falling back gracefully if unavailable."""
    commit = os.environ.get("ARGUS_GIT_COMMIT")
    if commit:
        return commit.strip()
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown"


def compute_sha256(path: Union[str, Path]) -> str:
    """Computes SHA-256 digest of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _sign_payload(sha256_hash: str) -> tuple[Optional[str], Optional[str]]:
    """Generates an optional HMAC or Ed25519 signature if keys are in environment."""
    # Check HMAC key first
    hmac_key = os.environ.get("ARGUS_ARTIFACT_HMAC_KEY") or os.environ.get("ARGUS_HMAC_KEY")
    if hmac_key:
        sig = hmac.new(
            hmac_key.encode("utf-8"),
            sha256_hash.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return sig, "hmac-sha256"

    # Check Ed25519 signing key
    ed25519_key = os.environ.get("ARGUS_ARTIFACT_SIGNING_KEY") or os.environ.get(
        "ARGUS_ED25519_PRIVATE_KEY"
    )
    if ed25519_key:
        try:
            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization

            ed25519_key = ed25519_key.strip()
            if len(ed25519_key) == 64:
                priv = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(ed25519_key))
            elif "BEGIN PRIVATE KEY" in ed25519_key:
                priv = serialization.load_pem_private_key(ed25519_key.encode(), password=None)
            else:
                priv = ed25519.Ed25519PrivateKey.from_private_bytes(ed25519_key.encode()[:32])

            sig_bytes = priv.sign(sha256_hash.encode("utf-8"))
            return sig_bytes.hex(), "ed25519"
        except Exception as e:
            raise SignatureVerificationError(f"Failed to generate Ed25519 signature: {e}") from e

    return None, None


def _verify_signature(
    sha256_hash: str,
    signature: Optional[str],
    sig_type: Optional[str],
) -> None:
    """Verifies HMAC or Ed25519 signature against environment keys."""
    require_sig = os.environ.get("ARGUS_REQUIRE_SIGNATURE", "0").lower() in ("1", "true", "yes")

    if not signature:
        if require_sig:
            raise SignatureVerificationError(
                "Signature is strictly required by ARGUS_REQUIRE_SIGNATURE but manifest is unsigned."
            )
        return

    if sig_type == "hmac-sha256":
        hmac_key = os.environ.get("ARGUS_ARTIFACT_HMAC_KEY") or os.environ.get("ARGUS_HMAC_KEY")
        if not hmac_key:
            if require_sig:
                raise SignatureVerificationError(
                    "HMAC signature present but ARGUS_ARTIFACT_HMAC_KEY is missing from environment."
                )
            return
        expected_sig = hmac.new(
            hmac_key.encode("utf-8"),
            sha256_hash.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise SignatureVerificationError("HMAC signature verification failed: signature mismatch.")

    elif sig_type == "ed25519":
        verify_key = os.environ.get("ARGUS_ARTIFACT_VERIFY_KEY") or os.environ.get(
            "ARGUS_ED25519_PUBLIC_KEY"
        )
        if not verify_key:
            if require_sig:
                raise SignatureVerificationError(
                    "Ed25519 signature present but ARGUS_ED25519_PUBLIC_KEY is missing from environment."
                )
            return
        try:
            from cryptography.exceptions import InvalidSignature
            from cryptography.hazmat.primitives.asymmetric import ed25519
            from cryptography.hazmat.primitives import serialization

            verify_key = verify_key.strip()
            if len(verify_key) == 64:
                pub = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(verify_key))
            elif "BEGIN PUBLIC KEY" in verify_key:
                pub = serialization.load_pem_public_key(verify_key.encode())
            else:
                pub = ed25519.Ed25519PublicKey.from_public_bytes(verify_key.encode()[:32])

            sig_bytes = bytes.fromhex(signature)
            pub.verify(sig_bytes, sha256_hash.encode("utf-8"))
        except InvalidSignature as e:
            raise SignatureVerificationError("Ed25519 signature verification failed: invalid signature.") from e
        except Exception as e:
            raise SignatureVerificationError(f"Error during Ed25519 verification: {e}") from e
    else:
        raise SignatureVerificationError(f"Unsupported signature type: {sig_type}")


def save_artifact(
    path: Union[str, Path],
    obj: Any,
    meta: Optional[Dict[str, Any]] = None,
) -> Path:
    """Saves a model or data artifact safely with a sidecar integrity manifest.

    Parameters
    ----------
    path : str or Path
        Target destination path for the artifact.
    obj : Any
        Model or object to save. Must use safe formats (XGBoost, LightGBM,
        CORAL, PyTorch weights_only, JSON, or NumPy).
    meta : dict, optional
        Metadata attributes (e.g. version, model type).

    Returns
    -------
    Path
        Absolute path to the saved artifact file.
    """
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(meta or {})

    # Check for forbidden extensions
    if path.suffix.lower() in BANNED_EXTENSIONS:
        raise InsecureArtifactError(
            f"Cannot save artifact with insecure extension '{path.suffix}'. "
            "Use safe formats: .json, .ubj, .txt, .npz, or .pt"
        )

    detected_type = meta.get("artifact_type", "unknown")

    # Serialize object safely
    if obj is not None:
        # XGBoost Booster / Model
        if hasattr(obj, "save_model"):
            obj.save_model(str(path))
            detected_type = "xgboost" if "xgb" in str(type(obj)).lower() else "lightgbm"
        # Custom adapter with save method (CORALAdapter / ClassAwareCORALAdapter)
        elif hasattr(obj, "save") and callable(getattr(obj, "save")):
            obj.save(path)
            detected_type = meta.get("artifact_type", "coral_adapter")
        # NumPy array or dict of arrays
        elif isinstance(obj, np.ndarray):
            if path.suffix == ".npz":
                np.savez(path, array=obj)
            else:
                np.save(path, obj)
            detected_type = "numpy"
        elif isinstance(obj, dict) and all(isinstance(v, np.ndarray) for v in obj.values()):
            np.savez(path, **obj)
            detected_type = "numpy_dict"
        # Plain dict / list
        elif isinstance(obj, (dict, list)):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2)
            detected_type = "json"
        # Raw bytes
        elif isinstance(obj, bytes):
            with open(path, "wb") as f:
                f.write(obj)
            detected_type = "bytes"
        # PyTorch Module or State Dict
        elif "torch" in str(type(obj)).lower() or (
            isinstance(obj, dict) and any("weight" in str(k) for k in obj.keys())
        ):
            import torch

            to_save = obj.state_dict() if hasattr(obj, "state_dict") else obj
            torch.save(to_save, path)
            detected_type = "torch_state_dict"
        else:
            raise InsecureArtifactError(
                f"Object of type '{type(obj)}' cannot be safely serialized without pickle. "
                "Supported types: XGBoost, LightGBM, CORALAdapter, NumPy, Dict, PyTorch state_dict."
            )

    if not path.exists():
        raise FileNotFoundError(f"Artifact file was not written to {path}")

    # Compute hash and signature
    sha256_hash = compute_sha256(path)
    sig, sig_type = _sign_payload(sha256_hash)
    version = meta.get("version", "1.0.0")
    created_at = datetime.now(timezone.utc).isoformat()
    git_commit = get_git_commit()

    manifest = {
        "artifact_file": path.name,
        "sha256": sha256_hash,
        "version": version,
        "created_at": created_at,
        "git_commit": git_commit,
        "artifact_type": detected_type,
        "signature": sig,
        "signature_type": sig_type,
        "metadata": meta,
    }

    manifest_path = Path(f"{path}.manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return path


def _find_manifest(path: Path) -> tuple[Optional[Path], Optional[Dict[str, Any]]]:
    """Locates manifest for an artifact either as sidecar or in INTEGRITY_MANIFEST."""
    # 1. Direct companion manifest: path.ext.manifest.json
    sidecar1 = Path(f"{path}.manifest.json")
    if sidecar1.exists():
        with open(sidecar1, "r", encoding="utf-8") as f:
            return sidecar1, json.load(f)

    # 2. Suffix replacement: path.manifest.json
    sidecar2 = path.with_suffix(".manifest.json")
    if sidecar2.exists():
        with open(sidecar2, "r", encoding="utf-8") as f:
            return sidecar2, json.load(f)

    # 3. Directory-level INTEGRITY_MANIFEST.json
    dir_manifest = path.parent / "INTEGRITY_MANIFEST.json"
    if dir_manifest.exists():
        with open(dir_manifest, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Find entry matching file name or path
            for key, val in data.items():
                if isinstance(val, dict) and "sha256" in val:
                    art_path = val.get("artifact_path", "")
                    if Path(art_path).name == path.name or key == path.stem:
                        manifest_entry = {
                            "artifact_file": path.name,
                            "sha256": val["sha256"],
                            "version": val.get("version", "1.0.0"),
                            "created_at": val.get("created_at", "legacy"),
                            "git_commit": data.get("_description", "manifest"),
                            "artifact_type": val.get("type", "unknown"),
                            "signature": val.get("signature"),
                            "signature_type": val.get("signature_type"),
                        }
                        return dir_manifest, manifest_entry

    return None, None


def load_artifact(
    path: Union[str, Path],
    model_type: Optional[str] = None,
    verify_signature: Optional[bool] = None,
) -> Any:
    """Safely loads an artifact after verifying SHA-256 hash and optional signatures.

    Parameters
    ----------
    path : str or Path
        Path to the artifact file.
    model_type : str, optional
        Explicit type hint ("xgboost", "lightgbm", "coral", "torch", "json", "numpy").
    verify_signature : bool, optional
        Force verification of signature.

    Returns
    -------
    Any
        The safely deserialized model or object.
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")

    # Check for banned extensions
    if path.suffix.lower() in BANNED_EXTENSIONS:
        raise InsecureArtifactError(
            f"Loading insecure artifact '{path.name}' is strictly forbidden. "
            "Pickle and Joblib serialization cannot be safely verified."
        )

    # Check magic bytes for pickle injection
    with open(path, "rb") as f:
        header = f.read(16)
        for prefix in PICKLE_MAGIC_PREFIXES:
            if header.startswith(prefix):
                raise InsecureArtifactError(
                    f"Insecure pickle payload detected in '{path.name}'. Deserialization refused."
                )

    # Locate manifest
    manifest_path, manifest = _find_manifest(path)
    if manifest is None:
        raise MissingManifestError(
            f"Refusing to load unverified artifact: missing integrity manifest for {path}"
        )

    expected_sha256 = manifest.get("sha256")
    if not expected_sha256:
        raise MissingManifestError(f"Manifest at {manifest_path} is missing 'sha256' field.")

    # Verify SHA-256 in constant time
    actual_sha256 = compute_sha256(path)
    if not hmac.compare_digest(actual_sha256, expected_sha256):
        raise ArtifactIntegrityError(
            f"Integrity check failed for {path.name}: "
            f"expected SHA-256 '{expected_sha256}', computed '{actual_sha256}'."
        )

    # Verify signature
    sig = manifest.get("signature")
    sig_type = manifest.get("signature_type")
    if verify_signature is True and not sig:
        raise SignatureVerificationError(f"Signature verification requested but artifact {path.name} is unsigned.")
    _verify_signature(actual_sha256, sig, sig_type)

    # Safe deserialization
    art_type = model_type or manifest.get("artifact_type") or ""

    if art_type == "xgboost" or path.suffix.lower() in (".json", ".ubj") and "xgb" in art_type.lower():
        import xgboost as xgb

        booster = xgb.Booster()
        booster.load_model(str(path))
        return booster

    elif art_type == "lightgbm" or path.suffix.lower() == ".txt":
        import lightgbm as lgb

        return lgb.Booster(model_file=str(path))

    elif art_type in ("coral", "coral_adapter"):
        from argus.adaptation.coral import CORALAdapter

        return CORALAdapter.load(path)

    elif art_type == "class_aware_coral":
        from argus.adaptation.class_aware_coral import ClassAwareCORALAdapter

        return ClassAwareCORALAdapter.load(path)

    elif art_type in ("torch", "torch_state_dict") or path.suffix.lower() in (".pt", ".pth"):
        import torch

        return torch.load(str(path), map_location="cpu", weights_only=True)

    elif path.suffix.lower() == ".safetensors":
        from safetensors.torch import load_file

        return load_file(str(path))

    elif path.suffix.lower() == ".npz":
        return np.load(path, allow_pickle=False)

    elif path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback to bytes if binary
    with open(path, "rb") as f:
        return f.read()
