# Inspection — CHG-0005

The Codex adapter Change demonstrated a lifecycle gap: repository review artifacts could be marked passed while a blocking external PR thread remained unresolved. FULL, STANDARD, and FAST completion gates required `review_passed` but did not independently require reconciliation of blocking external review threads.

The Codex publication layout also retained a misleading test name that implied nested relative resources were forbidden even though the intended safe contract permits them beneath a validated publication root.