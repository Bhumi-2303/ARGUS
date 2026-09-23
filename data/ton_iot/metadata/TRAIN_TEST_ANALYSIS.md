# TON_IoT Train/Test Structure Analysis

## 1. Available Splits

The current subset of the TON_IoT dataset includes files under the `train_test` directory. However, upon inspection:
- There is **no pre-defined training split** (e.g., separate `train.csv` files).
- There is **no pre-defined testing split** (e.g., separate `test.csv` files).
- There are **no train/test indicator columns** (e.g., `is_train` or `split` columns) within the CSV files.

The files represent combined subsets intended to be used for machine learning.

## 2. Leakage Possibility

Because there is no pre-defined temporal separation, random train/test splits performed on this data are highly susceptible to **train/test leakage**.

Specifically:
- **Temporal overlap:** Randomly sampling rows for a test set means that the test set will contain events that occurred concurrently with events in the training set.
- **Identical Feature Vectors:** In network and host data, many events might share the exact same feature vectors within a small time window. A random split might place identical or near-identical records in both sets.
- **Overlapping Identifiers:** If source IPs, PIDs, or session IDs are not excluded, the model might memorize these identifiers rather than learning generalizable patterns.

To prevent leakage, temporal separation is strongly recommended if timestamp columns are available (which they are for IoT telemetry, but missing for the processed network dataset).

## 3. Train/Test Separation Strategy

Since the provided datasets are not explicitly partitioned:
- We must not create artificial random splits if temporal ordering is required.
- **Blocked:** Proper temporal splitting of the network dataset is currently blocked because the `ts` (timestamp) column is missing from `train_test_network.csv`.

**Conclusion:** The datasets provide the features and labels needed, but lack the structural separation required to guarantee strict zero-leakage cross-validation without further processing.
