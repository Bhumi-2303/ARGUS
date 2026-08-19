"""
Tests for the FeatureAligner module.

Validates that both datasets are correctly mapped to the
Unified Feature Schema (UFS).
"""
import pytest
import numpy as np
import pandas as pd


def _make_nftoniotv2_sample(n: int = 100) -> pd.DataFrame:
    """Create a synthetic NF-ToN-IoT-v2 DataFrame with correct column names."""
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "IPV4_SRC_ADDR": ["192.168.1." + str(i % 255) for i in range(n)],
        "L4_SRC_PORT": rng.randint(1024, 65535, n),
        "IPV4_DST_ADDR": ["10.0.0." + str(i % 255) for i in range(n)],
        "L4_DST_PORT": rng.randint(1, 1024, n),
        "PROTOCOL": rng.choice([6, 17, 1], n),
        "L7_PROTO": rng.randint(0, 200, n),
        "IN_BYTES": rng.randint(0, 100000, n),
        "IN_PKTS": rng.randint(1, 1000, n),
        "OUT_BYTES": rng.randint(0, 100000, n),
        "OUT_PKTS": rng.randint(1, 1000, n),
        "TCP_FLAGS": rng.randint(0, 255, n),  # Bitmask
        "CLIENT_TCP_FLAGS": rng.randint(0, 255, n),
        "SERVER_TCP_FLAGS": rng.randint(0, 255, n),
        "FLOW_DURATION_MILLISECONDS": rng.randint(0, 60000, n),
        "DURATION_IN": rng.randint(0, 30000, n),
        "DURATION_OUT": rng.randint(0, 30000, n),
        "MIN_TTL": rng.randint(0, 128, n),
        "MAX_TTL": rng.randint(128, 255, n),
        "LONGEST_FLOW_PKT": rng.randint(100, 1500, n),
        "SHORTEST_FLOW_PKT": rng.randint(40, 100, n),
        "MIN_IP_PKT_LEN": rng.randint(20, 60, n),
        "MAX_IP_PKT_LEN": rng.randint(100, 1500, n),
        "SRC_TO_DST_SECOND_BYTES": rng.uniform(0, 10000, n),
        "DST_TO_SRC_SECOND_BYTES": rng.uniform(0, 10000, n),
        "SRC_TO_DST_AVG_THROUGHPUT": rng.uniform(0, 100000, n),
        "DST_TO_SRC_AVG_THROUGHPUT": rng.uniform(0, 100000, n),
        "NUM_PKTS_UP_TO_128_BYTES": rng.randint(0, 100, n),
        "NUM_PKTS_128_TO_256_BYTES": rng.randint(0, 50, n),
        "NUM_PKTS_256_TO_512_BYTES": rng.randint(0, 30, n),
        "NUM_PKTS_512_TO_1024_BYTES": rng.randint(0, 20, n),
        "NUM_PKTS_1024_TO_1514_BYTES": rng.randint(0, 10, n),
        "TCP_WIN_MAX_IN": rng.randint(0, 65535, n),
        "TCP_WIN_MAX_OUT": rng.randint(0, 65535, n),
        "RETRANSMITTED_IN_BYTES": rng.randint(0, 10000, n),
        "RETRANSMITTED_IN_PKTS": rng.randint(0, 50, n),
        "RETRANSMITTED_OUT_BYTES": rng.randint(0, 10000, n),
        "RETRANSMITTED_OUT_PKTS": rng.randint(0, 50, n),
        "ICMP_TYPE": rng.randint(0, 20, n),
        "ICMP_IPV4_TYPE": rng.randint(0, 20, n),
        "DNS_QUERY_ID": rng.randint(0, 65535, n),
        "DNS_QUERY_TYPE": rng.randint(0, 50, n),
        "DNS_TTL_ANSWER": rng.randint(0, 86400, n),
        "Label": rng.choice([0, 1], n),
        "Attack": rng.choice(["DDoS", "DoS", "Benign", "Recon"], n),
    })


def _make_ciciot2023_sample(n: int = 100) -> pd.DataFrame:
    """Create a synthetic CICIoT2023 DataFrame with correct column names."""
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "flow_duration": rng.uniform(0, 60000, n),
        "Header_Length": rng.randint(20, 60, n),
        "Duration": rng.uniform(0, 60, n),
        "Rate": rng.uniform(0, 1000, n),
        "Srate": rng.uniform(0, 500, n),
        "Drate": rng.uniform(0, 500, n),
        "fin_flag_number": rng.randint(0, 10, n),
        "syn_flag_number": rng.randint(0, 10, n),
        "rst_flag_number": rng.randint(0, 10, n),
        "psh_flag_number": rng.randint(0, 10, n),
        "ack_flag_number": rng.randint(0, 10, n),
        "ece_flag_number": rng.randint(0, 5, n),
        "cwr_flag_number": rng.randint(0, 5, n),
        "ack_count": rng.randint(0, 100, n),
        "syn_count": rng.randint(0, 100, n),
        "fin_count": rng.randint(0, 50, n),
        "urg_count": rng.randint(0, 10, n),
        "rst_count": rng.randint(0, 50, n),
        "HTTP": rng.choice([0, 1], n),
        "HTTPS": rng.choice([0, 1], n),
        "DNS": rng.choice([0, 1], n),
        "Telnet": rng.choice([0, 1], n),
        "SMTP": rng.choice([0, 1], n),
        "SSH": rng.choice([0, 1], n),
        "IRC": rng.choice([0, 1], n),
        "TCP": rng.choice([0, 1], n),
        "UDP": rng.choice([0, 1], n),
        "DHCP": rng.choice([0, 1], n),
        "ARP": rng.choice([0, 1], n),
        "ICMP": rng.choice([0, 1], n),
        "IPv": rng.choice([0, 1], n),
        "LLC": rng.choice([0, 1], n),
        "Tot sum": rng.uniform(0, 100000, n),
        "Min": rng.uniform(0, 60, n),
        "Max": rng.uniform(60, 1500, n),
        "AVG": rng.uniform(20, 800, n),
        "Std": rng.uniform(0, 500, n),
        "Tot size": rng.uniform(0, 100000, n),
        "IAT": rng.uniform(0, 1000, n),
        "Number": rng.randint(1, 1000, n),
        "Magnitue": rng.uniform(0, 1000, n),  # Note: typo matches real dataset
        "Radius": rng.uniform(0, 500, n),
        "Covariance": rng.uniform(-100, 100, n),
        "Variance": rng.uniform(0, 10000, n),
        "Weight": rng.uniform(0, 100, n),
        "label": rng.choice(["BenignTraffic", "DDoS-SYN_Flood", "Mirai-greeth_flood"], n),
    })


