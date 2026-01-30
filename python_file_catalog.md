# Python File Catalog

## Pipeline & orchestration scripts
- `Main_engine.py`: Discovers every `*_engine.py` module, instantiates subclasses of `BaseReconstructionEngine`, runs their `make_df()` helpers, and writes each dataframe into `full_multilayer_grammar.xlsx`, skipping engines that lack the required attributes or fail.
- `export_full_multilayer_grammar_minimal.py`: Guided exporter that imports every phonological/morphological/syntactic/generation engine in order, assembles their sheets into a single Excel file, and documents how `reconstruct_from_base_df` normalizes Unicode/UTF-8 before re-exporting.
- `compare_phonemes_to_export.py`: Loads the phoneme engine output, then reloads the CSV/Excel exports to spot mismatches, print summaries, and sample rows for QA.
- `engine_comparison_report.py`: Prints a textual report contrasting the legacy `sentence_generation_engine` with the enhanced generator, enumerating engine coverage, sentence patterns, verification rules, and recommendations.
- `colabcode.py`: Quick Colab-friendly smoke test that prints Python/PyTorch versions, checks CUDA availability, lists GPUs (via `nvidia-smi`), and runs a tiny tensor on the selected device.
- `reconstruction_utils.py`: Shared helpers for `reconstruct_from_base_df`: it loads phoneme/harakat maps, infers missing diacritics, rebuilds UTF-8/Unicode representations, and exposes CSV helpers so every engine can emit a canonical row.
- `run_server.py`: CLI wrapper that parses `host`, `port`, and `--reload` flags then launches `uvicorn web_app.main:app`, ensuring dependencies like `uvicorn` are installed before starting.

