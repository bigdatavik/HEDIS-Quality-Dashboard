"""
HEDIS Quality Measures Dashboard

Interactive dashboard for NCQA compliance tracking and gap closure analytics.
Shows quality score improvement from 85% -> 92%.

For quality team use.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="HEDIS Quality Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration from environment variables (with defaults for local testing)
CATALOG = os.getenv("CATALOG_NAME", "humana_quality")
SCHEMA = os.getenv("SCHEMA_NAME", "hedis_gold")
SQL_WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")

# MCP Configuration (Natural Language Search)
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "01f0b223e0e31cb0b4b093ef8578bcf8")
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = os.getenv("KNOWLEDGE_ASSISTANT_ENDPOINT_ID", "ka-0bbaf97e-endpoint")
MCP_ENABLED = GENIE_SPACE_ID is not None

# Databricks SQL connection
@st.cache_resource
def get_databricks_connection():
    """Create Databricks SQL connection using official Databricks pattern"""
    try:
        from databricks import sql
        from databricks.sdk.core import Config
        
        # Config() reads from DATABRICKS_HOST env var (set in app.yaml for Databricks Apps)
        cfg = Config()
        
        return sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def read_table(table_name: str) -> pd.DataFrame:
    """Read table from Databricks using SQL Connector"""
    conn = get_databricks_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {CATALOG}.{SCHEMA}.{table_name}")
            result = cursor.fetchall_arrow().to_pandas()
            return result
    except Exception as e:
        st.error(f"Error reading {table_name}: {e}")
        return pd.DataFrame()


def query_data(sql_query: str) -> pd.DataFrame:
    """Execute custom SQL query"""
    conn = get_databricks_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall_arrow().to_pandas()
            return result
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Header
st.markdown('<div class="main-header">📊 HEDIS Quality Measures Dashboard</div>', unsafe_allow_html=True)
st.markdown("### NCQA Compliance Tracking for Quality Team")
st.markdown("---")

# Load data
@st.cache_data(ttl=3600)
def load_all_data():
    """Load all dashboard data"""
    return {
        'quality_trends': read_table('quality_trends'),
        'measure_performance': read_table('measure_performance'),
        'gap_analytics': read_table('gap_closure_analytics'),
        'member_quality': read_table('member_quality_summary'),
        'open_gaps': read_table('open_gaps_dashboard')
    }

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3e5.png", width=100)
    st.title("Navigation")
    
    # Data refresh info
    st.info(f"**Catalog:** {CATALOG}\n\n**Schema:** {SCHEMA}\n\n**Last Refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Filters
    st.markdown("### Filters")
    current_year = datetime.now().year
    year_filter = st.selectbox(
        "Measurement Year",
        options=[current_year, current_year - 1, current_year - 2],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This dashboard tracks HEDIS quality measures and gap closure progress.
    
    **Key Features:**
    - Quality score trends
    - Measure performance
    - Gap closure analytics
    - Member-level insights
    """)

# Load data
try:
    data = load_all_data()
    
    if all(not df.empty for df in data.values()):
        st.success("✅ Connected to Databricks - Data loaded successfully!")
    else:
        st.warning("⚠️ Some tables are empty. Run data generation jobs first.")
        
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Overview",
    "📊 Measure Performance", 
    "🎯 Gap Analysis",
    "👥 Member Insights",
    "🔍 Member Lookup",
    "🤖 MCP Search"
])

