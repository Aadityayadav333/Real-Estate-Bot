import streamlit as st
import pandas as pd
import re
import altair as alt
from crew_optimized import run_property_investment_analysis
import time
import hashlib
import sys
from io import StringIO

st.set_page_config(
    page_title="🏙️ Property Investment Research Assistant",
    layout="wide",
)

st.title("🏙️ Retail Property Investment Analyzer")
st.markdown("Analyze **retail property investment opportunities** in any city using real market data.")
st.info("⚠️ Optimized with caching. Results cached for 1 hour to save API calls.")

# Initialize session state for caching
if 'cache' not in st.session_state:
    st.session_state.cache = {}
if 'cache_time' not in st.session_state:
    st.session_state.cache_time = {}

CACHE_DURATION = 3600  # 1 hour in seconds

def get_cache_key(city_name):
    """Generate cache key for city."""
    return hashlib.md5(city_name.lower().strip().encode()).hexdigest()

def get_cached_result(city_name):
    """Get cached result if available and not expired."""
    cache_key = get_cache_key(city_name)
    if cache_key in st.session_state.cache:
        cache_age = time.time() - st.session_state.cache_time.get(cache_key, 0)
        if cache_age < CACHE_DURATION:
            return st.session_state.cache[cache_key]
    return None

def set_cached_result(city_name, result):
    """Cache result for city."""
    cache_key = get_cache_key(city_name)
    st.session_state.cache[cache_key] = result
    st.session_state.cache_time[cache_key] = time.time()

city_name = st.text_input("Enter a City or Region", placeholder="e.g., Berlin, Tokyo, New York, London")

def extract_metrics_from_text(text: str):
    """Extract metrics from agent output text."""
    metrics = {}
    neighborhoods = []
    data_for_chart = []
    
    lines = text.split('\n')
    current_area = None
    current_price = None
    current_yield = None
    
    for line in lines:
        # Extract area names - multiple patterns
        area_patterns = [
            r'\*\*Area\s*\d+[:\s]*([^*\n]+)\*\*',
            r'\*\*([A-Z][A-Za-z\s-]+?)\*\*[:\s]*(?:Price|Yield)',
            r'(?:Area|Neighborhood|District)[:\s]*([A-Z][A-Za-z\s-]+?)(?:\n|Price)',
        ]
        
        area_match = None
        for pattern in area_patterns:
            area_match = re.search(pattern, line, re.IGNORECASE)
            if area_match:
                break
        
        if area_match:
            if current_area and current_price:
                data_for_chart.append({
                    "Neighborhood": current_area,
                    "Avg Price ($)": current_price,
                    "Rental Yield (%)": current_yield or 0
                })
            current_area = area_match.group(1).strip()
            if current_area not in neighborhoods:
                neighborhoods.append(current_area)
            current_price = None
            current_yield = None
        
        # Extract prices - handle various formats
        price_patterns = [
            r'Price[:\s]*[\$€£¥]?\s*([\d,]+(?:\.\d+)?)\s*[-–]\s*[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
            r'[\$€£¥]\s*([\d,]+(?:\.\d+)?)\s*(?:million|mil|M)',
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, line, re.IGNORECASE)
            if price_match and current_area:
                if len(price_match.groups()) >= 2:
                    low = float(price_match.group(1).replace(',', ''))
                    high = float(price_match.group(2).replace(',', ''))
                    current_price = (low + high) / 2
                else:
                    current_price = float(price_match.group(1).replace(',', ''))
                    if 'million' in line.lower() or 'mil' in line.lower():
                        current_price *= 1000000
                break
        
        # Extract rental yields
        yield_match = re.search(r'Yield[:\s]*([\d.]+)\s*%', line, re.IGNORECASE)
        if yield_match and current_area:
            current_yield = float(yield_match.group(1))
    
    # Add last area
    if current_area and current_price:
        data_for_chart.append({
            "Neighborhood": current_area,
            "Avg Price ($)": current_price,
            "Rental Yield (%)": current_yield or 0
        })
    
    # Calculate average yield
    all_yields = re.findall(r'([\d.]+)\s*%', text)
    if all_yields:
        yields_float = [float(y) for y in all_yields if float(y) < 50]
        if yields_float:
            metrics["Avg Rental Yield (%)"] = sum(yields_float) / len(yields_float)
    
    df = pd.DataFrame(data_for_chart) if data_for_chart else None
    
    return metrics, neighborhoods, df


