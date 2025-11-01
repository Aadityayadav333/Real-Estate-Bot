import streamlit as st
import pandas as pd
import re
import altair as alt
from crew import run_property_investment_analysis
import time

st.set_page_config(
    page_title="🏙️ Property Investment Research Assistant",
    layout="wide",
)

st.title("🏙️ Retail Property Investment Analyzer")
st.markdown("Analyze **retail property investment opportunities** in any city using real market data.")
st.info("⚠️ Using free API tier. Analysis may take 1-2 minutes. If rate limit is reached, wait 60 seconds.")

city_name = st.text_input("Enter a City or Region", placeholder="e.g., Berlin, Tokyo, New York, London")

def extract_metrics_from_text(text: str):
    """
    Enhanced extraction of metrics from agent output text.
    """
    metrics = {}
    neighborhoods = []
    data_for_chart = []

    # Split text into sections for each neighborhood
    sections = re.split(r'\*\*(?:Neighborhood|Area|Location|District)\s*\d+[:\s]*', text, flags=re.IGNORECASE)
    
    # Also try line-based extraction
    lines = text.split('\n')
    
    current_area = None
    current_price = None
    current_yield = None
    
    for line in lines:
        # Extract area/neighborhood names
        area_match = re.search(r'(?:Area|Neighborhood|District|Location)[:\s]*([A-Z][A-Za-z\s-]+?)(?:\n|$|,|\*)', line, re.IGNORECASE)
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
        price_match = re.search(r'(?:Price|Cost|Range)[:\s]*[\$€£¥]?\s*([\d,]+(?:\.\d+)?)\s*(?:to|-|–)\s*[\$€£¥]?\s*([\d,]+(?:\.\d+)?)', line, re.IGNORECASE)
        if price_match and current_area:
            low = float(price_match.group(1).replace(',', ''))
            high = float(price_match.group(2).replace(',', ''))
            current_price = (low + high) / 2
        elif not price_match:
            # Try single price
            single_price = re.search(r'[\$€£¥]\s*([\d,]+(?:\.\d+)?)\s*(?:million|mil|M|k|thousand)?', line, re.IGNORECASE)
            if single_price and current_area and not current_price:
                price_val = float(single_price.group(1).replace(',', ''))
                # Handle millions/thousands
                if 'million' in line.lower() or 'mil' in line.lower():
                    price_val *= 1000000
                elif 'k' in line.lower() or 'thousand' in line.lower():
                    price_val *= 1000
                current_price = price_val
        
        # Extract rental yields
        yield_match = re.search(r'(?:Rental\s*)?Yield[:\s]*([\d.]+)\s*%', line, re.IGNORECASE)
        if yield_match and current_area:
            current_yield = float(yield_match.group(1))
    
    # Add last area if exists
    if current_area and current_price:
        data_for_chart.append({
            "Neighborhood": current_area,
            "Avg Price ($)": current_price,
            "Rental Yield (%)": current_yield or 0
        })
    
    # Extract overall metrics
    all_yields = re.findall(r'([\d.]+)\s*%', text)
    if all_yields:
        yields_float = [float(y) for y in all_yields if float(y) < 50]  # Filter out unrealistic values
        if yields_float:
            metrics["Avg Rental Yield (%)"] = sum(yields_float) / len(yields_float)
    
    df = pd.DataFrame(data_for_chart) if data_for_chart else None
    
    return metrics, neighborhoods, df


if st.button("🔍 Run Analysis", type="primary"):
    if not city_name.strip():
        st.warning("⚠️ Please enter a valid city name.")
    else:
        with st.spinner(f"🔎 Researching retail investment opportunities in {city_name}... This may take 1-2 minutes."):
            try:
                result = run_property_investment_analysis(city_name)
                st.success(f"✅ Analysis completed for {city_name}!")

                # Handle different result formats
                if isinstance(result, dict):
                    output_text = result.get("output", str(result))
                elif hasattr(result, 'raw'):
                    output_text = result.raw
                else:
                    output_text = str(result)

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
                        
                        # Price chart
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
                        
                        # Show data table
                        st.markdown("**📋 Detailed Metrics**")
                        display_df = df.copy()
                        display_df["Avg Price ($)"] = display_df["Avg Price ($)"].apply(lambda x: f"${x:,.0f}")
                        display_df["Rental Yield (%)"] = display_df["Rental Yield (%)"].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("💡 Chart data not available. Check full report below for details.")

                # Full report in expander
                with st.expander("📋 Full Analysis Report", expanded=False):
                    st.markdown(output_text)

            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower():
                    st.error("⏱️ **Rate Limit Reached**: Please wait 60 seconds before trying again.")
                    st.info("💡 **Tip**: The free Groq API tier has limited requests per minute. Consider upgrading at https://console.groq.com/settings/billing")
                else:
                    st.error(f"❌ Error during analysis: {e}")
                    st.info("Please try again or try a different city name.")

# Footer
st.markdown("---")
st.markdown("*Powered by CrewAI + Groq + Serper* | Real-time market data analysis")
