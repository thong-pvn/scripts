#!/usr/bin/env python3
"""
Script test API generation và validation scoring
Yêu cầu: 
- Generation service chạy trên port 4000
- Validation service chạy trên port 8094 (hoặc có thể dùng validation engine trực tiếp)
"""

import requests
import time
import io
import base64
import argparse
from pathlib import Path
import sys
import os

# Thêm path để import validation modules
sys.path.append('validation')
sys.path.append('validation/engine')

import torch
import pybase64
import pyspz
from engine.data_structures import ValidationRequest, ValidationResponse, ValidationResult
from engine.validation_engine import ValidationEngine
from engine.io.ply import PlyLoader
from engine.rendering.renderer import Renderer


class GenerationTester:
    def __init__(self, generation_url="http://127.0.0.1:8000", validation_url="http://127.0.0.1:8094"):
        self.generation_url = generation_url
        self.validation_url = validation_url
        self.validation_engine = None
        self.renderer = None
        self.ply_loader = None
        
    def setup_validation_engine(self):
        """Setup validation engine giống như trong validator"""
        print("🔧 Đang setup validation engine...")
        self.validation_engine = ValidationEngine(verbose=True)
        self.validation_engine.load_pipelines()
        self.renderer = Renderer()
        self.ply_loader = PlyLoader()
        print("✅ Validation engine đã sẵn sàng!")
        
    def generate_3d_asset(self, prompt: str, save_to_file: str = None) -> bytes:
        """Gọi API generation để tạo 3D asset"""
        print(f"🎨 Đang tạo 3D asset với prompt: '{prompt}'")
        
        try:
            response = requests.post(
                f"{self.generation_url}/generate/",
                data={"prompt": prompt, "type": "ply"},
                timeout=300  # 5 minutes timeout
            )
            response.raise_for_status()
            
            ply_data = response.content
            print(f"✅ Đã tạo xong 3D asset! Kích thước: {len(ply_data)} bytes")
            
            if save_to_file:
                with open(save_to_file, 'wb') as f:
                    f.write(ply_data)
                print(f"💾 Đã lưu file PLY: {save_to_file}")
                
            return ply_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi khi gọi API generation: {e}")
            raise
            
    def validate_with_engine(self, ply_data: bytes, prompt: str) -> ValidationResult:
        """Sử dụng validation engine để chấm điểm (giống validator)"""
        print("📊 Đang validation với engine...")
        
        try:
            # Load PLY data
            pcl_buffer = io.BytesIO(ply_data)
            gs_data = self.ply_loader.from_buffer(pcl_buffer)
            
            # Render images để validation
            gs_data_gpu = gs_data.send_to_device(self.validation_engine.device)
            images = self.renderer.render_gs(gs_data_gpu, 16, 224, 224)
            
            # Validate text vs images
            validation_result = self.validation_engine.validate_text_to_gs(prompt, images)
            
            return validation_result
            
        except Exception as e:
            print(f"❌ Lỗi validation: {e}")
            raise
            
    def validate_with_api(self, ply_data: bytes, prompt: str) -> ValidationResponse:
        """Sử dụng validation API để chấm điểm"""
        print("🌐 Đang validation với API...")
        
        try:
            # Compress với SPZ
            compressed_data = pyspz.compress(ply_data, include_normals=False)
            encoded_data = pybase64.b64encode(compressed_data).decode('utf-8')
            
            request_data = ValidationRequest(
                prompt=prompt,
                data=encoded_data,
                compression=2,  # SPZ compression
                generate_preview=True,
                preview_score_threshold=0.5
            )
            
            response = requests.post(
                f"{self.validation_url}/validate_txt_to_3d_ply/",
                json=request_data.dict(),
                timeout=120
            )
            response.raise_for_status()
            
            return ValidationResponse(**response.json())
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi khi gọi validation API: {e}")
            raise
            
    def print_validation_results(self, result: ValidationResult, title="Validation Results"):
        """In kết quả validation"""
        print(f"\n📈 {title}")
        print("=" * 50)
        print(f"🎯 Final Score:           {result.final_score:.4f}")
        print(f"🎨 Quality Score:         {result.combined_quality_score:.4f}")  
        print(f"🎪 Alignment Score:       {result.alignment_score:.4f}")
        print(f"📐 SSIM Score:            {result.ssim_score:.4f}")
        print(f"👁️  LPIPS Score:           {result.lpips_score:.4f}")
        if result.validation_time:
            print(f"⏱️  Validation Time:       {result.validation_time:.2f}s")
        print("=" * 50)
        
        # Đánh giá chất lượng
        if result.final_score >= 0.8:
            print("🌟 Chất lượng: XUẤT SẮC!")
        elif result.final_score >= 0.6:
            print("👍 Chất lượng: TỐT")
        elif result.final_score >= 0.4:
            print("👌 Chất lượng: TRUNG BÌNH")
        else:
            print("👎 Chất lượng: CẦN CẢI THIỆN")
            
    def print_api_results(self, result: ValidationResponse, title="API Validation Results"):
        """In kết quả validation từ API"""
        print(f"\n📈 {title}")
        print("=" * 50)
        print(f"🎯 Final Score:           {result.score:.4f}")
        print(f"🎨 IQA Score:             {result.iqa:.4f}")  
        print(f"🎪 Alignment Score:       {result.alignment_score:.4f}")
        print(f"📐 SSIM Score:            {result.ssim:.4f}")
        print(f"👁️  LPIPS Score:           {result.lpips:.4f}")
        if result.preview:
            print(f"🖼️  Preview Image:         Available (base64)")
        print("=" * 50)
        
    def test_generation_and_validation(self, prompt: str, output_dir: str = "test_output", use_engine: bool = True, use_api: bool = False):
        """Test hoàn chỉnh generation và validation"""
        print(f"\n🚀 Bắt đầu test với prompt: '{prompt}'")
        
        # Tạo thư mục output
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Tạo tên file an toàn
        safe_filename = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')[:50]
        ply_file = output_path / f"{safe_filename}.ply"
        
        start_time = time.time()
        
        try:
            # Step 1: Generate 3D asset
            ply_data = self.generate_3d_asset(prompt, str(ply_file))
            generation_time = time.time() - start_time
            
            # Step 2: Validation với engine (giống validator)
            if use_engine:
                if self.validation_engine is None:
                    self.setup_validation_engine()
                    
                validation_start = time.time()
                engine_result = self.validate_with_engine(ply_data, prompt)
                validation_time = time.time() - validation_start
                engine_result.validation_time = validation_time
                
                self.print_validation_results(engine_result, "Engine Validation (Giống Validator)")
            
            # Step 3: Validation với API (optional)
            if use_api:
                try:
                    api_result = self.validate_with_api(ply_data, prompt)
                    self.print_api_results(api_result, "API Validation")
                except Exception as e:
                    print(f"⚠️  Validation API không khả dụng: {e}")
            
            total_time = time.time() - start_time
            
            print(f"\n⏱️  Thời gian:")
            print(f"   Generation: {generation_time:.2f}s")
            if use_engine and 'validation_time' in locals():
                print(f"   Validation: {validation_time:.2f}s")
            print(f"   Total: {total_time:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Test thất bại: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Test Generation API với Validation Scoring")
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt để tạo 3D asset")
    parser.add_argument("--generation-url", default="http://127.0.0.1:8000", help="URL của generation service")
    parser.add_argument("--validation-url", default="http://127.0.0.1:8094", help="URL của validation service")  
    parser.add_argument("--output-dir", "-o", default="test_output", help="Thư mục lưu kết quả")
    parser.add_argument("--use-api", action="store_true", help="Cũng test validation API")
    parser.add_argument("--no-engine", action="store_true", help="Không dùng validation engine")
    
    args = parser.parse_args()
    
    print("🧪 THREE GEN API TESTER")
    print("=" * 50)
    
    tester = GenerationTester(args.generation_url, args.validation_url)
    
    success = tester.test_generation_and_validation(
        prompt=args.prompt,
        output_dir=args.output_dir,
        use_engine=not args.no_engine,
        use_api=args.use_api
    )
    
    if success:
        print("\n✅ Test hoàn thành thành công!")
        return 0
    else:
        print("\n❌ Test thất bại!")
        return 1


if __name__ == "__main__":
    exit(main()) 