# TAB 1: OVERVIEW
with tab1:
    st.markdown("## Quality Performance Overview")
    
    # Get current year data
    current_trend = data['quality_trends'][data['quality_trends']['measurement_year'] == year_filter]
    
    if not current_trend.empty:
        current_data = current_trend.iloc[0]
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(
                label="Overall Quality Score",
                value=f"{current_data['quality_score']:.1f}",
                delta=f"{current_data['yoy_score_change']:.1f} pts vs prior year"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(
                label="Compliance Rate",
                value=f"{current_data['overall_compliance_rate']:.1%}",
                delta=f"{current_data['yoy_compliance_change']:.1%} vs prior year"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Stars Rating",
                value=f"{current_data['stars_rating']:.1f} ⭐",
                delta=None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="NCQA Percentile",
                value=f"{current_data['ncqa_percentile']}th",
                delta=None
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quality Trends Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Quality Score Trend")
        fig_quality = go.Figure()
        
        fig_quality.add_trace(go.Scatter(
            x=data['quality_trends']['measurement_year'],
            y=data['quality_trends']['quality_score'],
            mode='lines+markers+text',
            name='Quality Score',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=12),
            text=data['quality_trends']['quality_score'].apply(lambda x: f"{x:.1f}"),
            textposition='top center',
            textfont=dict(size=14, color='#1f77b4', family='Arial Black')
        ))
        
        # Add target line at 92
        fig_quality.add_hline(y=92, line_dash="dash", line_color="green", 
                             annotation_text="Target: 92", annotation_position="right")
        
        fig_quality.update_layout(
            height=400,
            showlegend=False,
            yaxis=dict(title="Quality Score", range=[80, 100]),
            xaxis=dict(title="Year"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        st.markdown("### Compliance Rate Trend")
        fig_compliance = go.Figure()
        
        fig_compliance.add_trace(go.Scatter(
            x=data['quality_trends']['measurement_year'],
            y=data['quality_trends']['overall_compliance_rate'] * 100,
            mode='lines+markers+text',
            name='Compliance Rate',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=12),
            text=data['quality_trends']['overall_compliance_rate'].apply(lambda x: f"{x:.0%}"),
            textposition='top center',
            textfont=dict(size=14, color='#2ca02c', family='Arial Black')
        ))
        
        # Add target line at 92%
        fig_compliance.add_hline(y=92, line_dash="dash", line_color="green",
                                annotation_text="Target: 92%", annotation_position="right")
        
        fig_compliance.update_layout(
            height=400,
            showlegend=False,
            yaxis=dict(title="Compliance Rate (%)", range=[80, 100]),
            xaxis=dict(title="Year"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_compliance, use_container_width=True)
    
    st.markdown("---")
    
    # Gap Closure Metrics
    col1, col2, col3 = st.columns(3)
    
    if not current_trend.empty:
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Gap Closure Rate",
                value=f"{current_data['gap_closure_rate']:.1%}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(
                label="Members Compliant",
                value=f"{current_data['members_compliant']:,}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="Total Members",
                value=f"{current_data['total_members']:,}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: MEASURE PERFORMANCE
with tab2:
    st.markdown("## HEDIS Measure Performance")
    
    # Filter data for selected year
    year_measures = data['measure_performance'][
        data['measure_performance']['measurement_year'] == year_filter
    ]
    
    if not year_measures.empty:
        # Measure performance bar chart
        st.markdown("### Compliance Rate by Measure")
        
        fig_measures = go.Figure()
        
        # Sort by compliance rate
        year_measures_sorted = year_measures.sort_values('compliance_rate', ascending=True)
        
        # Color code based on performance
        colors = ['#2ca02c' if x >= 0.90 else '#ffc107' if x >= 0.80 else '#dc3545' 
                  for x in year_measures_sorted['compliance_rate']]
        
        fig_measures.add_trace(go.Bar(
            y=year_measures_sorted['measure_code'],
            x=year_measures_sorted['compliance_rate'] * 100,
            orientation='h',
            marker=dict(color=colors),
            text=year_measures_sorted['compliance_rate'].apply(lambda x: f"{x:.1%}"),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Compliance: %{x:.1f}%<extra></extra>'
        ))
        
        fig_measures.update_layout(
            height=500,
            xaxis=dict(title="Compliance Rate (%)", range=[0, 100]),
            yaxis=dict(title="Measure Code"),
            showlegend=False
        )
        
        st.plotly_chart(fig_measures, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed measure table
        st.markdown("### Detailed Performance Metrics")
        
        display_df = year_measures[['measure_code', 'measure_name', 'denominator', 
                                    'numerator', 'compliance_rate', 'gaps_identified', 
                                    'gaps_closed', 'gap_closure_rate']].copy()
        
        display_df['compliance_rate'] = display_df['compliance_rate'].apply(lambda x: f"{x:.1%}")
        display_df['gap_closure_rate'] = display_df['gap_closure_rate'].apply(lambda x: f"{x:.1%}")
        
        display_df = display_df.rename(columns={
            'measure_code': 'Code',
            'measure_name': 'Measure',
            'denominator': 'Eligible',
            'numerator': 'Compliant',
            'compliance_rate': 'Compliance',
            'gaps_identified': 'Gaps ID',
            'gaps_closed': 'Gaps Closed',
            'gap_closure_rate': 'Closure Rate'
        })
        
        st.dataframe(display_df, use_container_width=True, height=400)
    else:
        st.warning(f"No measure data available for {year_filter}")

# TAB 3: GAP ANALYSIS
with tab3:
    st.markdown("## Gap Closure Analytics")
    
    if not data['gap_analytics'].empty:
        # Gap closure summary
        col1, col2, col3 = st.columns(3)
        
        total_gaps = data['gap_analytics']['total_gaps'].sum()
        total_closed = data['gap_analytics']['closed_gaps'].sum()
        overall_closure_rate = total_closed / total_gaps if total_gaps > 0 else 0
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Total Gaps Identified", value=f"{total_gaps:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(label="Gaps Closed", value=f"{total_closed:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Overall Closure Rate", value=f"{overall_closure_rate:.1%}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gap closure by measure
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Gap Closure Rate by Measure")
            
            fig_gap_closure = go.Figure()
            
            gap_sorted = data['gap_analytics'].sort_values('closure_rate', ascending=True)
            
            fig_gap_closure.add_trace(go.Bar(
                y=gap_sorted['measure_code'],
                x=gap_sorted['closure_rate'] * 100,
                orientation='h',
                marker=dict(color='#17a2b8'),
                text=gap_sorted['closure_rate'].apply(lambda x: f"{x:.1%}"),
                textposition='outside'
            ))
            
            fig_gap_closure.update_layout(
                height=400,
                xaxis=dict(title="Closure Rate (%)", range=[0, 100]),
                yaxis=dict(title="Measure"),
                showlegend=False
            )
            
            st.plotly_chart(fig_gap_closure, use_container_width=True)
        
        with col2:
            st.markdown("### Average Days to Close Gap")
            
            fig_days = go.Figure()
            
            gap_days = data['gap_analytics'][data['gap_analytics']['avg_days_to_close'].notna()]
            gap_days_sorted = gap_days.sort_values('avg_days_to_close', ascending=True)
            
            fig_days.add_trace(go.Bar(
                y=gap_days_sorted['measure_code'],
                x=gap_days_sorted['avg_days_to_close'],
                orientation='h',
                marker=dict(color='#ff7f0e'),
                text=gap_days_sorted['avg_days_to_close'].apply(lambda x: f"{x:.0f}"),
                textposition='outside'
            ))
            
            fig_days.update_layout(
                height=400,
                xaxis=dict(title="Days"),
                yaxis=dict(title="Measure"),
                showlegend=False
            )
            
            st.plotly_chart(fig_days, use_container_width=True)
        
        st.markdown("---")
        
        # Open gaps table
        st.markdown("### Current Open Gaps")
        
        if not data['open_gaps'].empty:
            # Priority filter
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=['High', 'Medium', 'Low'],
                default=['High', 'Medium', 'Low']
            )
            
            filtered_gaps = data['open_gaps'][data['open_gaps']['priority'].isin(priority_filter)]
            
            st.markdown(f"**Showing {len(filtered_gaps):,} open gaps**")
            
            display_gaps = filtered_gaps[['member_id', 'first_name', 'last_name', 'age', 
                                         'risk_level', 'measure_code', 'measure_name', 
                                         'priority', 'num_attempts', 'assigned_to']].head(100)
            
            st.dataframe(display_gaps, use_container_width=True, height=400)
        else:
            st.info("No open gaps! 🎉")

# TAB 4: MEMBER INSIGHTS
with tab4:
    st.markdown("## Member Quality Insights")
    
    if not data['member_quality'].empty:
        # Member summary
        total_members = len(data['member_quality'])
        active_members = len(data['member_quality'][data['member_quality']['is_active'] == True])
        high_compliance = len(data['member_quality'][data['member_quality']['compliance_rate'] >= 0.90])
        low_compliance = len(data['member_quality'][data['member_quality']['compliance_rate'] < 0.70])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Total Members", value=f"{total_members:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(label="Active Members", value=f"{active_members:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
            st.metric(label="High Compliance (≥90%)", value=f"{high_compliance:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card danger-metric">', unsafe_allow_html=True)
            st.metric(label="Low Compliance (<70%)", value=f"{low_compliance:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Distribution charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Compliance Rate Distribution")
            
            fig_dist = px.histogram(
                data['member_quality'][data['member_quality']['total_measures'] > 0],
                x='compliance_rate',
                nbins=20,
                labels={'compliance_rate': 'Compliance Rate', 'count': 'Number of Members'},
                color_discrete_sequence=['#1f77b4']
            )
            
            fig_dist.update_layout(height=400)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            st.markdown("### Members by Risk Level")
            
            risk_counts = data['member_quality']['risk_level'].value_counts()
            
            fig_risk = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color_discrete_sequence=['#2ca02c', '#ffc107', '#dc3545']
            )
            
            fig_risk.update_layout(height=400)
            st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("---")
        
        # At-risk members table
        st.markdown("### At-Risk Members (Compliance < 70%)")
        
        at_risk = data['member_quality'][
            (data['member_quality']['compliance_rate'] < 0.70) & 
            (data['member_quality']['total_measures'] > 0)
        ].sort_values('compliance_rate')
        
        if not at_risk.empty:
            display_at_risk = at_risk[['member_id', 'first_name', 'last_name', 'age', 
                                       'risk_level', 'total_measures', 'compliant_measures', 
                                       'open_gaps', 'compliance_rate']].head(50)
            
            display_at_risk['compliance_rate'] = display_at_risk['compliance_rate'].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(display_at_risk, use_container_width=True, height=400)
        else:
            st.success("No at-risk members! 🎉")

# TAB 5: MEMBER LOOKUP
with tab5:
    st.markdown("## Member Lookup")
    
    st.markdown("Search for a specific member to view their quality measures and gaps.")
    
    # Search input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "Enter Member ID, Last Name, or First Name",
            placeholder="e.g., M000001 or Smith"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_term and (search_button or search_term):
        # Search in member_quality table
        search_results = data['member_quality'][
            data['member_quality']['member_id'].str.contains(search_term, case=False, na=False) |
            data['member_quality']['last_name'].str.contains(search_term, case=False, na=False) |
            data['member_quality']['first_name'].str.contains(search_term, case=False, na=False)
        ]
        
        if not search_results.empty:
            st.success(f"Found {len(search_results)} member(s)")
            
            for idx, member in search_results.head(5).iterrows():
                with st.expander(f"👤 {member['first_name']} {member['last_name']} ({member['member_id']})", expanded=True):
                    # Member details
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Age", member['age'])
                    with col2:
                        st.metric("Gender", member['gender'])
                    with col3:
                        st.metric("Risk Level", member['risk_level'])
                    with col4:
                        status = "✅ Active" if member['is_active'] else "❌ Inactive"
                        st.markdown(f"**Status:** {status}")
                    
                    st.markdown("---")
                    
                    # Quality metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Measures", member['total_measures'])
                    with col2:
                        st.metric("Compliant", member['compliant_measures'])
                    with col3:
                        st.metric("Compliance Rate", f"{member['compliance_rate']:.1%}")
                    
                    # Open gaps
                    if member['open_gaps'] > 0:
                        st.markdown(f"**⚠️ Open Gaps: {member['open_gaps']}**")
                        
                        member_gaps = data['open_gaps'][
                            data['open_gaps']['member_id'] == member['member_id']
                        ]
                        
                        if not member_gaps.empty:
                            gap_display = member_gaps[['measure_code', 'measure_name', 
                                                       'priority', 'num_attempts', 'assigned_to']]
                            st.dataframe(gap_display, use_container_width=True)
                    else:
                        st.success("✅ No open gaps!")
        else:
            st.warning(f"No members found matching '{search_term}'")

# TAB 6: MCP SEARCH
with tab6:
    st.markdown("## 🤖 MCP Natural Language Search")
    
    if not MCP_ENABLED:
        st.warning("⚠️ MCP is not configured. Please set GENIE_SPACE_ID in environment.")
        st.stop()
    
    st.markdown("Ask questions in natural language about HEDIS quality measures, members, and gaps.")
    
    # Initialize HEDIS Agent with MCP tools
    @st.cache_resource
    def get_hedis_agent():
        """Initialize HEDIS Agent with MCP tools"""
        try:
            from hedis_agent import HEDISQualityAgent
            
            agent = HEDISQualityAgent(
                genie_space_id=GENIE_SPACE_ID,
                catalog=CATALOG,
                schema=SCHEMA,
                knowledge_assistant_endpoint_id=KNOWLEDGE_ASSISTANT_ENDPOINT_ID,
                ai_model_name=os.getenv("AI_MODEL_NAME", "databricks-meta-llama-3-1-70b-instruct")
            )
            
            return agent
        except Exception as e:
            st.error(f"Error initializing HEDIS Agent: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    agent = get_hedis_agent()
    
    if agent:
        # Get system status
        system_status = agent.get_system_status()
        
        # Quick status indicator at top
        genie_status = system_status.get('genie', {})
        uc_status = system_status.get('uc_functions', {})
        ka_status = system_status.get('knowledge_assistant', {})
        
        # Determine overall status
        all_healthy = (
            system_status.get('llm_ready') and
            genie_status.get('status') == 'healthy' and
            uc_status.get('status') == 'healthy'
        )
        
        if all_healthy:
            st.success(f"✅ **AI Agent Ready** | {system_status.get('tools_count', 0)} tools available")
        else:
            st.warning("⚠️ **AI Agent Partially Ready** | Some services may be unavailable")
        
        # Detailed connectivity information in collapsible section
        with st.expander("🔧 System Status & Connectivity Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Core Services")
                
                # LLM Status
                st.markdown("**🧠 AI Model**")
                if system_status.get('llm_ready'):
                    st.success("✅ Ready")
                else:
                    st.error("❌ Not initialized")
                
                # Genie Status
                st.markdown("**🔮 Genie MCP**")
                if genie_status.get('status') == 'healthy':
                    st.success(f"✅ Connected")
                    st.caption(f"Server: {genie_status.get('mcp_url', 'N/A')}")
                else:
                    st.error("❌ Not available")
                
                # UC Functions Status
                st.markdown("**⚙️ UC Functions MCP**")
                if uc_status.get('status') == 'healthy':
                    st.success(f"✅ Connected ({uc_status.get('tools_count', 0)} functions)")
                    st.caption(f"Server: {uc_status.get('mcp_url', 'N/A')}")
                    if uc_status.get('tools'):
                        st.markdown("**Available Functions:**")
                        for tool in uc_status.get('tools', [])[:6]:  # Show first 6
                            st.markdown(f"- `{tool}`")
                else:
                    st.warning("⚠️ Not connected")
            
            with col2:
                st.markdown("#### Optional Services")
                
                # Knowledge Assistant Status
                st.markdown("**📚 Knowledge Assistant**")
                if ka_status.get('status') == 'healthy':
                    st.success("✅ Ready")
                    st.caption(f"Endpoint: {ka_status.get('endpoint_id', 'N/A')}")
                elif ka_status.get('status') == 'not_configured':
                    st.info("ℹ️ Not configured (optional)")
                else:
                    st.warning("⚠️ Not available")
                
                st.markdown("---")
                st.markdown(f"**📊 Total Tools Available:** {system_status.get('tools_count', 0)}")
        
        # Query Interface
        query_text = st.text_input(
            "Ask a question:",
            placeholder="e.g., Show me member M000001's gaps, or Which members have open BCS gaps?",
            key="mcp_query"
        )
        
        st.markdown("*The AI agent will automatically choose the best tool(s) to answer your question.*")
        
        # Example queries
        with st.expander("💡 Example Queries"):
            st.markdown("""
            **Member Queries:**
            - Show me member M000001's quality metrics
            - What are M000100's open gaps?
            - Get all measures for member M000050
            
            **Gap Queries:**
            - Which members have open BCS gaps?
            - Show members with gaps in diabetes care
            - List all at-risk members
            
            **Performance Queries:**
            - What's the performance trend for CDC measure?
            - Show quality scores by year
            
            **Knowledge Queries:**
            - What are the HEDIS compliance requirements?
            - Explain the gap closure protocol
            - What is the NCQA audit process?
            """)
        
        # Initialize conversation history in session state
        if "mcp_conversation" not in st.session_state:
            st.session_state.mcp_conversation = []
        
        if query_text:
            with st.spinner("🤖 Agent is thinking..."):
                try:
                    # Get agent response
                    response = agent.chat(query_text, st.session_state.mcp_conversation)
                    
                    # Store in conversation history
                    st.session_state.mcp_conversation.append({"role": "user", "content": query_text})
                    st.session_state.mcp_conversation.append({"role": "assistant", "content": response})
                    
                    # Display response
                    st.markdown("### 🤖 Agent Response")
                    st.markdown(response)
                    
                except Exception as e:
                    st.error(f"❌ Error processing query: {e}")
                    st.markdown("**Troubleshooting:**")
                    st.markdown("- Check that MCP servers are accessible")
                    st.markdown("- Verify AI model endpoint is available")
                    st.markdown("- Ensure tools are properly initialized")
        
        # Conversation history
        if st.session_state.mcp_conversation:
            with st.expander("💬 Conversation History"):
                for i in range(0, len(st.session_state.mcp_conversation), 2):
                    if i < len(st.session_state.mcp_conversation):
                        user_msg = st.session_state.mcp_conversation[i]
                        st.markdown(f"**You:** {user_msg['content']}")
                        
                        if i + 1 < len(st.session_state.mcp_conversation):
                            agent_msg = st.session_state.mcp_conversation[i + 1]
                            st.markdown(f"**Agent:** {agent_msg['content'][:200]}...")
                            st.markdown("---")
            
            if st.button("🗑️ Clear Conversation"):
                st.session_state.mcp_conversation = []
                st.experimental_rerun()
    
    else:
        st.error("❌ HEDIS Agent failed to initialize")
        st.markdown("**Troubleshooting:**")
        st.markdown("1. Check that `databricks-mcp` package is installed")
        st.markdown("2. Verify Genie Space ID is correct")
        st.markdown("3. Confirm UC Functions are created in the schema")
        st.markdown("4. Ensure Knowledge Assistant endpoint is deployed (optional)")
        st.markdown("5. Verify AI model endpoint is accessible")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data Source:** Databricks Unity Catalog")
with col2:
    st.markdown(f"**Catalog:** {CATALOG}.{SCHEMA}")
with col3:
    st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