## Engine modules (alphabetical)
- `a3lam_amakin_engine.py`: Populates `أعلام الأماكن` with place-name lexicon entries, pairing geographic labels with their phoneme/haraka profiles to support location-aware generation (data defined inline in this module).
- `a3lam_ashkhas_engine.py`: Curates `أعلام الأشخاص` rows that describe personal names, tagging each with gender/number variants and pronunciation data for stylistic filters (data defined inline in this module).
- `a3lam_manqula_engine.py`: Captures `الأعلام المنقولة` (borrowed names) while recording the phonetic shifts and diacritic cues needed when they appear in formal text (data defined inline in this module).
- `active_participle_engine.py`: Lists `اسم الفاعل` templates sourced from morphological patterns so agents can be aligned with their root phonemes, case markers, and semantic roles (data defined inline in this module).
- `adad_names_engine.py`: Builds `أسماء الأعداد` rows by combining numeral stems with the matching haraka inventories and usage notes for counting phrases (data defined inline in this module).
- `adjective_engine.py`: Enumerates `الصفات` entries along with their meter of vowel patterns, so each adjective carries its phoneme series and agreement hints (data defined inline in this module).
- `afaal_khamsa_engine.py`: Documents `الأفعال_الخمسة`, including the verb forms, the placement of hamza/haraka, and the syntactic restrictions that determine when each waṣl occurs (data defined inline in this module).
- `asma_allah_engine.py`: Records the `أسماء الله الحسنى` with precise phoneme/UTF-8 sequences plus descriptive semantics for devotional generation (data defined inline in this module).
- `asma_allah_murakkaba_engine.py`: Mirrors compound divine names in `أسماء الله المركبة`, preserving their diacritic runs and contextual notes for respectful rendering (data defined inline in this module).
- `aswat_muhdatha_engine.py`: Structures `الأصوات المُحدثة` with sound nouns, phoneme inventories, and context tags to tie acoustic imagery to generated text (data defined inline in this module).
- `binaa_engine.py`: Differentiates `البناء` vs. `المعرب` entries, flagging how phoneme/haraka choices change when a lexeme is fixed or derived (data defined inline in this module).
- `common_attributes_engine.py`: Captures `الصفات المشتركة` metadata (shared haraka patterns, morphology) that other engines reuse when reconstructing UTF-8 (data defined inline in this module).
- `demonstratives_engine.py`: Loads phoneme/haraka CSVs, enumerates canonical demonstratives with their phonetic/diacritic rows, prints diagnostics, and returns a dataframe for the `اسم_الإشارة` sheet, sourcing data from the local `Phonemes.csv` and `Harakat.csv` files.
- `enhanced_sentence_generation_engine.py`: Synthesizes `جُمَل_مولدة_محسّنة` by sampling from verbs, nouns, particles, and rules that enforce agreement, then annotates each sentence with its component phonemes and validation status (data defined inline in this module).
- `fael_engine.py`: Fills `الفاعل` with agent patterns, listing their roots, case counts, and haraka/phoneme sequences so the gate knows which tokens should be raised (data defined inline in this module).
- `gender_engine.py`: Powers `النوع` by lining up masculine/feminine forms with the harakat toggles that drive number agreement and derivational suffixes (data defined inline in this module).
- `generic_nouns_engine.py`: Supplies `أسماء الجنس` entries keyed by semantic classes plus the phoneme runs that keep them generic in generation (data defined inline in this module).
- `haal_engine.py`: Describes `الحال` states through adverbial fillers, capturing their vowel patterns to signal how they attach to verbs or nouns (data defined inline in this module).
- `ijaz_itnab_engine.py`: Compiles `الإيجاز_والإطناب` examples, tracking the dislocation of harakat and the rhetorical contrast that defines brevity vs. embellishment (data defined inline in this module).
- `ishtighal_engine.py`: Covers `الاشتغال` derivations (verbal nouns) and their phonetic skeletons so the reconstructor can choose correct patterns (data defined inline in this module).
- `ism_ala_engine.py`: Lists `اسم الآلة` entries with strong ties between instrument semantics and their phoneme/haraka combos for accurate rendering (data defined inline in this module).
- `ism_hay_a_engine.py`: Captures `اسم الهيئة` forms, highlighting the vowels that encode manner/state in descriptive sentences (data defined inline in this module).
- `ism_mamdod_engine.py`: Details `الاسم_الممدود`, surfacing stretched endings, long vowels, and the contexts where they stay stable (data defined inline in this module).
- `ism_manqus_engine.py`: Documents `الاسم_المنقوص` cases, indicating which roots lose yāʼ endings and how harakat shift during inflection (data defined inline in this module).
- `ism_maqsor_engine.py`: Lists `الاسم_المقصور` entries that end with alif, noting their vowel length and the adjustments needed for genitive/accusative positions (data defined inline in this module).
- `ism_marra_engine.py`: Profiles `اسم المرة` nouns with phonemes that mark occurrence counts, aiding sentence builders that talk about repetition (data defined inline in this module).
- `istiara_engine.py`: Tells the `الاستعارة` story by pairing metaphorical expressions with the phoneme/haraka cues that keep their figurative meaning intact (data defined inline in this module).
- `istifham_engine.py`: Streams `full_multilayer_grammar_الاستفهام.csv` into `reconstruct_from_base_df` so the `الاستفهام` sheet mirrors that CSV and documents its question markers.
- `jawab_engine.py`: Recenters `الجواب` particles, documenting how each responds phonologically to preceding interrogatives (data defined inline in this module).
- `jinass_engine.py`: Lists `الجناس` (paronomasia) pairs with parallel phoneme chains to highlight sound-based wordplay (data defined inline in this module).
- `jins_ifradi_engine.py`: Captures `الجنس الإفرادي` forms, detailing their phonetic markers for single or singular noun classes (data defined inline in this module).
- `jins_jamii_engine.py`: Captures `الجنس الجمعي` forms, describing the phoneme clusters that unify collective nouns (data defined inline in this module).
- `kainat_aqila_engine.py`: Records `الكائنات العاقلة`, linking sentient noun entries to their diacritic agreement patterns (data defined inline in this module).
- `kainat_ghair_aqila_engine.py`: Records `الكائنات غير العاقلة`, ensuring inanimate entities carry the right haraka traits (data defined inline in this module).
- `kinaya_engine.py`: Generates `أسماء_الكناية` entries with their substituted phoneme templates so figurative references stay recognizable (data defined inline in this module).
- `mabni_majhool_engine.py`: Fills `المبني_للمجهول` forms, capturing how phoneme sequences shift when voices flip from active to passive (data defined inline in this module).
- `mafoul_ajlih_engine.py`: Lists `المفعول_لأجله` units with the phonetic hooks that tie them to causative intensification (data defined inline in this module).
- `mafoul_bih_engine.py`: Documents `المفعول_به` entries with their standard accusative harakat so verbs can find the correct objects (data defined inline in this module).
- `mafoul_mutlaq_engine.py`: Records `المفعول_المطلق` samples, noting the reiterative phoneme patterns used for emphasis (data defined inline in this module).
- `masdar_sinai_engine.py`: Profiles `المصدر_الصناعي` nouns derived via Sinoidal patterns, spelling out the root/haraka sequences they inherit (data defined inline in this module).
- `mimi_nouns_engine.py`: Describes `الأسماء الميمية` entries with their mim+root phoneme combos, guiding morphological filters that look for pattern-based nouns (data defined inline in this module).
- `mobtada_khabar_engine.py`: Juxtaposes `المبتدأ_والخبر` pairs, capturing how each interacts with case markers and the phonetic cues that keep them separate (data defined inline in this module).
- `mubalagh_sigha_engine.py`: Aggregates `صيغ_المبالغة` (exaggeration forms) plus the haraka changes triggered by intensified roots (data defined inline in this module).
- `muqabala_engine.py`: Documents `المقابلة` pairs, showing the PCM of opposed phoneme/haraka sequences (data defined inline in this module).
- `musatalahat_sharia_engine.py`: Lists `المصطلحات الشرعية` with both their phonological realization and doctrinal definitions (data defined inline in this module).
- `naeb_fael_engine.py`: Supplies `نائب_الفاعل` templates, detailing how the surrogate agent carries the phoneme/haraka load of the missing faʻil (data defined inline in this module).
- `nisba_engine.py`: Captures `النسب` adjectives, tagging each with suffix haraka patterns that express affiliation (data defined inline in this module).
- `particles_engine.py`: Enumerates `الحروف` (particles) along with the cases they govern and their haraka signatures (data defined inline in this module).
- `passive_participle_engine.py`: Documents `اسم المفعول` entries, pulling their passive endings and vowel patterns from root data (data defined inline in this module).
- `place_engine.py`: Lists `المكان` expressions with locale-specific phonemes and the haraka combos that keep them genitive (data defined inline in this module).
- `proper_nouns_engine.py`: Collects `الأعلام` across domains, pairing each with pronunciation notes for consistent naming (data defined inline in this module).
- `qasr_engine.py`: Frames `القصر` connectors, recording how each restricts scope and which harakat fix the meaning (data defined inline in this module).
- `qasr_taqdim_engine.py`: Expands `القصر_والتقديم` entries, highlighting the fronting patterns and diacritics that signal emphasis (data defined inline in this module).
- `saja_engine.py`: Crafts `السجع` grids by aligning rhymed endings with repeated phoneme chains and stylistic notes (data defined inline in this module).
- `sentence_generation_engine.py`: Builds `جُمَل_مولدة` examples from verbs, nouns, particles, and harakat-aware templates, then tags each sentence with its component tokens (data defined inline in this module).
- `sound_engine.py`: Details `الأصوات` entries (onomatopoeic nouns) and their consonant/vowel scaffolds (data defined inline in this module).
- `superlative_engine.py`: Documents `اسم التفضيل` forms, tracking the vowel shifts and comparison context they encode (data defined inline in this module).
- `taajjub_engine.py`: Captures `التعجب` exclamations with their distinctive harakat that push surprise onto the verb/noun (data defined inline in this module).
- `tamyeez_engine.py`: Produces `التمييز` entries with separating nouns and the phoneme accents that mark specification (data defined inline in this module).
- `taqdim_engine.py`: Lays out `التقديم` (fronting) structures with the haraka inversions that signal topical focus (data defined inline in this module).
- `taraduf_engine.py`: Maps `الترادف` synonyms while keeping their parallel phoneme/haraka pairs aligned (data defined inline in this module).
- `tasgheer_engine.py`: Lists `التصغير` diminutives, showing how the harakat sequence collapses as the lexeme shrinks (data defined inline in this module).
- `tashbih_engine.py`: Catalogs `التشبيه` similes with the repeated phoneme hooks linking literal and figurative halves (data defined inline in this module).
- `tibaq_engine.py`: Records `الطباق` (antithesis) pairs, capturing the polarizing phoneme/haraka contrasts (data defined inline in this module).
- `tibaq_muqabala_engine.py`: Extends with `الطباق_والمقابلة` by showing both the polar opposition and counterpart patterns (data defined inline in this module).
- `verbs_engine.py`: Builds `الأفعال` tables containing verb stems, their harakat/mood variations, and constraints for compatibility checks (data defined inline in this module).

