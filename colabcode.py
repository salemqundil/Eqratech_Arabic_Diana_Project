# ✅ Colab-ready: PyTorch + CUDA check
import platform

try:
    import torch
except ImportError:
    print("PyTorch is not installed. Run: pip install torch")
    raise SystemExit(1)

print(f"Python:  {platform.python_version()}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    # List GPUs (will work in Colab GPU runtimes)
    try:
        import subprocess
        print(subprocess.check_output(["nvidia-smi", "-L"], text=True).strip())
    except Exception:
        pass

    device = torch.device("cuda")
    # quick smoke test on GPU
    x = torch.randn(3, 3, device=device)
    print("Tensor device:", x.device)
else:
    device = torch.device("cpu")
    x = torch.randn(3, 3, device=device)
    print("Tensor device:", x.device)
