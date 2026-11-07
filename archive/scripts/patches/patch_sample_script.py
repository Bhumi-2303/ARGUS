with open("scripts/make_demo_samples.py", "r") as f:
    content = f.read()

content = content.replace(
    """        if n_rows > sample_size:
            _, sample_df = train_test_split(
                df_clean,
                test_size=sample_size,
                random_state=seed,
                stratify=df_clean["label"]
            )
        else:
            sample_df = df_clean""",
    """        if n_rows > sample_size:
            _, sample_df = train_test_split(
                df_clean,
                test_size=sample_size,
                random_state=seed,
                stratify=df_clean["label"]
            )
        else:
            # Shuffle while preserving class ratio if we are keeping all rows
            sample_df = df_clean.sample(frac=1.0, random_state=seed).reset_index(drop=True)"""
)

with open("scripts/make_demo_samples.py", "w") as f:
    f.write(content)