## Sentence generation helpers
- `comprehensive_sentence_generator.py`: Loads a long list of engines, samples their tools, filters invalid label combinations, and builds a large set of verified verbal/nominal/interrogative/negative sentences with phonology/morphology summaries for each generated instance.
- `simple_sentence_generator.py`: Safe generator that handles encoding issues, loads a core subset of engines, and emits basic verbal/nominal/prepositional sentences while tracking the originating pattern and components.
- `static_sentence_generator.py`: Uses hard-coded vocabulary dictionaries (fael, verbs, nouns, adjectives, etc.) to produce canonical sentence patterns like basic verbal, nominal, interrogative, and vocative examples when engine data is not available.

## Data & training utilities
- `phonemes_engine.py`: Loads multiple phoneme CSV sources, merges semantics/morphology/syntax/phonetics rows, assigns Unicode/UTF-8/IPA outputs, and exposes helpers to rebuild `full_multilayer_grammar.csv` or match phonemes with the canonical grammar.
- `scripts/prepare_quran_dataset.py`: Normalizes raw Quranic text, strips `<sel>` markers, shuffles verses, and writes train/validation/test JSONL splits based on configurable ratios.
- `scripts/train_transformer_quran.py`: Fine-tunes a HuggingFace transformer for Quran classification: it loads YAML configs, tokenizes the dataset, builds label mappings, trains via the Trainer API, and persists label metadata.

## Tests
- `tests/test_arabic_normalization.py`: Property-based Hypothesis tests that ensure Arabic NFC/NFD normalization is stable and hash digests remain identical after normalization cycles.
