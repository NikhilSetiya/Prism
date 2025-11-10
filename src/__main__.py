"""CLI entry point for Prism pipeline."""

import argparse
import sys
import json
from pathlib import Path

from src.models import CampaignBrief, ExecutionReport
from src.pipeline import CampaignPipeline
from src.utils import Config, load_json


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prism - Creative Automation Pipeline for Social Campaigns"
    )
    parser.add_argument(
        '--campaign',
        type=str,
        required=True,
        help='Path to campaign brief JSON file'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration YAML file (default: config.yaml)'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear cache before running campaign'
    )
    parser.add_argument(
        '--verify-cache',
        action='store_true',
        help='Run campaign twice to verify cache functionality'
    )
    
    args = parser.parse_args()
    
    try:
        # Clear cache if requested
        if args.clear_cache:
            import shutil
            cache_path = Path('./cache')
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print("Cache cleared.")
            cache_path.mkdir(exist_ok=True)
        
        # Load configuration
        print(f"Loading configuration from {args.config}...")
        config = Config.load(args.config)
        
        # Load campaign brief
        print(f"Loading campaign brief from {args.campaign}...")
        brief_data = load_json(args.campaign)
        brief = CampaignBrief(**brief_data)
        
        print(f"\nPrism Campaign Pipeline")
        print(f"Campaign: {brief.campaign_id}")
        print(f"Region: {brief.region}")
        print(f"Products: {len(brief.products)}")
        print(f"Locales: {', '.join(brief.locales)}")
        print(f"\nProcessing campaign...\n")
        
        # Initialize pipeline
        pipeline = CampaignPipeline(config)
        
        # Run pipeline (possibly twice for cache verification)
        runs = 2 if args.verify_cache else 1
        for run in range(runs):
            if runs > 1:
                print(f"\n{'='*50}")
                print(f"Run {run + 1} of {runs}")
                print(f"{'='*50}\n")
            
            report = pipeline.run(brief)
            
            # Display results after each run
            _display_report(report, run + 1 if runs > 1 else None)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in campaign brief - {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: Validation error - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def _display_report(report: ExecutionReport, run_number=None):
    """Display execution report."""
    header = "Campaign Execution Complete"
    if run_number:
        header = f"Run {run_number} Complete"
    
    print("\n" + "="*50)
    print(header)
    print("="*50)
    print(f"Campaign ID: {report.campaign_id}")
    print(f"Products processed: {report.products_count}")
    print(f"Assets generated: {report.assets_generated}")
    print(f"Assets reused: {report.assets_reused}")
    print(f"Total cost: ${report.total_cost:.2f}")
    print(f"Execution time: {report.execution_time:.2f}s")
    print(f"Cache efficiency: {report.cache_efficiency:.1f}%")
    print(f"Worker count: {report.worker_count}")
    print(f"Output path: {report.output_path}")
    
    if report.compliance_summary:
        comp = report.compliance_summary
        print(f"\nCompliance Summary:")
        print(f"  Total assets: {comp.get('total_assets', 0)}")
        print(f"  Passed: {comp.get('passed', 0)}")
        print(f"  Warnings: {comp.get('warnings', 0)}")
        print(f"  Errors: {comp.get('errors', 0)}")
    
    if report.errors:
        print(f"\nWarnings/Errors: {len(report.errors)}")
        for error in report.errors[:5]:
            print(f"  - {error}")
    
    print("\n" + "="*50)
    if not run_number:
        print("Campaign processing completed successfully!")


if __name__ == "__main__":
    sys.exit(main())

