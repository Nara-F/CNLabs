PYTHON ?= python3
LAB ?=
MODE ?= student
SUITE ?= public
TEST ?=
REPORT_DIR ?= reports
.PHONY: build test grade lint audit validate validate-starter
build:
	$(PYTHON) -m compileall -q netlab labs examples scripts
test: build
	$(PYTHON) -m netlab.grade $(if $(LAB),--lab $(LAB)) --mode $(MODE) --suite $(SUITE) $(if $(IMPL_ROOT),--impl-root "$(IMPL_ROOT)") $(if $(HIDDEN_ROOT),--hidden-root "$(HIDDEN_ROOT)") $(if $(TEST),--test "$(TEST)") --report-dir "$(REPORT_DIR)"
grade: test
lint: build
audit:
	$(PYTHON) scripts/check_public.py --audit
validate-starter:
	$(PYTHON) scripts/check_public.py --validate-starter
validate: audit validate-starter
