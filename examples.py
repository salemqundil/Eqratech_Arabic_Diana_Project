#!/usr/bin/env python3
"""
Example: Using the BERT Training Pipeline for Arabic Phonemes

This script demonstrates how to:
1. Load and use the UTF-8 tokenizer
2. Run a quick training test
3. Use the trained model
"""

import os
import sys

def example_tokenizer_usage():
    """Example 1: Using the UTF-8 Phoneme Tokenizer"""
    print("="*70)
    print("Example 1: UTF-8 Phoneme Tokenizer")
    print("="*70)
    
    from utf8_tokenizer import UTF8PhonemeTokenizer
    
    # Create and initialize tokenizer
    print("\n1. Creating tokenizer...")
    tokenizer = UTF8PhonemeTokenizer()
    tokenizer.build_vocab_from_phonemes()
    print(f"   Vocabulary size: {len(tokenizer.vocab)} tokens")
    
    # Encode some text
    print("\n2. Encoding Arabic text...")
    test_texts = [
        "السلام عليكم",
        "مرحبا بك",
        "كيف حالك"
    ]
    
    for text in test_texts:
        encoded = tokenizer.encode(text, padding=True, max_length=30)
        print(f"\n   Text: {text}")
        print(f"   Encoded IDs: {encoded['input_ids'][:10]}... (showing first 10)")
        print(f"   Attention Mask: {encoded['attention_mask'][:10]}...")
        
        # Decode back
        decoded = tokenizer.decode(encoded['input_ids'])
        print(f"   Decoded: {decoded}")
    
    # Save tokenizer
    print("\n3. Saving tokenizer...")
    os.makedirs('examples', exist_ok=True)
    tokenizer.save_vocab('examples/example_vocab.json')
    print("   Saved to: examples/example_vocab.json")
    
    return tokenizer


def example_training_config():
    """Example 2: Understanding the training configuration"""
    print("\n" + "="*70)
    print("Example 2: Training Configuration")
    print("="*70)
    
    import json
    
    print("\n1. Loading configuration...")
    with open('config/training_config.json', 'r') as f:
        config = json.load(f)
    
    print("\n2. Key configuration settings:")
    print(f"   Model: {config['model_name']}")
    print(f"   Output directory: {config['output_dir']}")
    print(f"   Training epochs: {config['training']['num_train_epochs']}")
    print(f"   Batch size: {config['training']['per_device_train_batch_size']}")
    print(f"   Learning rate: {config['training']['learning_rate']}")
    
    print("\n3. Curriculum learning stages:")
    if config.get('curriculum_training', {}).get('enabled'):
        for idx, stage in enumerate(config['curriculum_training']['stages'], 1):
            print(f"   Stage {idx}: {stage['name']}")
            print(f"      Max length: {stage['max_length']}")
            print(f"      Epochs: {stage['epochs']}")
    
    return config


def example_quick_training():
    """Example 3: Running a quick training demonstration"""
    print("\n" + "="*70)
    print("Example 3: Quick Training Demonstration")
    print("="*70)
    
    print("\nNOTE: This is a demonstration of the training setup.")
    print("For actual training, run:")
    print("  python run_training.py --config config/training_config.json")
    
    # Show what would happen
    print("\n1. Training pipeline steps:")
    steps = [
        "Check dependencies",
        "Load training configuration",
        "Initialize UTF-8 Phoneme Tokenizer",
        "Build vocabulary from phoneme data",
        "Prepare training and evaluation datasets",
        "Create BERT model (86M parameters)",
        "Run curriculum training (3 stages):",
        "  - Stage 1: Phoneme basics (max_length=128)",
        "  - Stage 2: Word level (max_length=256)",
        "  - Stage 3: Full sequences (max_length=512)",
        "Save model checkpoints",
        "Save final trained model"
    ]
    
    for step in steps:
        print(f"   ✓ {step}")
    
    print("\n2. Expected outputs:")
    print("   - Model checkpoints: ./output/bert-arabic-phoneme/stage_*/checkpoint-*/")
    print("   - Final models: ./output/bert-arabic-phoneme/stage_*/final_model/")
    print("   - Training logs: ./logs/")
    print("   - Tokenizer vocab: ./tokenizers/vocab.json")


def example_using_trained_model():
    """Example 4: How to use a trained model (conceptual)"""
    print("\n" + "="*70)
    print("Example 4: Using Trained Model (After Training)")
    print("="*70)
    
    print("\nAfter training completes, you can use the model like this:")
    print("""
from transformers import BertForMaskedLM
from utf8_tokenizer import UTF8PhonemeTokenizer

# 1. Load the trained model
model_path = './output/bert-arabic-phoneme/stage_3_full_sequences/final_model'
model = BertForMaskedLM.from_pretrained(model_path)

# 2. Load the tokenizer
tokenizer = UTF8PhonemeTokenizer()
tokenizer.load_vocab(f'{model_path}/vocab.json')

# 3. Prepare input with masked token
text = "مرحبا [MASK] العالم"
inputs = tokenizer.encode(text, return_tensors='pt')

# 4. Get predictions
with torch.no_grad():
    outputs = model(**inputs)
    predictions = outputs.logits

# 5. Get top predictions for masked token
masked_index = (inputs['input_ids'] == tokenizer.vocab['[MASK]']).nonzero(as_tuple=True)[1]
predicted_token_ids = predictions[0, masked_index].argmax(axis=-1)
predicted_tokens = tokenizer.decode(predicted_token_ids)

print(f"Predicted: {predicted_tokens}")
    """)


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("BERT Training Pipeline Examples")
    print("Eqratech Arabic Diana Project")
    print("="*70)
    
    try:
        # Example 1: Tokenizer
        _ = example_tokenizer_usage()
        
        # Example 2: Configuration
        _ = example_training_config()
        
        # Example 3: Training demonstration
        example_quick_training()
        
        # Example 4: Using trained model
        example_using_trained_model()
        
        # Summary
        print("\n" + "="*70)
        print("Examples Complete!")
        print("="*70)
        print("\nNext steps:")
        print("1. Test your setup:")
        print("   python test_setup.py")
        print("\n2. Run full training:")
        print("   python run_training.py --config config/training_config.json")
        print("\n3. Check the documentation:")
        print("   cat BERT_TRAINING_README.md")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
