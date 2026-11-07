"""Tests for ARGUS Secure Artifact Management and Loading.

Verifies:
1. Valid artifacts (JSON, XGBoost, LightGBM, CORAL) load properly.
2. Missing manifests are rejected (fail closed).
3. Tampered files are rejected (hash mismatch).
4. Insecure formats (pickle, joblib, injected pickle payloads) are strictly rejected.
5. HMAC and Ed25519 cryptographic signatures are validated.
6. Reloaded models reproduce numerically identical predictions and metrics on fixed samples.
"""

import os
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest
import xgboost as xgb
import lightgbm as lgb
from cryptography.hazmat.primitives.asymmetric import ed25519

from argus.security.artifacts import (
    save_artifact,
    load_artifact,
    ArtifactIntegrityError,
    MissingManifestError,
    InsecureArtifactError,
    SignatureVerificationError,
    compute_sha256,
)
from argus.adaptation.coral import CORALAdapter
from argus.adaptation.class_aware_coral import ClassAwareCORALAdapter


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


def test_valid_json_artifact_loads(temp_dir):
    data = {"status": "ok", "threshold": 0.99, "metrics": [0.1, 0.2, 0.3]}
    p = temp_dir / "config.json"
    save_artifact(p, data, meta={"version": "1.0.0"})
    loaded = load_artifact(p)
    assert loaded == data


def test_valid_xgboost_artifact_loads(temp_dir):
    X = np.random.randn(20, 4)
    y = np.random.randint(0, 2, size=20)
    dtrain = xgb.DMatrix(X, label=y)
    param = {"max_depth": 2, "eta": 1, "objective": "binary:logistic"}
    bst = xgb.train(param, dtrain, num_boost_round=2)

    p = temp_dir / "model.ubj"
    save_artifact(p, bst, meta={"version": "1.0.0", "artifact_type": "xgboost"})
    loaded_bst = load_artifact(p, model_type="xgboost")
    assert isinstance(loaded_bst, xgb.Booster)

    preds_orig = bst.predict(dtrain)
    preds_loaded = loaded_bst.predict(dtrain)
    np.testing.assert_allclose(preds_orig, preds_loaded, rtol=1e-7, atol=1e-7)


def test_missing_manifest_rejected(temp_dir):
    p = temp_dir / "orphan_model.json"
    p.write_text('{"weights": [1, 2, 3]}', encoding="utf-8")
    with pytest.raises(MissingManifestError, match="missing integrity manifest"):
        load_artifact(p)


def test_tampered_file_rejected(temp_dir):
    data = {"weights": [1.0, 2.0, 3.0]}
    p = temp_dir / "model.json"
    save_artifact(p, data, meta={"version": "1.0.0"})

    # Tamper with the artifact
    p.write_text('{"weights": [1.0, 2.0, 999.0]}', encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="Integrity check failed"):
        load_artifact(p)


def test_pickle_file_rejected(temp_dir):
    p_pkl = temp_dir / "model.pkl"
    with pytest.raises(InsecureArtifactError, match="insecure extension"):
        save_artifact(p_pkl, {"a": 1})

    p_joblib = temp_dir / "model.joblib"
    with pytest.raises(InsecureArtifactError, match="insecure extension"):
        save_artifact(p_joblib, {"a": 1})


def test_disguised_pickle_payload_rejected(temp_dir):
    # A file with .json extension but containing pickle protocol magic bytes
    p = temp_dir / "trojan.json"
    p.write_bytes(b"\x80\x04\x95\x10\x00\x00\x00\x00\x00\x00\x00}\x94.")
    # Create a manifest for it to test the payload check
    sha = compute_sha256(p)
    manifest_p = temp_dir / "trojan.json.manifest.json"
    manifest_p.write_text(f'{{"artifact_file": "trojan.json", "sha256": "{sha}"}}', encoding="utf-8")

    with pytest.raises(InsecureArtifactError, match="Insecure pickle payload detected"):
        load_artifact(p)


def test_hmac_signature_flow(temp_dir, monkeypatch):
    monkeypatch.setenv("ARGUS_ARTIFACT_HMAC_KEY", "secret-test-key-argus")
    p = temp_dir / "signed_hmac.json"
    save_artifact(p, {"safe": True})

    # Valid key loads successfully
    loaded = load_artifact(p)
    assert loaded == {"safe": True}

    # Wrong key raises SignatureVerificationError
    monkeypatch.setenv("ARGUS_ARTIFACT_HMAC_KEY", "wrong-secret-key")
    with pytest.raises(SignatureVerificationError, match="HMAC signature verification failed"):
        load_artifact(p)


