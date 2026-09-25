import pytest
import pandas as pd
import numpy as np
from training.preprocessing.preprocessor import Preprocessor
from training.utils.config_manager import ConfigurationManager

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5],
        'B': ['cat', 'dog', 'cat', 'bird', 'dog'],
        'target': [0, 1, 0, 1, 0]
    })

def test_preprocessor_instantiates():
    cm = ConfigurationManager()
    prep = Preprocessor(cm)
    assert prep is not None
    
def test_handle_missing(sample_df):
    cm = ConfigurationManager()
    prep = Preprocessor(cm)
    df_clean = prep.handle_missing(sample_df, strategy='median')
    assert not df_clean['A'].isnull().any()
    assert df_clean['A'][2] == 3.0 # median of [1,2,4,5]
    
def test_encode_categoricals(sample_df):
    cm = ConfigurationManager()
    prep = Preprocessor(cm)
    df_encoded = prep.encode_categoricals(sample_df, method='label')
    assert pd.api.types.is_numeric_dtype(df_encoded['B'])
    
def test_split_data(sample_df):
    cm = ConfigurationManager()
    prep = Preprocessor(cm)
    # Using small sizes just to test the split logic executes
    splits = prep.split_data(sample_df, target_col='target', test_size=0.2, val_size=0.2, stratify=False)
    assert "X_train" in splits
    assert "y_test" in splits
