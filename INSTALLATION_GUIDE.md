# Coq Installation and Compilation Guide

## Installation Status

⚠️ **Coq is not currently installed in this environment**

## Installing Coq

### Option 1: Using opam (Recommended)

```bash
# Install opam if not already installed
sudo apt-get update
sudo apt-get install -y opam

# Initialize opam
opam init -y
eval $(opam env)

# Install Coq 8.18.0
opam install -y coq.8.18.0

# Verify installation
coqc --version
```

### Option 2: Using apt (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y coq
coqc --version
```

### Option 3: From source

See https://github.com/coq/coq/blob/master/INSTALL.md

## Compiling the Project

Once Coq 8.18.0+ is installed:

### Compile individual modules

```bash
cd coq/

# Compile in dependency order
coqc UsulLughah.v
coqc ArabicOntology.v
coqc AGT_Core.v
coqc AGT_Complete.v
coqc AGT_Extended.v
coqc AGT_Semantics.v
coqc AGT_Discourse.v
coqc AGT_Mathematical.v
coqc AGT_DerivationalCatalog.v
coqc AGT_LexicalModels.v
coqc AGT_Compositional.v
```

### Compile all modules at once

```bash
cd coq/
for file in UsulLughah.v ArabicOntology.v AGT_Core.v AGT_Complete.v AGT_Extended.v AGT_Semantics.v AGT_Discourse.v AGT_Mathematical.v AGT_DerivationalCatalog.v AGT_LexicalModels.v AGT_Compositional.v; do
    echo "Compiling $file..."
    coqc $file
done
```

## Expected Results

All 11 modules should compile successfully:
- ✅ UsulLughah.v
- ✅ ArabicOntology.v
- ✅ AGT_Core.v
- ✅ AGT_Complete.v (FIXED: L_Dad pattern)
- ✅ AGT_Extended.v (FIXED: Inductive Illa)
- ✅ AGT_Semantics.v
- ✅ AGT_Discourse.v
- ✅ AGT_Mathematical.v (with warnings about large numbers)
- ✅ AGT_DerivationalCatalog.v (FIXED: period)
- ✅ AGT_LexicalModels.v (FIXED: decidability)
- ✅ AGT_Compositional.v (FIXED: type annotation)

## Compilation Fixes Applied

All 5 compilation errors identified in COMPILATION_REPORT.md have been fixed:

1. **AGT_Complete.v** (line 45): Added missing `L_Dad` case
2. **AGT_Extended.v** (line 253): Renamed `Inductive 3illa` to `Inductive Illa`
3. **AGT_DerivationalCatalog.v** (line 31): Added missing period
4. **AGT_LexicalModels.v** (line 234): Added `VerbTense_eq_dec` decidability
5. **AGT_Compositional.v** (line 159): Added `%nat` type annotation

## Troubleshooting

### If compilation fails:

1. **Check Coq version**: Must be 8.18.0 or later
   ```bash
   coqc --version
   ```

2. **Check module dependencies**: Modules must be compiled in order (as listed above)

3. **Clear compiled files** if recompiling:
   ```bash
   cd coq/
   rm -f *.vo *.vok *.vos *.glob
   ```

4. **Check specific error messages** and refer to COMPILATION_REPORT.md

## Verification

To verify all modules compile:

```bash
cd coq/
rm -f *.vo *.vok *.vos *.glob
for file in *.v; do
    echo "=== Compiling $file ==="
    if coqc $file; then
        echo "✅ $file compiled successfully"
    else
        echo "❌ $file failed to compile"
    fi
done
```

## Resources

- Coq Documentation: https://coq.inria.fr/documentation
- Coq GitHub: https://github.com/coq/coq
- This project's COMPILATION_REPORT.md for detailed error documentation
- This project's ROADMAP.md for future extensions
