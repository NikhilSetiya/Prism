"""Prism - Streamlit UI for Creative Automation Pipeline."""

import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Prism components
from src.models import CampaignBrief
from src.pipeline import CampaignPipeline
from src.utils import Config

# Import UI helpers
from ui import gallery, uploader, reports


def check_api_key():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.sidebar.success("✓ API Key Configured")
    else:
        st.sidebar.error("✗ API Key Missing")
        st.sidebar.warning("Set OPENAI_API_KEY in .env file")


def main():
    """Main Streamlit app entry point."""
    st.set_page_config(
        page_title="Prism - Creative Automation",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title
    st.title("🎨 Prism - Creative Automation Pipeline")
    st.markdown("*One hero image per product → systematic variations across formats & locales*")
    st.caption("Generate once, reuse everywhere: Hero + variants architecture for cost-efficient campaigns")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Check API key status
    check_api_key()
    
    st.sidebar.markdown("---")
    
    # Page selection
    page = st.sidebar.radio(
        "Select Page",
        ["Campaign", "Gallery", "Cache", "History"],
        label_visibility="collapsed"
    )
    
    # Route to appropriate page
    if page == "Campaign":
        campaign_page()
    elif page == "Gallery":
        gallery_page()
    elif page == "Cache":
        cache_page()
    elif page == "History":
        history_page()


def manual_campaign_form():
    """Interactive form to create campaign brief manually."""
    st.markdown("### Create Campaign Brief")
    st.markdown("Fill in the form below to create your campaign. Hover over ℹ️ for hints.")
    
    # Number of products OUTSIDE the form so it can update dynamically
    st.subheader("📦 Products Configuration")
    num_products = st.number_input(
        "Number of Products", 
        min_value=2, 
        max_value=5, 
        value=2,
        help="Select how many products to configure (2-5)"
    )
    st.caption(f"You'll configure {num_products} product(s) below")
    st.markdown("---")
    
    with st.form("manual_campaign_form"):
        # Campaign basics
        st.subheader("📋 Campaign Information")
        
        col1, col2 = st.columns(2)
        with col1:
            campaign_id = st.text_input(
                "Campaign ID*",
                value="",
                placeholder="e.g., summer_2025_launch",
                help="Filesystem-safe ID (lowercase, underscores only)"
            )
        
        with col2:
            region = st.selectbox(
                "Region*",
                ["EMEA", "NA", "APAC", "LATAM", "GLOBAL"],
                help="Target market region"
            )
        
        target_audience = st.text_input(
            "Target Audience*",
            placeholder="e.g., millennials_25-35",
            help="Primary demographic target"
        )
        
        campaign_message = st.text_input(
            "Campaign Message*",
            placeholder="e.g., Discover Summer Freshness",
            help="Main tagline or headline (5-200 characters)",
            max_chars=200
        )
        
        locales_input = st.text_input(
            "Locales*",
            value="en",
            placeholder="en, fr, de",
            help="Comma-separated language codes (e.g., en, fr, de)"
        )
        
        st.markdown("---")
        
        # Products section
        st.subheader(f"📦 Product Details ({num_products} products)")
        st.caption("Fill in details for each product")
        
        products = []
        for i in range(num_products):
            with st.expander(f"Product {i+1}", expanded=i<2):
                col1, col2 = st.columns(2)
                
                with col1:
                    prod_id = st.text_input(
                        "Product ID*",
                        key=f"prod_id_{i}",
                        placeholder="e.g., shampoo_citrus_500ml",
                        help="Filesystem-safe (lowercase, underscores)"
                    )
                    
                    prod_name = st.text_input(
                        "Product Name*",
                        key=f"prod_name_{i}",
                        placeholder="e.g., CitriFresh Shampoo",
                        help="Brand-friendly display name"
                    )
                
                with col2:
                    prod_category = st.selectbox(
                        "Category*",
                        ["haircare", "skincare", "bodycare", "cosmetics", "wellness", "other"],
                        key=f"prod_cat_{i}"
                    )
                
                prod_desc = st.text_area(
                    "Description*",
                    key=f"prod_desc_{i}",
                    placeholder="e.g., Citrus-infused cleansing shampoo with natural extracts",
                    help="Product description (10-500 characters)",
                    max_chars=500,
                    height=80
                )
                
                st.markdown("**Creative Brief**")
                
                setting = st.text_input(
                    "Setting",
                    key=f"setting_{i}",
                    value="Clean studio environment",
                    placeholder="e.g., Fresh bathroom scene with natural elements"
                )
                
                mood = st.text_input(
                    "Mood",
                    key=f"mood_{i}",
                    value="Fresh and energetic",
                    placeholder="e.g., Energetic, fresh, clean"
                )
                
                visual_elements = st.text_input(
                    "Key Visual Elements",
                    key=f"visual_{i}",
                    placeholder="Product bottle, water splash, natural light (comma-separated)",
                    help="Important elements to include (comma-separated)"
                )
                
                st.markdown("**Brand Style**")
                
                colors = st.text_input(
                    "Color Palette",
                    key=f"colors_{i}",
                    value="#FF6B35, #004E89, #FFFFFF",
                    placeholder="#FF6B35, #004E89, #FFFFFF",
                    help="2-5 brand colors in hex format (comma-separated)"
                )
                
                visual_style = st.text_input(
                    "Visual Style",
                    key=f"vstyle_{i}",
                    value="Clean and modern",
                    placeholder="e.g., Modern minimalist, Natural organic"
                )
                
                photo_style = st.text_input(
                    "Photography Style",
                    key=f"pstyle_{i}",
                    value="Commercial product photography",
                    placeholder="e.g., Commercial product photography"
                )
                
                # Store product data
                if prod_id and prod_name and prod_desc:
                    products.append({
                        "id": prod_id,
                        "name": prod_name,
                        "description": prod_desc,
                        "category": prod_category,
                        "creative_brief": {
                            "setting": setting,
                            "mood": mood,
                            "key_visual_elements": [e.strip() for e in visual_elements.split(',') if e.strip()]
                        },
                        "brand_style": {
                            "color_palette": [c.strip() for c in colors.split(',') if c.strip()],
                            "visual_style": visual_style,
                            "photography_style": photo_style
                        }
                    })
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("✅ Create Campaign Brief", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not campaign_id:
                st.error("❌ Campaign ID is required")
                return
            
            if not campaign_message:
                st.error("❌ Campaign message is required")
                return
            
            if len(products) < 2:
                st.error("❌ At least 2 products are required")
                return
            
            # Parse locales
            locales = [l.strip() for l in locales_input.split(',') if l.strip()]
            if not locales:
                st.error("❌ At least one locale is required")
                return
            
            # Build campaign brief
            brief_data = {
                "campaign_id": campaign_id,
                "region": region,
                "target_audience": target_audience,
                "campaign_message": campaign_message,
                "locales": locales,
                "products": products
            }
            
            try:
                # Validate with Pydantic
                brief = CampaignBrief(**brief_data)
                st.session_state.brief = brief
                st.session_state.brief_data = brief_data
                
                st.success(f"✅ Campaign brief created: **{campaign_id}**")
                
                # Show summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Products", len(brief.products))
                with col2:
                    st.metric("Locales", len(brief.locales))
                with col3:
                    st.metric("Region", brief.region)
                
                # Option to download as JSON
                st.markdown("---")
                json_str = json.dumps(brief_data, indent=2)
                st.download_button(
                    "💾 Download as JSON",
                    data=json_str,
                    file_name=f"{campaign_id}_brief.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"❌ Validation error: {e}")


def campaign_page():
    """Campaign execution page - upload brief, assets, and run pipeline."""
    st.header("🚀 Run Campaign")
    st.markdown("""
    **Hero + Variants Architecture:** Generate or reuse hero images for each product, then automatically create 
    aspect ratio variations (1:1, 9:16, 16:9) and localized compositions.
    """)
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        **Phase 1: Hero Images**
        - Check input folder for user-provided images
        - Check cache for previously generated heroes
        - Generate new heroes via DALL-E 3 only if needed
        
        **Phase 2: Variations** (local processing, no API cost)
        - Create aspect ratio crops: 1:1 (Instagram), 9:16 (Stories), 16:9 (YouTube)
        - Intelligent center-crop preserves subject focus
        
        **Phase 3: Composition** (local processing, no API cost)
        - Add localized text overlays
        - Apply brand logos
        - Run compliance checks
        
        **Cost Example:** 2 products × 3 aspects × 2 locales = 12 final assets
        - Hero generation: 2 × $0.08 = **$0.16**
        - Variations & composition: **$0.00** (local processing)
        - With cache: **$0.00** (all heroes reused)
        """)
    
    # Initialize session state for brief
    if 'brief' not in st.session_state:
        st.session_state.brief = None
    if 'brief_data' not in st.session_state:
        st.session_state.brief_data = None
    
    # Section 1: Upload or Create Campaign Brief
    with st.expander("📋 Campaign Brief", expanded=True):
        # Tab selection: Upload or Create
        brief_tab = st.radio(
            "Choose method",
            ["📤 Upload JSON", "✍️ Create Manually"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if brief_tab == "📤 Upload JSON":
            uploaded_brief = st.file_uploader(
                "Upload campaign brief (JSON)",
                type=['json'],
                key="brief_uploader",
                help="Upload a JSON file containing campaign configuration"
            )
            
            if uploaded_brief:
                try:
                    # Parse JSON
                    brief_data = json.load(uploaded_brief)
                    st.session_state.brief_data = brief_data
                    
                    # Validate with Pydantic
                    brief = CampaignBrief(**brief_data)
                    st.session_state.brief = brief
                    
                    st.success(f"✓ Valid brief: **{brief.campaign_id}**")
                    
                    # Show brief summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Products", len(brief.products))
                    with col2:
                        st.metric("Locales", len(brief.locales))
                    with col3:
                        st.metric("Region", brief.region)
                    
                    # Show full brief in expandable section
                    with st.expander("View Full Brief"):
                        st.json(brief_data)
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                    st.session_state.brief = None
                except Exception as e:
                    st.error(f"❌ Invalid campaign brief: {e}")
                    st.session_state.brief = None
            else:
                st.info("👆 Upload a campaign brief to get started")
        
        else:  # Create Manually
            manual_campaign_form()
    
    # Section 2: Upload Input Assets (Optional)
    with st.expander("🖼️ Input Assets (Optional)", expanded=False):
        st.markdown("""
        Upload product images to use instead of generating them.
        
        **Naming convention:**
        - `{product_id}.png` - Generic image for all aspect ratios
        - `{product_id}_{aspect_ratio}.png` - Specific to aspect ratio (e.g., `shampoo_citrus_500ml_1x1.png`)
        """)
        
        uploaded_assets = st.file_uploader(
            "Upload product images",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="asset_uploader"
        )
        
        if uploaded_assets:
            st.subheader("Uploaded Assets Preview")
            cols = st.columns(4)
            for idx, asset in enumerate(uploaded_assets):
                with cols[idx % 4]:
                    st.image(asset, caption=asset.name, use_container_width=True)
            
            # Validation warnings
            if st.session_state.brief:
                product_ids = [p.id for p in st.session_state.brief.products]
                for asset in uploaded_assets:
                    error = uploader.validate_asset_naming(asset.name, product_ids)
                    if error:
                        st.warning(f"⚠️ {error}")
        
        # Show existing assets
        existing_assets = uploader.list_existing_assets()
        if existing_assets:
            st.markdown("---")
            st.subheader("Existing Assets")
            cols = st.columns(4)
            for idx, asset_path in enumerate(existing_assets):
                with cols[idx % 4]:
                    st.image(str(asset_path), caption=asset_path.name, use_container_width=True)
                    if st.button(f"🗑️ Delete", key=f"del_{asset_path.name}"):
                        if uploader.delete_asset(asset_path):
                            st.success(f"Deleted {asset_path.name}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete {asset_path.name}")
    
    # Section 3: Execute Pipeline
    st.markdown("---")
    
    if not st.session_state.brief:
        st.warning("⚠️ Please upload a campaign brief first")
        return
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        return
    
    # Run button
    if st.button("🚀 Run Campaign", type="primary", use_container_width=True):
        # Save uploaded assets if any
        if uploaded_assets:
            with st.spinner("Saving uploaded assets..."):
                saved = uploader.save_input_assets(uploaded_assets)
                if saved:
                    st.success(f"✓ Saved {len(saved)} asset(s)")
        
        # Execute pipeline
        with st.status("Generating assets...", expanded=True) as status:
            try:
                # Load config
                st.write("📝 Loading configuration...")
                config = Config.load()
                
                # Initialize pipeline
                st.write("🔧 Initializing pipeline...")
                pipeline = CampaignPipeline(config)
                
                # Run pipeline
                st.write("🎨 Generating campaign assets...")
                report = pipeline.run(st.session_state.brief)
                
                status.update(label="✅ Campaign Complete!", state="complete")
                
                # Display report
                st.markdown("---")
                reports.display_execution_report(report)
                
                # Success message with link to gallery
                st.success("🎉 Campaign generated successfully!")
                if st.button("🖼️ View Assets in Gallery"):
                    st.session_state.page = "Gallery"
                    st.rerun()
                
            except Exception as e:
                status.update(label="❌ Campaign Failed", state="error")
                st.error(f"Error: {e}")
                
                # Show traceback in expandable
                import traceback
                with st.expander("🐛 Error Details"):
                    st.code(traceback.format_exc())


def gallery_page():
    """Asset gallery page - view and download generated assets."""
    st.header("🖼️ Asset Gallery")
    st.markdown("Browse and download generated campaign assets.")
    
    # Get all campaigns
    campaigns = gallery.list_campaigns()
    
    if not campaigns:
        st.info("📭 No campaigns found. Run a campaign first to see assets here.")
        return
    
    # Campaign selector
    selected_campaign = st.selectbox(
        "Select Campaign",
        campaigns,
        key="gallery_campaign_selector"
    )
    
    if not selected_campaign:
        return
    
    # Load assets for selected campaign
    assets_by_product = gallery.load_campaign_assets(selected_campaign)
    
    if not assets_by_product:
        st.warning(f"No assets found for campaign: {selected_campaign}")
        return
    
    # Bulk download button
    col1, col2 = st.columns([3, 1])
    with col2:
        zip_buffer = gallery.create_campaign_zip(selected_campaign)
        st.download_button(
            "📦 Download All (ZIP)",
            data=zip_buffer,
            file_name=f"{selected_campaign}_assets.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Display assets by product
    for product_id, assets in assets_by_product.items():
        with st.expander(f"📦 {product_id}", expanded=True):
            if not assets:
                st.info("No assets found for this product")
                continue
            
            # Get aspect ratios and locales from assets
            aspect_ratios = gallery.get_aspect_ratios_from_assets(assets)
            locales = gallery.get_locales_from_assets(assets)
            
            # Create grid: columns for aspect ratios
            if aspect_ratios:
                cols = st.columns(len(aspect_ratios))
                
                for col_idx, ratio in enumerate(aspect_ratios):
                    with cols[col_idx]:
                        st.subheader(ratio.replace('x', ':'))
                        
                        # Show assets for each locale in this aspect ratio
                        for locale in locales:
                            # Find matching asset
                            matching_assets = [
                                a for a in assets
                                if gallery.get_asset_info(a) == (ratio, locale)
                            ]
                            
                            if matching_assets:
                                asset_path = matching_assets[0]
                                
                                # Display image
                                st.image(
                                    str(asset_path),
                                    caption=f"{locale.upper()}",
                                    use_container_width=True
                                )
                                
                                # Download button
                                with open(asset_path, 'rb') as f:
                                    st.download_button(
                                        f"⬇️ Download {locale.upper()}",
                                        data=f.read(),
                                        file_name=asset_path.name,
                                        mime="image/png",
                                        key=f"dl_{product_id}_{ratio}_{locale}",
                                        use_container_width=True
                                    )
    
    st.markdown("---")
    st.caption(f"Showing assets from: `output/{selected_campaign}/`")


def cache_page():
    """Cache management page - view stats and clear cache."""
    st.header("💾 Cache Management")
    st.markdown("View cache statistics and manage cached assets.")
    
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    
    cache_files = list(cache_dir.glob("*.png"))
    
    # Statistics
    st.subheader("📈 Cache Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cached Assets", len(cache_files))
    
    with col2:
        if cache_files:
            size_mb = sum(f.stat().st_size for f in cache_files) / 1024 / 1024
            st.metric("Cache Size", f"{size_mb:.1f} MB")
        else:
            st.metric("Cache Size", "0 MB")
    
    with col3:
        avg_hit_rate = reports.calculate_avg_cache_hit_rate()
        st.metric("Avg Hit Rate", f"{avg_hit_rate:.0f}%")
    
    st.markdown("---")
    
    # Cache contents
    if cache_files:
        with st.expander("📋 View Cache Contents", expanded=False):
            import pandas as pd
            from datetime import datetime
            
            cache_data = []
            for f in sorted(cache_files, key=lambda x: x.stat().st_mtime, reverse=True):
                cache_data.append({
                    "File": f.name,
                    "Size": f"{f.stat().st_size / 1024:.1f} KB",
                    "Modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            df = pd.DataFrame(cache_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("🗂️ Cache is empty")
    
    # Actions
    st.markdown("---")
    st.subheader("🧹 Cache Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Clear All Cache**")
        st.caption("Delete all cached assets to free up space")
        
        if st.button("🗑️ Clear All Cache", type="secondary", use_container_width=True, disabled=len(cache_files) == 0):
            with st.form("confirm_clear_all"):
                st.warning(f"⚠️ This will delete {len(cache_files)} cached assets")
                confirm = st.checkbox("I understand this action cannot be undone")
                
                if st.form_submit_button("Confirm Delete", type="primary"):
                    if confirm:
                        deleted_count = 0
                        for f in cache_files:
                            try:
                                f.unlink()
                                deleted_count += 1
                            except Exception:
                                pass
                        
                        st.success(f"✓ Deleted {deleted_count} cached assets")
                        st.rerun()
                    else:
                        st.error("Please check the confirmation box")
    
    with col2:
        st.markdown("**Clear Old Cache**")
        st.caption("Delete cache older than 30 days")
        
        import time
        old_files = [
            f for f in cache_files
            if (time.time() - f.stat().st_mtime) > 30 * 24 * 3600
        ]
        
        if st.button(
            f"🧹 Clear Old Cache ({len(old_files)} files)",
            type="secondary",
            use_container_width=True,
            disabled=len(old_files) == 0
        ):
            deleted_count = 0
            for f in old_files:
                try:
                    f.unlink()
                    deleted_count += 1
                except Exception:
                    pass
            
            st.success(f"✓ Deleted {deleted_count} old cached assets")
            st.rerun()
    
    # Cache explanation
    st.markdown("---")
    with st.expander("ℹ️ How Caching Works"):
        st.markdown("""
        **Prism caches generated assets to reduce costs and improve performance:**
        
        - When generating heroes, Prism checks if a similar hero was created before
        - Cache key is based on: product ID, campaign message, and region
        - If found in cache, reuses the hero instead of generating a new one
        - Hero cache rate shows how often heroes are reused
        
        **Benefits:**
        - 💰 **Cost efficient**: Reuse heroes across campaigns
        - ⚡ **Faster execution**: Cached heroes load instantly
        - 🌍 **Consistency**: Same inputs produce same outputs
        
        **When to clear cache:**
        - Running low on disk space
        - Want to regenerate assets with updated prompts
        - Cache files are corrupted
        """)
    


def history_page():
    """Execution history page - view past campaigns and reports."""
    st.header("📊 Execution History")
    st.markdown("View execution reports and performance metrics for past campaigns.")
    
    # Load all reports
    all_reports = reports.load_all_reports()
    
    if not all_reports:
        st.info("📭 No execution history yet. Run a campaign to see reports here.")
        return
    
    # Summary statistics
    st.subheader("📈 Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Campaigns", len(all_reports))
    
    with col2:
        # Calculate total assets from compliance summaries
        total_assets = sum(r.get('compliance_summary', {}).get('total_assets', 0) for r in all_reports)
        st.metric("Total Assets", total_assets)
    
    with col3:
        total_cost = sum(r['total_cost'] for r in all_reports)
        st.metric("Total Cost", f"${total_cost:.2f}")
    
    with col4:
        avg_cache = sum(r.get('cache_efficiency', 0) for r in all_reports) / len(all_reports)
        st.metric("Avg Cache Hit", f"{avg_cache:.0f}%")
    
    st.markdown("---")
    
    # Campaign list as table
    st.subheader("📋 Campaign Reports")
    
    import pandas as pd
    from datetime import datetime
    
    table_data = []
    for r in sorted(all_reports, key=lambda x: x['timestamp'], reverse=True):
        # Calculate totals from hero tracking
        heroes_gen = r.get('hero_images_generated', 0)
        heroes_cached = r.get('hero_images_cached', 0)
        total_assets = r.get('compliance_summary', {}).get('total_assets', 0)
        
        table_data.append({
            "Campaign": r['campaign_id'],
            "Date": datetime.fromtimestamp(r['timestamp']).strftime("%Y-%m-%d %H:%M"),
            "Products": r['products_count'],
            "Assets": total_assets,
            "Heroes Gen": heroes_gen,
            "Heroes Cached": heroes_cached,
            "Cost": f"${r['total_cost']:.2f}",
            "Time": f"{r['execution_time']:.1f}s"
        })
    
    df = pd.DataFrame(table_data)
    
    # Display table with highlighting
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Campaign": st.column_config.TextColumn("Campaign", width="medium"),
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Cost": st.column_config.TextColumn("Cost", width="small"),
            "Time": st.column_config.TextColumn("Time", width="small")
        }
    )
    
    st.markdown("---")
    
    # Report details selector
    st.subheader("🔍 Campaign Details")
    
    campaign_ids = [r['campaign_id'] for r in sorted(all_reports, key=lambda x: x['timestamp'], reverse=True)]
    selected = st.selectbox("Select campaign to view details", campaign_ids, key="history_detail_selector")
    
    if selected:
        # Find the report
        report = next((r for r in all_reports if r['campaign_id'] == selected), None)
        
        if report:
            reports.display_report_details(report)
    
    # Comparison section
    st.markdown("---")
    st.subheader("📊 Compare Campaigns")
    
    if len(all_reports) >= 2:
        selected_campaigns = st.multiselect(
            "Select campaigns to compare (up to 5)",
            campaign_ids,
            max_selections=5,
            key="history_compare"
        )
        
        if len(selected_campaigns) >= 2:
            # Create comparison table
            comparison_data = []
            for campaign_id in selected_campaigns:
                r = next((r for r in all_reports if r['campaign_id'] == campaign_id), None)
                if r:
                    total_heroes = r.get('hero_images_generated', 0) + r.get('hero_images_cached', 0)
                    hero_cache_rate = (r.get('hero_images_cached', 0) / total_heroes * 100) if total_heroes > 0 else 0
                    
                    comparison_data.append({
                        "Campaign": campaign_id,
                        "Products": r['products_count'],
                        "Assets": r.get('compliance_summary', {}).get('total_assets', 0),
                        "Heroes": total_heroes,
                        "Cost": r['total_cost'],
                        "Time (s)": r['execution_time'],
                        "Hero Cache %": hero_cache_rate
                    })
            
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                
                # Show comparison table
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
                
                # Show comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Cost Comparison**")
                    st.bar_chart(comp_df.set_index('Campaign')['Cost'])
                
                with col2:
                    st.markdown("**Hero Cache Efficiency**")
                    st.bar_chart(comp_df.set_index('Campaign')['Hero Cache %'])
        else:
            st.info("Select at least 2 campaigns to compare")
    else:
        st.info("Need at least 2 campaigns to enable comparison")


if __name__ == "__main__":
    main()

