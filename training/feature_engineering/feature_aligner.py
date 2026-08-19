import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class FeatureAligner:
    """
    FeatureAligner maps completely different IoT cybersecurity datasets
    to a Unified Feature Schema (UFS) for cross-dataset experiments.
    
    Supported datasets:
    1. NF-ToN-IoT-v2 (NetFlow v9 naming)
    2. CICIoT2023 (CICFlowMeter naming)
    """
    
    def __init__(self, config_path: str = 'training/configs/semantic_map.yaml') -> None:
        """
        Initializes the FeatureAligner.
        
        Args:
            config_path (str): Path to the semantic mapping YAML config.
                               Note: the mapping logic is hardcoded here for 
                               robustness, but path is accepted for compatibility.
        """
        self.config_path = config_path
        
        # Hardcoded UFS mapping as the source of truth
        self.ufs_mapping = {
            'nftoniotv2': {
                'FLOW_DURATION_MILLISECONDS': 'flow_duration_ms',
                'IN_BYTES': 'total_fwd_bytes',
                'IN_PKTS': 'total_fwd_packets',
                'OUT_BYTES': 'total_bwd_bytes',
                'PROTOCOL': 'protocol',
                'MIN_IP_PKT_LEN': 'pkt_len_min',
                'MAX_IP_PKT_LEN': 'pkt_len_max',
                'SRC_TO_DST_SECOND_BYTES': 'fwd_rate',
                'DST_TO_SRC_SECOND_BYTES': 'bwd_rate',
                # Derived columns mapping
                'derived_tcp_flag_fin': 'tcp_flag_fin',
                'derived_tcp_flag_syn': 'tcp_flag_syn',
                'derived_tcp_flag_rst': 'tcp_flag_rst',
                'derived_tcp_flag_psh': 'tcp_flag_psh',
                'derived_tcp_flag_ack': 'tcp_flag_ack',
                'derived_tcp_flag_ece': 'tcp_flag_ece',
                'derived_tcp_flag_cwr': 'tcp_flag_cwr',
                'derived_pkt_len_avg': 'pkt_len_avg'
            },
            'ciciot2023': {
                'flow_duration': 'flow_duration_ms',
                'Tot sum': 'total_fwd_bytes',
                'Number': 'total_fwd_packets',
                'Tot size': 'total_bwd_bytes',
                'Min': 'pkt_len_min',
                'Max': 'pkt_len_max',
                'AVG': 'pkt_len_avg',
                'Std': 'pkt_len_std',
                'Srate': 'fwd_rate',
                'Drate': 'bwd_rate',
                'Header_Length': 'header_length',
                'Rate': 'flow_rate',
                'IAT': 'flow_iat',
                'Magnitue': 'magnitude',
                'fin_flag_number': 'tcp_flag_fin',
                'syn_flag_number': 'tcp_flag_syn',
                'rst_flag_number': 'tcp_flag_rst',
                'psh_flag_number': 'tcp_flag_psh',
                'ack_flag_number': 'tcp_flag_ack',
                'ece_flag_number': 'tcp_flag_ece',
                'cwr_flag_number': 'tcp_flag_cwr',
                # Derived columns mapping
                'derived_protocol': 'protocol'
            }
        }
        
        self.unified_feature_names = [
            'flow_duration_ms', 'total_fwd_bytes', 'total_fwd_packets', 'total_bwd_bytes',
            'protocol', 'tcp_flag_fin', 'tcp_flag_syn', 'tcp_flag_rst', 'tcp_flag_psh',
            'tcp_flag_ack', 'tcp_flag_ece', 'tcp_flag_cwr', 'pkt_len_min', 'pkt_len_max',
            'pkt_len_avg', 'pkt_len_std', 'fwd_rate', 'bwd_rate', 'header_length',
            'flow_rate', 'flow_iat', 'magnitude'
        ]

    def _derive_nftoniotv2_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Derives necessary features for the NF-ToN-IoT-v2 dataset.
        
        Args:
            df (pd.DataFrame): The original NF-ToN-IoT-v2 dataframe.
            
        Returns:
            pd.DataFrame: Dataframe with derived columns added.
        """
        logger.info("Deriving NF-ToN-IoT-v2 specific features...")
        df_derived = df.copy()
        
        # Extract TCP flags from bitmask
        if 'TCP_FLAGS' in df_derived.columns:
            # FIN=0x01, SYN=0x02, RST=0x04, PSH=0x08, ACK=0x10, ECE=0x40, CWR=0x80
            flags = df_derived['TCP_FLAGS'].fillna(0).astype(int)
            df_derived['derived_tcp_flag_fin'] = (flags & 0x01).ne(0).astype(int)
            df_derived['derived_tcp_flag_syn'] = (flags & 0x02).ne(0).astype(int)
            df_derived['derived_tcp_flag_rst'] = (flags & 0x04).ne(0).astype(int)
            df_derived['derived_tcp_flag_psh'] = (flags & 0x08).ne(0).astype(int)
            df_derived['derived_tcp_flag_ack'] = (flags & 0x10).ne(0).astype(int)
            df_derived['derived_tcp_flag_ece'] = (flags & 0x40).ne(0).astype(int)
            df_derived['derived_tcp_flag_cwr'] = (flags & 0x80).ne(0).astype(int)
        else:
            logger.warning("TCP_FLAGS column not found in NF-ToN-IoT-v2 dataset.")
            for flag in ['fin', 'syn', 'rst', 'psh', 'ack', 'ece', 'cwr']:
                df_derived[f'derived_tcp_flag_{flag}'] = 0
                
        # Compute average packet length: (IN_BYTES + OUT_BYTES) / (IN_PKTS + OUT_PKTS)
        if all(col in df_derived.columns for col in ['IN_BYTES', 'OUT_BYTES', 'IN_PKTS', 'OUT_PKTS']):
            total_bytes = df_derived['IN_BYTES'] + df_derived['OUT_BYTES']
            total_pkts = df_derived['IN_PKTS'] + df_derived['OUT_PKTS']
            df_derived['derived_pkt_len_avg'] = np.where(total_pkts == 0, 0, total_bytes / total_pkts)
        else:
            logger.warning("Required columns for derived_pkt_len_avg not found.")
            df_derived['derived_pkt_len_avg'] = 0.0
            
        return df_derived

    def _derive_ciciot2023_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Derives necessary features for the CICIoT2023 dataset.
        
        Args:
            df (pd.DataFrame): The original CICIoT2023 dataframe.
            
        Returns:
            pd.DataFrame: Dataframe with derived columns added.
        """
        logger.info("Deriving CICIoT2023 specific features...")
        df_derived = df.copy()
        
        # Derive protocol integer: TCP=6, UDP=17, ICMP=1
        protocol = np.zeros(len(df_derived), dtype=int)
        
        if 'TCP' in df_derived.columns:
            protocol = np.where(df_derived['TCP'] == 1, 6, protocol)
        if 'UDP' in df_derived.columns:
            protocol = np.where(df_derived['UDP'] == 1, 17, protocol)
        if 'ICMP' in df_derived.columns:
            protocol = np.where(df_derived['ICMP'] == 1, 1, protocol)
            
        df_derived['derived_protocol'] = protocol
        
        return df_derived

    def align_dataset(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """
        Maps a specific dataset to the Unified Feature Schema.
        
        Args:
            df (pd.DataFrame): The raw dataframe.
            dataset_name (str): Name of the dataset ('nftoniotv2' or 'ciciot2023').
            
        Returns:
            pd.DataFrame: Aligned dataframe using unified column names.
        """
        dataset_name = dataset_name.lower()
        if dataset_name not in self.ufs_mapping:
            raise ValueError(f"Dataset '{dataset_name}' is not supported. Supported datasets: {list(self.ufs_mapping.keys())}")
        
        logger.info(f"Aligning dataset '{dataset_name}' to Unified Feature Schema...")
        
        # Apply derivations
        if dataset_name == 'nftoniotv2':
            df_processed = self._derive_nftoniotv2_features(df)
        elif dataset_name == 'ciciot2023':
            df_processed = self._derive_ciciot2023_features(df)
            
        # Map columns
        mapping = self.ufs_mapping[dataset_name]
        df_aligned = pd.DataFrame()
        
        for orig_col, ufs_col in mapping.items():
            if orig_col in df_processed.columns:
                df_aligned[ufs_col] = df_processed[orig_col]
            else:
                logger.debug(f"Column '{orig_col}' not found in dataset. Skipping.")
                
        # Ensure all unified features exist in df_aligned (fill missing with 0.0)
        for ufs_col in self.unified_feature_names:
            if ufs_col not in df_aligned.columns:
                df_aligned[ufs_col] = 0.0

        # Carry over the label column
        if dataset_name == 'nftoniotv2':
            if 'Label' in df_processed.columns:
                df_aligned['Label'] = df_processed['Label'].values
        elif dataset_name == 'ciciot2023':
            if 'label' in df_processed.columns:
                df_aligned['Label'] = (df_processed['label'] != 'BenignTraffic').astype(int).values
            elif 'Label' in df_processed.columns:
                df_aligned['Label'] = df_processed['Label'].values

        # Sort columns to ensure identical column ordering
        feature_cols = [c for c in self.unified_feature_names if c in df_aligned.columns]
        if 'Label' in df_aligned.columns:
            df_aligned = df_aligned[feature_cols + ['Label']]
        else:
            df_aligned = df_aligned[feature_cols]

        return df_aligned

    def get_unified_feature_names(self) -> List[str]:
        """
        Returns a list of all potential unified feature names.
        
        Returns:
            List[str]: List of unified feature names.
        """
        return self.unified_feature_names

    def get_alignment_report(self, source_df: pd.DataFrame, target_df: pd.DataFrame, source_name: str, target_name: str) -> Dict[str, Any]:
        """
        Generates a report comparing the source dataframe and aligned dataframe.
        
        Args:
            source_df (pd.DataFrame): The original raw dataframe.
            target_df (pd.DataFrame): The aligned dataframe.
            source_name (str): The name of the source dataset.
            target_name (str): The name of the target/unified dataset representation.
            
        Returns:
            Dict[str, Any]: Dictionary containing mapping report and distributions.
        """
        source_name = source_name.lower()
        mapping = self.ufs_mapping.get(source_name, {})
        
        mapped_features = []
        dropped_features = []
        
        for col in source_df.columns:
            if col in mapping:
                mapped_features.append(col)
            else:
                dropped_features.append(col)
                
        # Only analyze numeric columns for distributions
        numeric_target_df = target_df.select_dtypes(include=[np.number])
        distributions = {}
        for col in numeric_target_df.columns:
            distributions[col] = {
                'mean': float(numeric_target_df[col].mean()),
                'std': float(numeric_target_df[col].std())
            }
            
        report = {
            'source_dataset': source_name,
            'total_source_features': len(source_df.columns),
            'total_mapped_features': len(mapped_features),
            'total_dropped_features': len(dropped_features),
            'mapped_features': mapped_features,
            'dropped_features_sample': dropped_features[:10], # Just a sample to avoid huge output
            'distributions': distributions
        }
        
        return report
