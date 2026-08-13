# Intent — Run Distribution Verification on main

After CHG-0002 was integrated into `main`, the Tests workflow ran but Distribution Verification did not because its push trigger excludes `main`.

Requirement: every push to `main` must trigger Distribution Verification. No Protocol, CLI, Adapter, or public API behavior changes.
