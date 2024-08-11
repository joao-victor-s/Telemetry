# Miscellaneous
setup:
	sh scripts/dev-setup.sh

validate:
	pre-commit run --all-files
