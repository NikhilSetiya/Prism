"""Report display and formatting functions."""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import streamlit as st


def display_execution_report(report) -> None:
    """Display execution report with metrics in nice format."""
    st.subheader("📊 Execution Report")
    
    # Main metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products", report.products_count)
    with col2:
        # Calculate total final assets from compliance summary if available
        if hasattr(report, 'compliance_summary') and report.compliance_summary:
            total_assets = report.compliance_summary.get('total_assets', 0)
        else:
            # Fallback: calculate from hero tracking
            total_assets = getattr(report, 'variations_created', 0) * 2  # variations × locales
        st.metric("Total Assets", total_assets)
    with col3:
        st.metric("Cost", f"${report.total_cost:.2f}")
    with col4:
        st.metric("Time", f"{report.execution_time:.1f}s")
    
    # Hero + Variations tracking
    st.markdown("### 🎨 Generation Breakdown")
    col5, col6, col7 = st.columns(3)
    with col5:
        heroes_gen = getattr(report, 'hero_images_generated', 0)
        st.metric("Heroes Generated", heroes_gen, help="New hero images created via DALL-E")
    with col6:
        heroes_cached = getattr(report, 'hero_images_cached', 0)
        st.metric("Heroes Cached", heroes_cached, help="Hero images reused from cache")
    with col7:
        variations = getattr(report, 'variations_created', 0)
        st.metric("Variations Created", variations, help="Aspect ratio variations from heroes")
    
    # Efficiency insight
    total_heroes = heroes_gen + heroes_cached
    if total_heroes > 0:
        cache_rate = (heroes_cached / total_heroes) * 100
        if cache_rate > 50:
            st.success(f"💰 Cost efficient! {cache_rate:.0f}% of heroes reused from cache")
        elif cache_rate > 0:
            st.info(f"📊 {cache_rate:.0f}% of heroes reused from cache")
    
    # Output path
    st.info(f"📁 Assets saved to: `{report.output_path}`")
    
    # Errors if any
    if hasattr(report, 'errors') and report.errors:
        with st.expander(f"⚠️ Warnings/Errors ({len(report.errors)})", expanded=True):
            for error in report.errors:
                st.warning(error)


def display_report_details(report: Dict[str, Any]) -> None:
    """Display detailed report view."""
    st.subheader(f"📋 {report['campaign_id']}")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Products", report['products_count'])
    with col2:
        # Get total assets from compliance summary
        total = report.get('compliance_summary', {}).get('total_assets', 0)
        st.metric("Assets", total)
    with col3:
        st.metric("Cost", f"${report['total_cost']:.2f}")
    with col4:
        st.metric("Time", f"{report['execution_time']:.1f}s")
    
    # Hero tracking
    col5, col6, col7 = st.columns(3)
    with col5:
        heroes_gen = report.get('hero_images_generated', 0)
        st.metric("Heroes Generated", heroes_gen)
    with col6:
        heroes_cached = report.get('hero_images_cached', 0)
        st.metric("Heroes Cached", heroes_cached)
    with col7:
        variations = report.get('variations_created', 0)
        st.metric("Variations", variations)
    
    # Timing breakdown
    if 'timings' in report and report['timings']:
        with st.expander("⏱️ Timing Breakdown"):
            timings = report['timings']
            if 'total' in timings:
                st.write(f"**Total:** {timings['total']:.2f}s")
            # Show other timings
            other_timings = {k: v for k, v in timings.items() if k != 'total'}
            if other_timings:
                for operation, duration in sorted(other_timings.items()):
                    if isinstance(duration, dict):
                        st.write(f"**{operation}:**")
                        for sub_op, sub_duration in duration.items():
                            st.write(f"  - {sub_op}: {sub_duration:.2f}s")
                    else:
                        st.write(f"- {operation}: {duration:.2f}s")
    
    # Errors
    if 'errors' in report and report['errors']:
        with st.expander(f"⚠️ Errors ({len(report['errors'])})", expanded=True):
            for error in report['errors']:
                st.error(error)
    
    # Link to gallery
    if st.button("🖼️ View Assets in Gallery", key=f"view_{report['campaign_id']}"):
        st.session_state.selected_campaign = report['campaign_id']
        st.session_state.page = "Gallery"
        st.rerun()


def calculate_avg_cache_hit_rate() -> float:
    """Calculate average cache hit rate across all execution reports."""
    log_dir = Path("logs")
    if not log_dir.exists():
        return 0.0
    
    rates = []
    for log_file in log_dir.glob("*_execution.json"):
        try:
            with open(log_file) as f:
                report = json.load(f)
                if 'cache_efficiency' in report:
                    rates.append(report['cache_efficiency'])
        except Exception:
            continue
    
    return sum(rates) / len(rates) if rates else 0.0


def load_all_reports() -> List[Dict[str, Any]]:
    """Load all execution reports from logs directory."""
    log_dir = Path("logs")
    if not log_dir.exists():
        return []
    
    reports = []
    for log_file in log_dir.glob("*_execution.json"):
        try:
            with open(log_file) as f:
                report = json.load(f)
                report['timestamp'] = log_file.stat().st_mtime
                report['log_file'] = str(log_file)
                reports.append(report)
        except Exception:
            continue
    
    return reports


def format_report_timestamp(timestamp: float) -> str:
    """Format timestamp as readable date string."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

