.PHONY: build test check run clean spec

build:
	cargo build --release

test:
	cargo test

check:
	cargo clippy -- -D warnings
	cargo fmt --check

run:
	cargo run --

clean:
	cargo clean

spec:
	XDG_CACHE_HOME="$(CURDIR)/.cache" PATH="$(CURDIR)/target/release:$(PATH)" \
		uv run --extra dev pytest spec/ --mustmatch-lang bash --mustmatch-timeout 60 -v
