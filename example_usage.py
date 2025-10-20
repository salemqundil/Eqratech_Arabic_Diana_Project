#!/usr/bin/env python3
"""
Example: Using the Trained BERT Model

This script demonstrates how to load and use a trained BERT model
for Arabic phoneme processing.
"""

import sys
import os
from pathlib import Path


def example_load_model():
    """Example 1: Load a trained BERT model."""
    print("=" * 70)
    print("Example 1: Loading Trained BERT Model")
    print("=" * 70)
    
    try:
        from transformers import BertForMaskedLM
        from utf8_tokenizer import UTF8PhonemeTokenizer
        
        # Path to the trained model
        model_path = "./output/bert-arabic-phoneme/final_model"
        
        # Check if model exists
        if not Path(model_path).exists():
            print(f"\n⚠️  Model not found at: {model_path}")
            print("Please train the model first using:")
            print("  python run_training.py --config config/training_config.json")
            return False
        
        print(f"\n📁 Loading model from: {model_path}")
        
        # Load the model
        model = BertForMaskedLM.from_pretrained(model_path)
        print("✓ Model loaded successfully")
        
        # Load the tokenizer
        tokenizer = UTF8PhonemeTokenizer()
        vocab_path = os.path.join(model_path, "vocab.json")
        tokenizer.load_vocab(vocab_path)
        print(f"✓ Tokenizer loaded (vocab size: {tokenizer.vocab_size})")
        
        print("\n✅ Model and tokenizer ready for use!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please run: python setup_bert_training.py --install")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def example_tokenize_text():
    """Example 2: Tokenize Arabic text."""
    print("\n" + "=" * 70)
    print("Example 2: Tokenizing Arabic Text")
    print("=" * 70)
    
    try:
        from utf8_tokenizer import UTF8PhonemeTokenizer
        
        # Create tokenizer
        tokenizer = UTF8PhonemeTokenizer()
        tokenizer.build_vocab_from_phonemes()
        
        # Test texts
        test_texts = [
            "مرحبا",
            "السلام عليكم",
            "كيف حالك"
        ]
        
        print(f"\n📝 Tokenizing {len(test_texts)} texts...")
        
        for text in test_texts:
            print(f"\nOriginal: {text}")
            
            # Encode
            encoded = tokenizer.encode(text, padding=True, max_length=20)
            print(f"Encoded IDs: {encoded['input_ids'][:10]}...")
            print(f"Attention mask: {encoded['attention_mask'][:10]}...")
            
            # Decode
            decoded = tokenizer.decode(encoded['input_ids'])
            print(f"Decoded: {decoded}")
        
        print("\n✅ Tokenization complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def example_masked_prediction():
    """Example 3: Make predictions with masked language modeling."""
    print("\n" + "=" * 70)
    print("Example 3: Masked Language Model Prediction")
    print("=" * 70)
    
    try:
        from transformers import BertForMaskedLM
        from utf8_tokenizer import UTF8PhonemeTokenizer
        import torch
        
        # Path to the trained model
        model_path = "./output/bert-arabic-phoneme/final_model"
        
        if not Path(model_path).exists():
            print(f"\n⚠️  Model not found at: {model_path}")
            print("Skipping this example (model not trained yet)")
            return True
        
        # Load model and tokenizer
        print("\n📁 Loading model and tokenizer...")
        model = BertForMaskedLM.from_pretrained(model_path)
        tokenizer = UTF8PhonemeTokenizer()
        tokenizer.load_vocab(os.path.join(model_path, "vocab.json"))
        
        # Test text with mask
        test_text = "مرحبا [MASK] العالم"
        print(f"\n📝 Input text: {test_text}")
        
        # Encode
        inputs = tokenizer.encode(test_text, padding=True, max_length=128)
        input_ids = torch.tensor([inputs['input_ids']])
        attention_mask = torch.tensor([inputs['attention_mask']])
        
        # Get predictions
        print("🔮 Making predictions...")
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = outputs.logits
        
        # Find the masked token position
        mask_token_id = tokenizer.vocab[tokenizer.mask_token]
        mask_position = (input_ids == mask_token_id).nonzero(as_tuple=True)[1]
        
        if len(mask_position) > 0:
            # Get top predictions for the masked position
            mask_pos = mask_position[0].item()
            predicted_token_ids = predictions[0, mask_pos].topk(5).indices
            
            print(f"\n🎯 Top 5 predictions for [MASK]:")
            for i, token_id in enumerate(predicted_token_ids, 1):
                token = tokenizer.inverse_vocab.get(token_id.item(), '[UNK]')
                print(f"  {i}. {token}")
        else:
            print("\n⚠️  No [MASK] token found in input")
        
        print("\n✅ Prediction complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def example_save_load_vocabulary():
    """Example 4: Save and load tokenizer vocabulary."""
    print("\n" + "=" * 70)
    print("Example 4: Save and Load Tokenizer Vocabulary")
    print("=" * 70)
    
    try:
        from utf8_tokenizer import UTF8PhonemeTokenizer
        import tempfile
        
        # Create tokenizer
        print("\n📝 Creating tokenizer...")
        tokenizer = UTF8PhonemeTokenizer()
        tokenizer.build_vocab_from_phonemes()
        print(f"✓ Vocabulary built (size: {tokenizer.vocab_size})")
        
        # Save vocabulary
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_vocab_path = f.name
        
        print(f"\n💾 Saving vocabulary to: {temp_vocab_path}")
        tokenizer.save_vocab(temp_vocab_path)
        
        # Load vocabulary into a new tokenizer
        print("📂 Loading vocabulary into new tokenizer...")
        new_tokenizer = UTF8PhonemeTokenizer()
        new_tokenizer.load_vocab(temp_vocab_path)
        print(f"✓ Vocabulary loaded (size: {new_tokenizer.vocab_size})")
        
        # Verify they're the same
        if tokenizer.vocab_size == new_tokenizer.vocab_size:
            print("\n✅ Vocabulary save/load successful!")
        else:
            print("\n⚠️  Vocabulary sizes don't match")
        
        # Clean up
        os.unlink(temp_vocab_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Run all examples."""
    print("=" * 70)
    print("BERT Model Usage Examples for Arabic Phoneme Processing")
    print("=" * 70)
    print("\nThis script demonstrates how to:")
    print("  1. Load a trained BERT model")
    print("  2. Tokenize Arabic text")
    print("  3. Make predictions with masked language modeling")
    print("  4. Save and load tokenizer vocabulary")
    print()
    
    examples = [
        ("Load Model", example_load_model),
        ("Tokenize Text", example_tokenize_text),
        ("Masked Prediction", example_masked_prediction),
        ("Save/Load Vocab", example_save_load_vocabulary)
    ]
    
    results = []
    
    for name, func in examples:
        try:
            success = func()
            results.append((name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} examples completed successfully")
    
    if passed < total:
        print("\n💡 Tip: Train the model first if you haven't:")
        print("   python run_training.py --config config/training_config.json")


if __name__ == '__main__':
    main()