if st.button("🔍 Run Analysis", type="primary"):
    if not city_name.strip():
        st.warning("⚠️ Please enter a valid city name.")
    else:
        # Check cache first
        cached_result = get_cached_result(city_name)
        
        if cached_result:
            st.success(f"📦 Using cached results for {city_name} (saved within last hour)")
            output_text = cached_result
        else:
            # Create progress container
            progress_container = st.container()
            progress_text = progress_container.empty()
            log_container = st.expander("🔍 **Live Process Log**", expanded=True)
            
            # Capture stdout for verbose output
            log_capture = StringIO()
            
            # Progress callback
            def update_progress(message):
                progress_text.info(message)
                log_container.markdown(f"- {message}")
            
            try:
                update_progress(f"🚀 Initializing analysis for **{city_name}**...")
                time.sleep(0.5)
                
                # Capture verbose output
                old_stdout = sys.stdout
                sys.stdout = log_capture
                
                try:
                    result = run_property_investment_analysis(city_name, update_progress)
                finally:
                    sys.stdout = old_stdout
                
                # Show captured logs
                captured_output = log_capture.getvalue()
                if captured_output:
                    with log_container:
                        st.code(captured_output, language="text")
                
                # Handle different result formats
                if isinstance(result, dict):
                    output_text = result.get("output", str(result))
                elif hasattr(result, 'raw'):
                    output_text = result.raw
                else:
                    output_text = str(result)
                
                # Cache the result
                set_cached_result(city_name, output_text)
                progress_text.empty()
                
            except Exception as e:
                sys.stdout = old_stdout
                error_msg = str(e)
                if "rate_limit" in error_msg.lower():
                    st.error("⏱️ **Rate Limit Reached**: Please wait 60 seconds before trying again.")
                    st.info("💡 Consider upgrading at https://console.groq.com/settings/billing")
                else:
                    st.error(f"❌ Error: {e}")
                    st.info("Please try again or try a different city.")
                st.stop()
        
        st.success(f"✅ Analysis completed for **{city_name}**!")

        # Extract metrics
        metrics, neighborhoods, df = extract_metrics_from_text(output_text)

        # Display metrics
        st.markdown("### 📊 Investment Overview")
        
        cols = st.columns([1, 2])
        
        with cols[0]:
            if metrics:
                for key, val in metrics.items():
                    st.metric(label=key, value=f"{val:.2f}%")
            
            if neighborhoods:
                st.markdown("**📍 Top Neighborhoods:**")
                for i, neighborhood in enumerate(neighborhoods[:3], 1):
                    st.write(f"{i}. {neighborhood}")
        
        with cols[1]:
            # Visualization
            if df is not None and not df.empty and len(df) > 0:
                st.markdown("**💰 Price Comparison**")
                
                price_chart = (
                    alt.Chart(df)
                    .mark_bar(color="#1f77b4", size=40)
                    .encode(
                        x=alt.X("Neighborhood:N", title="Neighborhood", sort="-y"),
                        y=alt.Y("Avg Price ($):Q", title="Average Price ($)"),
                        tooltip=["Neighborhood", "Avg Price ($)", "Rental Yield (%)"]
                    )
                    .properties(height=300)
                )
                st.altair_chart(price_chart, use_container_width=True)
                
                st.markdown("**📋 Detailed Metrics**")
                display_df = df.copy()
                display_df["Avg Price ($)"] = display_df["Avg Price ($)"].apply(lambda x: f"${x:,.0f}")
                display_df["Rental Yield (%)"] = display_df["Rental Yield (%)"].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("💡 Chart data not available. Check full report below.")

        # Full report
        with st.expander("📋 Full Analysis Report", expanded=False):
            st.markdown(output_text)

# Show cache info
if st.session_state.cache:
    with st.sidebar:
        st.markdown("### 📦 Cached Cities")
        st.caption(f"Results cached for {CACHE_DURATION // 60} minutes")
        
        # Get city names from cache
        cached_cities = []
        for cache_key in st.session_state.cache_time.keys():
            cache_age = time.time() - st.session_state.cache_time[cache_key]
            if cache_age < CACHE_DURATION:
                mins_ago = int(cache_age / 60)
                cached_cities.append(f"• Cached {mins_ago}m ago")
        
        for city_info in cached_cities[:5]:  # Show max 5
            st.text(city_info)
        
        if st.button("🗑️ Clear Cache"):
            st.session_state.cache = {}
            st.session_state.cache_time = {}
            st.rerun()

# Footer
st.markdown("---")
st.markdown("*Powered by CrewAI + Groq + Serper* | Optimized with caching and live progress")
