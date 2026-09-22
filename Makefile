.PHONY: reproduce backup-artifacts restore-artifacts

reproduce:
	python scripts/fit_fusion.py
	python scripts/final_eval.py

backup-artifacts:
	@echo "Creating artifacts backup at /tmp/argus_artifacts_backup.tar.gz..."
	tar -czvf /tmp/argus_artifacts_backup.tar.gz artifacts/models artifacts/day1 artifacts/day4 2>/dev/null || tar -czvf /tmp/argus_artifacts_backup.tar.gz artifacts/models artifacts/day4
	sha256sum /tmp/argus_artifacts_backup.tar.gz

restore-artifacts:
	@echo "Restoring artifacts from /tmp/argus_artifacts_backup.tar.gz..."
	tar -xzvf /tmp/argus_artifacts_backup.tar.gz