class TestFeatureAligner:
    """Test suite for FeatureAligner."""

    def test_import(self):
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()
        assert aligner is not None

    def test_align_nftoniotv2(self):
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()
        df = _make_nftoniotv2_sample(50)
        aligned = aligner.align_dataset(df, "nftoniotv2")

        # Should have unified column names
        assert "Label" in aligned.columns
        # Should NOT have original-only columns
        assert "IPV4_SRC_ADDR" not in aligned.columns
        assert "Attack" not in aligned.columns
        assert "DNS_QUERY_ID" not in aligned.columns

    def test_align_ciciot2023(self):
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()
        df = _make_ciciot2023_sample(50)
        aligned = aligner.align_dataset(df, "ciciot2023")

        assert "Label" in aligned.columns
        # Should NOT have original columns
        assert "Magnitue" not in aligned.columns
        assert "label" not in aligned.columns

    def test_aligned_columns_match(self):
        """Both datasets should produce the same column set after alignment."""
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        nf_aligned = aligner.align_dataset(_make_nftoniotv2_sample(50), "nftoniotv2")
        cic_aligned = aligner.align_dataset(_make_ciciot2023_sample(50), "ciciot2023")

        nf_cols = set(nf_aligned.columns)
        cic_cols = set(cic_aligned.columns)

        assert nf_cols == cic_cols, f"Column mismatch: NF-only={nf_cols - cic_cols}, CIC-only={cic_cols - nf_cols}"

    def test_no_nans_after_alignment(self):
        """Aligned output should not introduce NaNs in mapped columns."""
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        for name, make_fn in [("nftoniotv2", _make_nftoniotv2_sample),
                               ("ciciot2023", _make_ciciot2023_sample)]:
            aligned = aligner.align_dataset(make_fn(100), name)
            nan_cols = aligned.columns[aligned.isnull().any()].tolist()
            assert len(nan_cols) == 0, f"NaN columns in {name}: {nan_cols}"

    def test_all_numeric_after_alignment(self):
        """All non-target columns should be numeric after alignment."""
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        for name, make_fn in [("nftoniotv2", _make_nftoniotv2_sample),
                               ("ciciot2023", _make_ciciot2023_sample)]:
            aligned = aligner.align_dataset(make_fn(100), name)
            features = aligned.drop(columns=["Label"], errors="ignore")
            non_numeric = features.select_dtypes(exclude=[np.number]).columns.tolist()
            assert len(non_numeric) == 0, f"Non-numeric columns in {name}: {non_numeric}"

    def test_label_preserved(self):
        """Label column should be preserved correctly."""
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        nf = _make_nftoniotv2_sample(50)
        aligned = aligner.align_dataset(nf, "nftoniotv2")
        assert set(aligned["Label"].unique()).issubset({0, 1})

    def test_invalid_dataset_name_raises(self):
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        with pytest.raises((ValueError, KeyError)):
            aligner.align_dataset(pd.DataFrame(), "unknown_dataset")

    def test_get_unified_feature_names(self):
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()
        names = aligner.get_unified_feature_names()
        assert isinstance(names, list)
        assert len(names) >= 10  # Should have at least 10 mapped features

    def test_tcp_flag_derivation_nftoniotv2(self):
        """TCP flags should be correctly extracted from bitmask."""
        from training.feature_engineering.feature_aligner import FeatureAligner
        aligner = FeatureAligner()

        df = _make_nftoniotv2_sample(10)
        # Set a known bitmask: SYN=0x02, ACK=0x10 → 0x12 = 18
        df["TCP_FLAGS"] = 18
        aligned = aligner.align_dataset(df, "nftoniotv2")

        # SYN and ACK flags should be set
        if "tcp_flag_syn" in aligned.columns:
            assert (aligned["tcp_flag_syn"] > 0).all()
        if "tcp_flag_ack" in aligned.columns:
            assert (aligned["tcp_flag_ack"] > 0).all()
        # FIN should NOT be set (bit 0x01 not in 18)
        if "tcp_flag_fin" in aligned.columns:
            assert (aligned["tcp_flag_fin"] == 0).all()