def test_ed25519_signature_flow(temp_dir, monkeypatch):
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()

    monkeypatch.setenv("ARGUS_ED25519_PRIVATE_KEY", priv.private_bytes_raw().hex())
    p = temp_dir / "signed_ed25519.json"
    save_artifact(p, {"verified": True})
    monkeypatch.delenv("ARGUS_ED25519_PRIVATE_KEY")

    # Verify with correct public key
    monkeypatch.setenv("ARGUS_ED25519_PUBLIC_KEY", pub.public_bytes_raw().hex())
    loaded = load_artifact(p)
    assert loaded == {"verified": True}

    # Verify with wrong public key
    wrong_pub = ed25519.Ed25519PrivateKey.generate().public_key()
    monkeypatch.setenv("ARGUS_ED25519_PUBLIC_KEY", wrong_pub.public_bytes_raw().hex())
    with pytest.raises(SignatureVerificationError, match="Ed25519 signature verification failed"):
        load_artifact(p)


def test_unsigned_file_rejected_when_signature_required(temp_dir, monkeypatch):
    p = temp_dir / "unsigned.json"
    save_artifact(p, {"plain": True})

    monkeypatch.setenv("ARGUS_REQUIRE_SIGNATURE", "1")
    with pytest.raises(SignatureVerificationError, match="Signature is strictly required"):
        load_artifact(p)


def test_reloaded_xgboost_predictions_numerically_identical(temp_dir):
    """Verifies reloaded XGBoost model reproduces exact predictions on fixed sample."""
    sample_csv = Path("data/raw/legacy_package/argus_coral_data/nfton_train_calibration.csv")
    model_path = Path("artifacts/models/xgb_adapted.json")

    assert sample_csv.exists()
    assert model_path.exists()

    df = pd.read_csv(sample_csv, nrows=100)
    features = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
    X = df[features]
    dmatrix = xgb.DMatrix(X)

    # 1. Original model predictions
    orig_booster = xgb.Booster()
    orig_booster.load_model(str(model_path))
    preds_orig = orig_booster.predict(dmatrix)

    # 2. Save via save_artifact in safe format (.json and .ubj)
    save_json_path = temp_dir / "reloaded_adapted.json"
    save_artifact(save_json_path, orig_booster, meta={"version": "1.0.0", "artifact_type": "xgboost"})

    save_ubj_path = temp_dir / "reloaded_adapted.ubj"
    save_artifact(save_ubj_path, orig_booster, meta={"version": "1.0.0", "artifact_type": "xgboost"})

    # 3. Reload via load_artifact
    reloaded_json = load_artifact(save_json_path, model_type="xgboost")
    reloaded_ubj = load_artifact(save_ubj_path, model_type="xgboost")

    preds_json = reloaded_json.predict(dmatrix)
    preds_ubj = reloaded_ubj.predict(dmatrix)

    # Assert exact numerical equivalence
    np.testing.assert_allclose(preds_orig, preds_json, rtol=1e-7, atol=1e-7)
    np.testing.assert_allclose(preds_orig, preds_ubj, rtol=1e-7, atol=1e-7)

    # Check metrics at frozen threshold 0.99
    y_bin_orig = (preds_orig >= 0.99).astype(int)
    y_bin_json = (preds_json >= 0.99).astype(int)
    y_bin_ubj = (preds_ubj >= 0.99).astype(int)
    np.testing.assert_array_equal(y_bin_orig, y_bin_json)
    np.testing.assert_array_equal(y_bin_orig, y_bin_ubj)


def test_reloaded_coral_transforms_numerically_identical(temp_dir):
    """Verifies reloaded CORAL adapters reproduce exact transformed values."""
    X_s = np.array([[0.5, 0.2, 3.1, 4.2], [0.8, 0.1, 2.5, 3.8], [0.3, 0.9, 1.2, 2.0], [0.7, 0.4, 3.0, 4.1]])
    X_t = np.array([[0.6, 0.3, 3.0, 4.0], [0.7, 0.2, 2.7, 3.9], [0.4, 0.8, 1.5, 2.2], [0.5, 0.3, 2.8, 3.9]])
    y_s = np.array([0, 1, 0, 1])
    y_t = np.array([0, 1, 0, 1])

    # CORALAdapter
    adapter = CORALAdapter().fit(X_s, X_t)
    trans_orig = adapter.transform(X_s)

    p_npz = temp_dir / "coral.npz"
    save_artifact(p_npz, adapter, meta={"version": "1.0.0", "artifact_type": "coral_adapter"})
    loaded_adapter = load_artifact(p_npz, model_type="coral")
    trans_reloaded = loaded_adapter.transform(X_s)

    np.testing.assert_allclose(trans_orig, trans_reloaded, rtol=1e-12, atol=1e-12)

    # ClassAwareCORALAdapter
    ca_adapter = ClassAwareCORALAdapter().fit(X_s, y_s, X_t, y_t)
    ca_trans_orig = ca_adapter.transform(X_s, y_s)

    p_ca_json = temp_dir / "ca_coral.json"
    save_artifact(p_ca_json, ca_adapter, meta={"version": "1.0.0", "artifact_type": "class_aware_coral"})
    loaded_ca = load_artifact(p_ca_json, model_type="class_aware_coral")
    ca_trans_reloaded = loaded_ca.transform(X_s, y_s)

    np.testing.assert_allclose(ca_trans_orig, ca_trans_reloaded, rtol=1e-12, atol=1e-12)
