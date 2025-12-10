# tools/export_to_onnx.py
"""
Export a Stable Diffusion model to ONNX and apply optional dynamic quantization.
Works with latest ONNX Runtime + Optimum ONNX.

Usage:
  python tools/export_to_onnx.py --model_id runwayml/stable-diffusion-v1-5 --out_dir ./onnx-sd --quantize
"""

import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_id", type=str, required=True)
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--opset", type=int, default=16)
    parser.add_argument("--quantize", action="store_true")
    args = parser.parse_args()

    model_id = args.model_id
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export to ONNX
    print("🔧 Exporting model to ONNX... This may take several minutes...")
    try:
        from optimum.onnxruntime import ORTStableDiffusionPipeline

        ORTStableDiffusionPipeline.from_pretrained(
            model_id,
            export=True,
            opset=args.opset,
            output_dir=str(out_dir),
        )
        print("✅ ONNX export completed.")
    except Exception as e:
        print("❌ Export failed:", e)
        return

    # Optional quantization
    if args.quantize:
        print("🔧 Applying dynamic quantization...")
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType

            for onnx_file in out_dir.glob("*.onnx"):
                qfile = onnx_file.parent / f"{onnx_file.stem}_quant.onnx"

                quantize_dynamic(
                    model_input=str(onnx_file),
                    model_output=str(qfile),
                    weight_type=QuantType.QInt8
                )

                print(f"  ➤ Quantized: {onnx_file.name} → {qfile.name}")

            print("✅ Quantization complete.")
        except Exception as e:
            print("❌ Quantization failed:", e)
            return

if __name__ == "__main__":
    main()
