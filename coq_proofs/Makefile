# Makefile for Coq Argmin Arabic Proofs

# Coq compiler
COQC=coqc
COQDEP=coqdep

# Source files (in dependency order)
VFILES=Assumptions.v CoreTypes.v Energy.v Generator.v Canonical.v \
       Minimizer.v SyntaxGates.v Maqam.v Theorems.v

# Object files
VOFILES=$(VFILES:.v=.vo)

# Default target
all: $(VOFILES) verify

# Compile Coq files
%.vo: %.v
	$(COQC) -R . ArgminArabic $<

# Dependencies (auto-generated)
.depend: $(VFILES)
	$(COQDEP) -R . ArgminArabic $(VFILES) > .depend

-include .depend

# Verification
verify: $(VOFILES)
	@echo "=== Verification Report ==="
	@echo "Checking for axioms..."
	@grep -Rn "Axiom\|Admitted\|Parameter" *.v | grep -v Assumptions.v || echo "✓ No axioms outside Assumptions.v"
	@echo ""
	@echo "Checking theorem completeness..."
	@grep -c "Qed\." Theorems.v | xargs echo "✓ Theorems with Qed:"
	@echo ""
	@echo "=== Build Complete ==="

# Clean
clean:
	rm -f *.vo *.vok *.vos *.glob .*.aux .depend

# Help
help:
	@echo "Targets:"
	@echo "  all     - Compile all Coq files and verify"
	@echo "  verify  - Run verification checks"
	@echo "  clean   - Remove compiled files"
	@echo "  help    - Show this message"

.PHONY: all verify clean help
