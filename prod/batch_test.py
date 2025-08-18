#!/usr/bin/env python3
"""
Script test batch nhiều prompts cùng lúc
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Import test script
from test_generation_api import GenerationTester

DEFAULT_PROMPTS = [
    "robot with multi-colored neon stripes",
    "dark brown hockey stick with black tape",
    "streamlined red turbine base",
    "metallic griffin holding golden treasure chest tightly",
    "yellow textured triangular pencil holder",
    "teal fabric scissors with curved blades",
    "jagged obsidian rock darkly reflecting light",
    "glossy white compact robot model",
    "tall white vase with fresh flowers in it",
    "shiny white crystal with iridescent colors"
    "pink heart-shaped toadstool in woods",
    "iridescent gold griffin standing proud",
    "platinum earring sparkles faintly",
    "vintage doll with curly hair twirling around",
    "glossy purple grape bunch on stem",
    "jade bangle with mother of pearl inlay",
    "sleek carbon fiber black race car",
    "smooth white frothy milk pitcher",
    "sleek violet mermaid in starlight gown",
    "tiny square white and black opal bracelet",
    "gold chisel with chips in it",
    "clear cylindrical citrine with sunny yellow shade",
    "navy blue soccer cleats studs",
    "green four-eyed robot holding tool",
    "spaceship carries booster rockets",
    "sophisticated pearl tiara with subtle curves",
    "onyx flat broadsword",
    "gold-plated action figure with dynamic pose",
    "robot with white square body and blue round head",
    "glossy emerald obelisk-shaped gem",
    "sleek black robot beside plant pot",
    "smooth green pear perched atop white napkin",
    "vintage steel drum adorned with tropical designs",
    "white cotton ball nestled in wooden bowl",
    "long bench made of metal",
    "small curved wooden tool",
    "large yellow diamond with chip in it",
    "multi-colored beads on leather string",
    "purple frisbee aerodynamic and disc-shaped",
    "purple synthetic track shoe",
    "matte-black humanoid robot standing in pose of contemplation",
    "pinecone on blue spruce branch",
    "tiny wand wrapped in velvet ribbon",
    "minimalist clear plastic protractor",
    "red vanity mirror",
    "glossy yellow fruit bowl deep rimmed",
    "opal necklace with sun shape",
    "blue monkey with yellow face",
    "elegant pearl pendant on dainty chain",
    "warm brown mug of hot chocolate",
    "wizards cloak with golden trim",
    "metallic green bow with polished wood limbs",
    "prismatic violet tourmaline glows",
    "sniper rifle custom scope with infrared capabilities",
    "gray squirrel running briskly",
    "beige robot holding wrench",
    "giant red centaur holding shield",
    "dagger with ivory handle and golden tip",
    "powerful purple hippogriff in fierce battle stance",
    "vibrant blue feathered phoenix wings spread standing proud on marble pedestal",
    "metallic cylinder with rounded edges",
    "metal carving tool set",
    "elegant gold ring featuring sapphire centerpiece",
    "lustrous white opal shard",
    "mortar tube loaded ready for launch",
    "compact green bamboo cabinet",
    "donut with flames",
    "clay pot with rim chips",
    "colorful macaron set on silver tray",
    "silvery-white robot embodying modern simplicity",
    "colorful kaleidoscope-shaped glass ornament",
    "artillery piece in sandbags",
    "translucent hexagonal quartz piece in pale yellow tone",
    "tall purple plastic spaceship",
    "smooth brown obsidian bracelet",
    "azure yellow mushroom",
    "table tennis paddle with red surface",
    "smooth purple robot adorned with golden symbols",
    "iridescent purple crystal pointed tip",
    "ornamental ivory horned helmet",
    "purple felt puzzle piece",
    "grey lamp with pink stripes",
    "blue earring with leaf-shaped stone",
    "heart-shaped pendant in gold",
    "opal brooch with alligator clip closure",
    "greek bowl painted with red and black figures",
    "brown dagger with ebony tip",
    "glossy blue baseball bat with engraved logo",
    "stone elephant tusks curved in tranquil pose",
    "robot wearing red sphere",
    "platinum bullet casing",
    "tiny robot in pink overalls",
    "large wooden shelf with candles and tea lights",
    "black goblet with runes",
    "gold choker with heart-shaped pendant",
    "polished titanium fishing hook",
    "lavender-hued cupcake with swirl pattern",
    "green robot in star pose",
    "pear-shaped milky opal with iridescent glow",
    "turquoise android robot with expressive face",
    "cup brimming with frothy minty mojito",
    "high-tech explorer ship equipped with scanning lasers",
    "glossy emerald gemstone carved into oval shape",
    "pleated khaki pants wide leg fit",
    "model airplane red and white striped",
    "measuring tape coiled",
    "lustered gold topaz prism",
    "wide and tall wooden table with two chairs on either side of it",
    "jet-black robot with smooth surfaces",
    "gold band with star pattern",
    "dull grey rusty scimitar with jagged edge",
    "glossy gold cylindrical bot balanced on its side",
    "silver tongs on countertop",
    "yellow cylindrical shield",
    "metallic droid featuring polished gold finish",
    "orange peeler placed beside bowl",
    "cyan hovercraft with inflatable pontoons and canopy",
    "white oven mitt hanging from handle",
    "silk gloves white soft touch",
    "sapphire shell encasing golden cyborg heart",
    "silvery white trapezoidal robot",
    "blue dragon with grey horns",
    "plastic bucket holding gardening tools",
    "opal ring featuring swirling pattern",
    "purple orb embedded with stars",
    "tall vase with long stem and wide base",
    "phoenician amphora painted with seafaring scenes",
    "goblin wielding rusted curved sword",
    "goblin with mischievous grin red cap",
    "sleek curved knife in black",
    "polished scissors in metal stand",
    "elegant volleyball uniform style",
    "modern glass vase holding single white lily bloom",
    "statue of lion made of ceramic",
    "gold-plated robot with octagonal head",
    "turquoise spherical drone robot",
    "wooden saw with sharp blade and handle for gripping",
    "futuristic black shuttle with transparent cockpit windows",
    "sturdy dahlia flower with petals in gradient hues",
    "standing angel in gold and white",
    "roman amphora wide mouthed",
    "heavy-duty leatherwork awl",
    "mortar launcher in trench",
    "tiny gold-plated reclining mermaid statue",
    "green emerald that sparkles in sunlight",
    "gleaming sapphire hexagon perched on silver platter",
    "pink box of chocolates with strawberries and raspberries",
    "small wooden stool with blue cushion and white flowers",
    "flat-bladed rectangular shovel face",
    "green tea bag in cup steeping liquid"
]

def run_batch_test(prompts, output_dir="batch_results", use_engine=True, use_api=False):
    """Chạy test batch cho nhiều prompts"""
    
    print("🎪 BATCH TEST - THREE GEN API")
    print("=" * 50)
    print(f"📝 Số prompts: {len(prompts)}")
    print(f"📁 Output dir: {output_dir}")
    print(f"🔧 Use validation engine: {use_engine}")
    print(f"🌐 Use validation API: {use_api}")
    print("=" * 50)
    
    # Tạo output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize tester
    tester = GenerationTester()
    if use_engine:
        tester.setup_validation_engine()
    
    # Results tracking
    results = []
    total_start = time.time()
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🔄 [{i}/{len(prompts)}] Testing: '{prompt}'")
        print("-" * 40)
        
        # Retry logic cho mỗi prompt
        max_retries = 10
        min_retries = 3
        best_score = 0.0
        best_ply_data = None
        best_validation_result = None
        best_generation_time = 0.0
        
        for retry_attempt in range(max_retries):
            if retry_attempt > 0:
                print(f"🔄 Retry attempt {retry_attempt + 1}/{max_retries} cho prompt '{prompt}'")
            
            try:
                start_time = time.time()
                
                # Generate
                ply_data = tester.generate_3d_asset(prompt)
                generation_time = time.time() - start_time
                
                # Validate với engine hoặc API
                validation_result = None
                if use_engine and tester.validation_engine:
                    validation_start = time.time()
                    validation_result = tester.validate_with_engine(ply_data, prompt)
                    validation_time = time.time() - validation_start
                    validation_result.validation_time = validation_time
                    
                    tester.print_validation_results(validation_result, f"Result [{i}/{len(prompts)}] - Attempt {retry_attempt + 1}")
                elif use_api:
                    try:
                        validation_start = time.time()
                        api_result = tester.validate_with_api(ply_data, prompt)
                        validation_time = time.time() - validation_start
                        
                        # Convert API result to engine result format để tương thích
                        validation_result = type('ValidationResult', (), {
                            'final_score': api_result.score,
                            'combined_quality_score': api_result.iqa,
                            'alignment_score': api_result.alignment_score,
                            'ssim_score': api_result.ssim,
                            'lpips_score': api_result.lpips,
                            'validation_time': validation_time
                        })()
                        
                        tester.print_validation_results(validation_result, f"API Result [{i}/{len(prompts)}] - Attempt {retry_attempt + 1}")
                    except Exception as e:
                        print(f"⚠️  Validation API thất bại: {e}")
                
                # Kiểm tra score và quyết định có retry hay không
                current_score = validation_result.final_score if validation_result else 0.0
                
                # Cập nhật best result nếu score cao hơn
                if current_score >= best_score:
                    best_score = current_score
                    best_ply_data = ply_data
                    best_validation_result = validation_result
                    best_generation_time = generation_time
                    print(f"🎯 Cập nhật best score: {best_score:.4f}")
                
                # Nếu score >= 0.6, dừng retry
                if( best_score >= 0.6 and retry_attempt >= min_retries ):
                    print(f"✅ Score đạt yêu cầu ({current_score:.4f} >= 0.6), dừng retry")
                    break
                else:
                    print(f"⚠️  Score thấp ({current_score:.4f} < 0.6), sẽ retry...")
                    
            except Exception as e:
                print(f"❌ Error với prompt '{prompt}' - Attempt {retry_attempt + 1}: {e}")
                if retry_attempt == max_retries - 1:
                    # Lần cuối cùng thất bại, lưu error
                    results.append({
                        "prompt": prompt,
                        "index": i,
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error": str(e),
                        "retry_attempts": retry_attempt + 1
                    })
                    break
                continue
        
        # Lưu kết quả tốt nhất (nếu có)
        if best_ply_data is not None:
            # Save result data
            result_data = {
                "prompt": prompt,
                "index": i,
                "generation_time": best_generation_time,
                "ply_size": len(best_ply_data),
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "retry_attempts": retry_attempt + 1 if 'retry_attempt' in locals() else 1,
                "best_score": best_score
            }
            
            if best_validation_result:
                result_data.update({
                    "final_score": best_validation_result.final_score,
                    "quality_score": best_validation_result.combined_quality_score,
                    "alignment_score": best_validation_result.alignment_score,
                    "ssim_score": best_validation_result.ssim_score,
                    "lpips_score": best_validation_result.lpips_score,
                    "validation_time": best_validation_result.validation_time
                })
            
            results.append(result_data)
            
            # Save PLY file với kết quả tốt nhất
            safe_filename = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_filename = safe_filename.replace(' ', '_')[:50]
            ply_file = output_path / f"{i:02d}_{safe_filename}.ply"
            
            with open(ply_file, 'wb') as f:
                f.write(best_ply_data)
                
            print(f"💾 Saved: {ply_file} (Best score: {best_score:.4f})")
        else:
            print(f"❌ Không thể tạo 3D asset cho prompt '{prompt}' sau {max_retries} attempts")
    
    total_time = time.time() - total_start
    
    # Save batch results
    batch_report = {
        "total_prompts": len(prompts),
        "successful": len([r for r in results if r.get("success", False)]),
        "failed": len([r for r in results if not r.get("success", False)]),
        "total_time": total_time,
        "average_time_per_prompt": total_time / len(prompts),
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    # Save JSON report
    report_file = output_path / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(batch_report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print_batch_summary(batch_report, report_file)
    
    return batch_report

def print_batch_summary(report, report_file):
    """In summary kết quả batch test"""
    
    print("\n" + "=" * 60)
    print("📊 BATCH TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Successful: {report['successful']}/{report['total_prompts']}")
    print(f"❌ Failed: {report['failed']}/{report['total_prompts']}")
    print(f"⏱️  Total time: {report['total_time']:.1f}s")
    print(f"⏱️  Average per prompt: {report['average_time_per_prompt']:.1f}s")
    
    # Validation statistics
    valid_results = [r for r in report['results'] if r.get('success') and 'final_score' in r]
    if valid_results:
        scores = [r['final_score'] for r in valid_results]
        quality_scores = [r['quality_score'] for r in valid_results]
        alignment_scores = [r['alignment_score'] for r in valid_results]
        
        print(f"\n🎯 VALIDATION SCORES:")
        print(f"   Final Score: {min(scores):.3f} - {max(scores):.3f} (avg: {sum(scores)/len(scores):.3f})")
        print(f"   Quality: {min(quality_scores):.3f} - {max(quality_scores):.3f} (avg: {sum(quality_scores)/len(quality_scores):.3f})")
        print(f"   Alignment: {min(alignment_scores):.3f} - {max(alignment_scores):.3f} (avg: {sum(alignment_scores)/len(alignment_scores):.3f})")
        
        # Quality distribution
        excellent = len([s for s in scores if s >= 0.8])
        good = len([s for s in scores if 0.6 <= s < 0.8])
        average = len([s for s in scores if 0.4 <= s < 0.6])
        poor = len([s for s in scores if s < 0.4])
        
        print(f"\n🏆 QUALITY DISTRIBUTION:")
        print(f"   🌟 Excellent (≥0.8): {excellent}")
        print(f"   👍 Good (0.6-0.8): {good}")
        print(f"   👌 Average (0.4-0.6): {average}")  
        print(f"   👎 Poor (<0.4): {poor}")
    
    print(f"\n📁 Report saved: {report_file}")
    print("=" * 60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch test Generation API")
    parser.add_argument("--prompts-file", "-f", help="File chứa danh sách prompts (mỗi dòng 1 prompt)")
    parser.add_argument("--output-dir", "-o", default="batch_results", help="Thư mục output")
    parser.add_argument("--no-engine", action="store_true", help="Không dùng validation engine")
    parser.add_argument("--use-api", action="store_true", help="Dùng validation API thay vì engine")
    parser.add_argument("--count", "-c", type=int, help="Số prompts từ default list (nếu không có file)")
    
    args = parser.parse_args()
    
    # Load prompts
    if args.prompts_file:
        try:
            with open(args.prompts_file, 'r', encoding='utf-8') as f:
                prompts = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ File không tìm thấy: {args.prompts_file}")
            return 1
    else:
        count = args.count if args.count else len(DEFAULT_PROMPTS)
        prompts = DEFAULT_PROMPTS[:count]
    
    if not prompts:
        print("❌ Không có prompts để test!")
        return 1
    
    try:
        report = run_batch_test(
            prompts=prompts,
            output_dir=args.output_dir,
            use_engine=not args.no_engine,
            use_api=args.use_api
        )
        
        if report['successful'] > 0:
            print("\n✅ Batch test hoàn thành!")
            return 0
        else:
            print("\n❌ Tất cả prompts đều thất bại!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Batch test bị ngắt bởi user")
        return 1
    except Exception as e:
        print(f"\n❌ Batch test thất bại: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 
