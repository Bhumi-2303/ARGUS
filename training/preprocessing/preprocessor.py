import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.model_selection import train_test_split

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class Preprocessor:
    """Orchestrates the data preprocessing pipeline."""

    def __init__(self, config: ConfigurationManager):
        """
        Initializes the Preprocessor.
        
        Args:
            config: ConfigurationManager instance.
        """
        self.config = config
        self.logger = get_logger(__name__)
        # Keep track of fitted scalers/encoders for inference time
        self.scalers: Dict[str, Any] = {}
        self.encoders: Dict[str, LabelEncoder] = {}

    def handle_missing(self, df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
        """Handles missing values in the DataFrame."""
        self.logger.info("handling_missing_values", strategy=strategy)
        df_clean = df.copy()
        
        if strategy == 'drop':
            df_clean = df_clean.dropna()
        else:
            for col in df_clean.columns:
                if df_clean[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df_clean[col]):
                        if strategy == 'median':
                            fill_val = df_clean[col].median()
                        elif strategy == 'mean':
                            fill_val = df_clean[col].mean()
                        else:
                            fill_val = df_clean[col].mode()[0]
                        df_clean[col] = df_clean[col].fillna(fill_val)
                    else:
                        # For categoricals, always use mode
                        fill_val = df_clean[col].mode()[0] if not df_clean[col].mode().empty else "UNKNOWN"
                        df_clean[col] = df_clean[col].fillna(fill_val)
                        
        self.logger.debug("missing_values_handled", original_shape=df.shape, new_shape=df_clean.shape)
        return df_clean

    def handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes duplicate rows."""
        self.logger.info("handling_duplicates")
        initial_len = len(df)
        df_clean = df.drop_duplicates()
        dropped = initial_len - len(df_clean)
        self.logger.debug("duplicates_removed", count=dropped)
        return df_clean

    def handle_outliers(self, df: pd.DataFrame, method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """Handles outliers in numeric columns."""
        self.logger.info("handling_outliers", method=method, threshold=threshold)
        df_clean = df.copy()
        
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        
        if method == 'iqr':
            for col in numeric_cols:
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                # Cap the outliers rather than dropping to preserve dataset size
                df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)
        elif method == 'zscore':
            for col in numeric_cols:
                mean = df_clean[col].mean()
                std = df_clean[col].std()
                if std > 0:
                    z_scores = (df_clean[col] - mean) / std
                    # Cap based on z-score threshold (usually 3.0)
                    df_clean[col] = np.where(z_scores > threshold, mean + threshold * std,
                                     np.where(z_scores < -threshold, mean - threshold * std, df_clean[col]))
        else:
            self.logger.warning("unknown_outlier_method", method=method)
            
        return df_clean

    def encode_categoricals(self, df: pd.DataFrame, method: str = 'label') -> pd.DataFrame:
        """Encodes categorical variables."""
        self.logger.info("encoding_categoricals", method=method)
        df_encoded = df.copy()
        cat_cols = df_encoded.select_dtypes(include=['object', 'category']).columns
        
        if method == 'label':
            for col in cat_cols:
                le = LabelEncoder()
                # Convert to string to handle mixed types gracefully
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                self.encoders[col] = le
        elif method == 'onehot':
            df_encoded = pd.get_dummies(df_encoded, columns=cat_cols)
        else:
            self.logger.warning("unknown_encoding_method", method=method)
            
        return df_encoded

    def normalize(self, df: pd.DataFrame, method: str = 'standard', columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Normalizes numeric features."""
        self.logger.info("normalizing_features", method=method)
        df_norm = df.copy()
        
        if columns is None:
            columns = df_norm.select_dtypes(include=[np.number]).columns.tolist()
            
        if not columns:
            return df_norm
            
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            self.logger.warning("unknown_normalization_method", method=method)
            return df_norm
            
        df_norm[columns] = scaler.fit_transform(df_norm[columns])
        self.scalers['main'] = scaler
        
        return df_norm

    def validate_features(self, df: pd.DataFrame) -> bool:
        """Validates that the dataframe is ready for ML (no NaNs, all numeric)."""
        if df.isnull().any().any():
            self.logger.error("validation_failed_nans_present")
            return False
            
        non_numeric = df.select_dtypes(exclude=[np.number]).columns
        if len(non_numeric) > 0:
            self.logger.error("validation_failed_non_numeric_present", columns=non_numeric.tolist())
            return False
            
        return True

    def split_data(self, df: pd.DataFrame, target_col: str, test_size: float = 0.2, 
                   val_size: float = 0.1, random_seed: int = 42, stratify: bool = True) -> Dict[str, Any]:
        """Splits the dataset into train, validation, and test sets."""
        self.logger.info("splitting_data", test_size=test_size, val_size=val_size)
        
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")
            
        X = df.drop(columns=[target_col])
        y = df[target_col]
        
        stratify_col = y if stratify else None
        
        # First split: Train+Val vs Test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_seed, stratify=stratify_col
        )
        
        # Second split: Train vs Val (adjusting val_size relative to remaining data)
        relative_val_size = val_size / (1.0 - test_size)
        stratify_temp = y_temp if stratify else None
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=relative_val_size, random_state=random_seed, stratify=stratify_temp
        )
        
        self.logger.info("data_split_complete", 
                         train_shape=X_train.shape, 
                         val_shape=X_val.shape, 
                         test_shape=X_test.shape)
                         
        return {
            "X_train": X_train, "X_val": X_val, "X_test": X_test,
            "y_train": y_train, "y_val": y_val, "y_test": y_test
        }

    def run_pipeline(self, df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
        """
        Executes the full preprocessing pipeline based on configuration.
        
        Args:
            df: Raw DataFrame.
            target_col: Name of the target variable.
            
        Returns:
            Dict containing the splits (X_train, y_train, etc.)
        """
        self.logger.info("starting_preprocessing_pipeline")
        df_processed = df.copy()
        prep_config = self.config.get("preprocessing", {})
        
        # 1. Duplicates
        if prep_config.get("handle_duplicates", True):
            df_processed = self.handle_duplicates(df_processed)
            
        # 2. Missing Values
        if prep_config.get("handle_missing", True):
            df_processed = self.handle_missing(df_processed, strategy=prep_config.get("missing_strategy", "median"))
            
        # 3. Categoricals
        if prep_config.get("encode_categoricals", True):
            # Target col shouldn't be one-hot encoded with features usually, but label encoding is fine
            df_processed = self.encode_categoricals(df_processed, method=prep_config.get("encoding_method", "label"))
            
        # Separate target for outlier handling and normalization to prevent target leakage/modification
        y = df_processed[target_col]
        X = df_processed.drop(columns=[target_col])
        
        # 4. Outliers (on features only)
        if prep_config.get("handle_outliers", True):
            X = self.handle_outliers(
                X, 
                method=prep_config.get("outlier_method", "iqr"),
                threshold=prep_config.get("outlier_threshold", 1.5)
            )
            
        # 5. Normalize (on features only)
        if prep_config.get("normalize", True):
            X = self.normalize(X, method=prep_config.get("normalization_method", "standard"))
            
        # Recombine to validate
        df_final = pd.concat([X, y], axis=1)
        
        if not self.validate_features(df_final):
            raise ValueError("Preprocessed data failed validation.")
            
        # 6. Split
        split_config = self.config.get("splitting", {})
        splits = self.split_data(
            df=df_final,
            target_col=target_col,
            test_size=split_config.get("test_size", 0.2),
            val_size=split_config.get("val_size", 0.1),
            random_seed=split_config.get("random_seed", 42),
            stratify=split_config.get("stratify", True)
        )
        
        self.logger.info("preprocessing_pipeline_complete")
        return splits
