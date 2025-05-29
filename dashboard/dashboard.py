import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import plotly.graph_objects as go

BASE_URL = "http://localhost:8000/api"

def fetch_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error fetching {endpoint}: {e}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        st.error(f"JSON Decode Error for {endpoint}: {e}")
        return []
    except requests.RequestException as e:
        st.error(f"Error fetching {endpoint}: {e}")
        return []

st.set_page_config(page_title="Logistics Fleet Management", layout="wide")
st.title("Logistics Fleet Management Dashboard")

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.selectbox(
    "Select Section",
    ["Deliveries", "Vehicles", "Drivers", "Weather", "Maintenance", "Routes", "SLAs", "Traffic", "Metrics"]
)

# Deliveries Section
if section == "Deliveries":
    st.header("Deliveries")
    deliveries = fetch_data("deliveries")
    df_deliveries = pd.DataFrame(deliveries)
    
    if not df_deliveries.empty:
        # Convert datetime fields to appropriate format
        if 'scheduled_time' in df_deliveries.columns:
            df_deliveries['scheduled_time'] = pd.to_datetime(df_deliveries['scheduled_time'])
        if 'actual_time' in df_deliveries.columns:
            df_deliveries['actual_time'] = pd.to_datetime(df_deliveries['actual_time'])
        if 'date' in df_deliveries.columns:
            df_deliveries['date'] = pd.to_datetime(df_deliveries['date']).dt.date
        
        # KPI Cards
        st.subheader("Delivery KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sla_rate = df_deliveries['sla_compliance'].mean() * 100 if 'sla_compliance' in df_deliveries.columns else 0
            st.metric("SLA Compliance Rate (%)", f"{sla_rate:.2f}%", delta=None)
        with col2:
            avg_delay = df_deliveries['delay_minutes'].mean() if 'delay_minutes' in df_deliveries.columns else 0
            st.metric("Avg Delay (min)", f"{avg_delay:.1f}", delta=None)
        with col3:
            avg_fuel = df_deliveries['fuel_consumed'].mean() if 'fuel_consumed' in df_deliveries.columns else 0
            st.metric("Avg Fuel Consumed (L)", f"{avg_fuel:.1f}", delta=None)
        with col4:
            on_time_rate = (len(df_deliveries[(df_deliveries['status'] == 'Delivered') & (df_deliveries['delay_minutes'] <= 0)]) / len(df_deliveries)) * 100 if 'status' in df_deliveries.columns and 'delay_minutes' in df_deliveries.columns else 0
            st.metric("On-Time Delivery Rate (%)", f"{on_time_rate:.2f}%", delta=None)
        
        # Filters
        with st.expander("Filter Deliveries", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_options = sorted(df_deliveries['status'].unique()) if 'status' in df_deliveries.columns else []
                selected_status = st.multiselect("Status", options=status_options, default=status_options)
            
            with col2:
                sla_type_options = sorted(df_deliveries['sla_type'].unique()) if 'sla_type' in df_deliveries.columns else []
                selected_sla_type = st.multiselect("SLA Type", options=sla_type_options, default=sla_type_options)
            
            with col3:
                min_date = df_deliveries['date'].min() if 'date' in df_deliveries.columns else None
                max_date = df_deliveries['date'].max() if 'date' in df_deliveries.columns else None
                if pd.isna(min_date) or pd.isna(max_date):
                    st.warning("Invalid date range in data. Showing all dates.")
                    start_date, end_date = None, None
                else:
                    selected_dates = st.date_input(
                        "Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        start_date, end_date = selected_dates
                    else:
                        start_date = end_date = selected_dates
            
            with col4:
                compliance_options = ["All", "Compliant", "Non-Compliant"]
                selected_compliance = st.selectbox("Compliance Status", options=compliance_options)
        
        # Apply Filters
        filtered_df = df_deliveries.copy()
        if selected_status:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        if selected_sla_type:
            filtered_df = filtered_df[filtered_df['sla_type'].isin(selected_sla_type)]
        if start_date is not None and end_date is not None:
            filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) & 
                (filtered_df['date'] <= end_date)
            ]
        if selected_compliance != "All":
            if selected_compliance == "Compliant":
                filtered_df = filtered_df[filtered_df['sla_compliance'] == 1]
            else:  # Non-Compliant
                filtered_df = filtered_df[filtered_df['sla_compliance'] == 0]
        
        # Display Filtered Table
        desired_columns = [
            "id", "vehicle_id", "driver_id", "scheduled_time", "actual_time",
            "status", "sla_type", "distance_km", "fuel_consumed", "delay_minutes",
            "sla_compliance"
        ]
        available_columns = list(dict.fromkeys([col for col in desired_columns if col in filtered_df.columns]))
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Delivery Insights")
        
        # Sankey Diagram (Delivery Flow by SLA Type and Compliance)
        if 'sla_type' in filtered_df.columns and 'sla_compliance' in filtered_df.columns:
            sankey_data = filtered_df.groupby(['sla_type', 'sla_compliance']).size().reset_index(name='count')
            sankey_data['compliance_label'] = sankey_data['sla_compliance'].map({1: 'Compliant', 0: 'Non-Compliant'})
            
            labels = list(sankey_data['sla_type'].unique()) + list(sankey_data['compliance_label'].unique())
            source = [labels.index(sla) for sla in sankey_data['sla_type']]
            target = [labels.index(comp) for comp in sankey_data['compliance_label']]
            value = sankey_data['count']
            
            fig_sankey = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value
                )
            )])
            fig_sankey.update_layout(title="Delivery Flow by SLA Type and Compliance", height=400)
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.warning("SLA type or compliance data missing for Sankey diagram.")
        
        # Box Plot (Delay Minutes by Status)
        if 'delay_minutes' in filtered_df.columns and 'status' in filtered_df.columns:
            fig_box = px.box(
                filtered_df,
                x='status',
                y='delay_minutes',
                color='status',
                title="Delay Minutes by Delivery Status",
                labels={'status': 'Status', 'delay_minutes': 'Delay (min)'}
            )
            fig_box.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("Delay or status data missing for box plot.")
        
        # Scatter Plot (Fuel Consumed vs. Distance)
        if 'fuel_consumed' in filtered_df.columns and 'distance_km' in filtered_df.columns and 'status' in filtered_df.columns:
            fig_scatter = px.scatter(
                filtered_df,
                x='distance_km',
                y='fuel_consumed',
                color='status',
                hover_data=['id'],
                title="Fuel Consumed vs. Distance",
                labels={'distance_km': 'Distance (km)', 'fuel_consumed': 'Fuel Consumed (L)'}
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("Fuel, distance, or status data missing for scatter plot.")
        
        # Existing Bar Chart: Status Distribution
        if 'status' in filtered_df.columns:
            status_counts = filtered_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_bar = px.bar(
                status_counts,
                x='status',
                y='count',
                color='status',
                title="Delivery Status Distribution",
                labels={'status': 'Status', 'count': 'Number of Deliveries'}
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Status data missing for bar chart.")
    else:
        st.warning("No delivery data available. Check FastAPI logs and API response.")

# Vehicles Section
elif section == "Vehicles":
    st.header("Vehicles")
    vehicles = fetch_data("vehicles")
    df_vehicles = pd.DataFrame(vehicles)
    
    if not df_vehicles.empty:
        # Convert datetime fields
        if 'last_maintenance_date' in df_vehicles.columns:
            df_vehicles['last_maintenance_date'] = pd.to_datetime(df_vehicles['last_maintenance_date']).dt.date
        
        # KPI Cards
        st.subheader("Vehicle KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fuel_eff = df_vehicles['fuel_efficiency'].mean() if 'fuel_efficiency' in df_vehicles.columns else 0
            st.metric("Avg Fuel Efficiency (km/L)", f"{fuel_eff:.1f}", delta=None)
        with col2:
            idle_hours = df_vehicles['idle_hours'].mean() if 'idle_hours' in df_vehicles.columns else 0
            st.metric("Avg Idle Hours", f"{idle_hours:.1f}", delta=None)
        with col3:
            overdue_maint = len(df_vehicles[
            (pd.Timestamp.now().normalize() - pd.to_datetime(df_vehicles['last_maintenance_date'])).dt.days > 180
            ]) if 'last_maintenance_date' in df_vehicles.columns else 0
            st.metric("Vehicles Overdue Maintenance", f"{overdue_maint}", delta=None)
        with col4:
            poor_battery = (len(df_vehicles[df_vehicles['battery_health'] < 70]) / len(df_vehicles)) * 100 if 'battery_health' in df_vehicles.columns and not df_vehicles.empty else 0
            st.metric("Poor Battery Health (%)", f"{poor_battery:.1f}%", delta=None)
        
        # Filters
        with st.expander("Filter Vehicles", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_options = sorted(df_vehicles['status'].unique()) if 'status' in df_vehicles.columns else []
                selected_status = st.multiselect("Status", status_options, default=status_options)
            
            with col2:
                min_fuel_eff = float(df_vehicles['fuel_efficiency'].min()) if 'fuel_efficiency' in df_vehicles.columns else 0
                max_fuel_eff = float(df_vehicles['fuel_efficiency'].max()) if 'fuel_efficiency' in df_vehicles.columns else 0
                selected_fuel_eff = st.slider(
                    "Fuel Efficiency (km/L)",
                    min_value=min_fuel_eff,
                    max_value=max_fuel_eff,
                    value=(min_fuel_eff, max_fuel_eff),
                    step=0.1
                ) if min_fuel_eff != max_fuel_eff else st.slider("Fuel Efficiency (km/L)", 0.0, 1.0, (0.0, 1.0))
            
            with col3:
                min_date = df_vehicles['last_maintenance_date'].min() if 'last_maintenance_date' in df_vehicles.columns else datetime.now().date()
                max_date = df_vehicles['last_maintenance_date'].max() if 'last_maintenance_date' in df_vehicles.columns else datetime.now().date()
                date_range = st.date_input(
                    "Maintenance Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                start_date, end_date = date_range if len(date_range) == 2 else (min_date, max_date)
            
            with col4:
                tire_options = sorted(df_vehicles['tire_condition'].unique()) if 'tire_condition' in df_vehicles.columns else []
                selected_tire = st.multiselect("Tire Condition", options=tire_options, default=tire_options)
        
        # Apply Filters
        filtered_df = df_vehicles.copy()
        if selected_status:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        if 'fuel_efficiency' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['fuel_efficiency'] >= selected_fuel_eff[0]) & 
                (filtered_df['fuel_efficiency'] <= selected_fuel_eff[1])
            ]
        if 'last_maintenance_date' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['last_maintenance_date'] >= start_date) & 
                (filtered_df['last_maintenance_date'] <= end_date)
            ]
        if selected_tire:
            filtered_df = filtered_df[filtered_df['tire_condition'].isin(selected_tire)]
        
        # Display Filtered Table
        desired_columns = [
            "id", "model", "fuel_efficiency", "last_maintenance_date",
            "mileage", "idle_hours", "status", "avg_fuel_consumption",
            "engine_hours", "tire_condition", "battery_health"
        ]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Vehicle Insights")
        
        # Bubble Chart (Fuel Efficiency vs. Mileage)
        if all(col in filtered_df.columns for col in ['fuel_efficiency', 'mileage', 'engine_hours', 'status']):
            fig_bubble = px.scatter(
                filtered_df,
                x='mileage',
                y='fuel_efficiency',
                size='engine_hours',
                color='status',
                hover_data=['id', 'model'],
                title="Fuel Efficiency vs. Mileage",
                labels={'mileage': 'Mileage (km)', 'fuel_efficiency': 'Fuel Efficiency (km/L)', 'engine_hours': 'Engine Hours (miles)'}
            )
            fig_bubble.update_layout(height=400)
            st.plotly_chart(fig_bubble, use_container_width=True)
        else:
            st.warning("Fuel efficiency, mileage, or status data missing for bubble chart.")
            
        # Line Chart (Maintenance Age Over Time)
        if 'last_maintenance_date' in filtered_df.columns and 'tire_condition' in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df['maintenance_age_days'] = [(datetime.now().date() - d).days for d in filtered_df['last_maintenance_date']]
            fig_line = px.line(
                filtered_df,
                x='last_maintenance_date',
                y='maintenance_age_days',
                color='tire_condition',
                title="Days Since Last Maintenance by Tire Condition",
                labels={'last_maintenance_date': 'Maintenance Date', 'maintenance_age_days': 'Days Since Maintenance'}
            )
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Maintenance date or tire condition data missing for line chart.")
            
        # Violin Plot (Battery Health by Status)
        if 'battery_health' in filtered_df.columns and 'status' in filtered_df.columns:
            fig_violin = px.violin(
                filtered_df,
                x='status',
                y='battery_health',
                color='status',
                title="Battery Health by Vehicle Status",
                labels={'status': 'Status', 'battery_health': 'Battery Health (%)'}
            )
            fig_violin.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_violin, use_container_width=True)
        else:
            st.warning("Battery health or status data missing for violin plot.")
            
    else:
        st.error("No vehicle data available. Check FastAPI logs and API response.")

# Drivers Section
elif section == "Drivers":
    st.header("Drivers")
    drivers = fetch_data("drivers")
    df_drivers = pd.DataFrame(drivers)
    
    if not df_drivers.empty:
        # Convert datetime fields
        df_drivers['joined_date'] = pd.to_datetime(df_drivers['joined_date']).dt.date
        df_drivers['training_completed'] = df_drivers['training_completed'].astype(bool)
        
        # KPI Cards
        st.subheader("Driver Performance KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_punctuality = df_drivers['punctuality_score'].mean()
            st.metric("Avg Punctuality Score", f"{avg_punctuality:.1f}", delta=None)
        with col2:
            avg_incidents = df_drivers['incident_count'].mean()
            st.metric("Avg Incidents per Driver", f"{avg_incidents:.2f}", delta=None)
        with col3:
            avg_deliveries = df_drivers['total_deliveries'].mean()
            st.metric("Avg Deliveries per Driver", f"{avg_deliveries:.0f}", delta=None)
        with col4:
            training_rate = (df_drivers['training_completed'].sum() / len(df_drivers)) * 100
            st.metric("Training Completion Rate", f"{training_rate:.1f}%", delta=None)
        
        # Filters
        with st.expander("Filter Drivers", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_options = sorted(df_drivers['status'].unique())
                selected_status = st.multiselect("Status", options=status_options, default=status_options)
            
            with col2:
                min_punctuality = float(df_drivers['punctuality_score'].min())
                max_punctuality = float(df_drivers['punctuality_score'].max())
                selected_punctuality = st.slider(
                    "Punctuality Score",
                    min_value=min_punctuality,
                    max_value=max_punctuality,
                    value=(min_punctuality, max_punctuality),
                    step=0.1
                )
            
            with col3:
                min_date = df_drivers['joined_date'].min()
                max_date = df_drivers['joined_date'].max()
                if pd.isna(min_date) or pd.isna(max_date):
                    st.warning("Invalid join date range. Showing all dates.")
                    start_date, end_date = None, None
                else:
                    selected_dates = st.date_input(
                        "Joined Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        start_date, end_date = selected_dates
                    else:
                        start_date = end_date = selected_dates
            
            with col4:
                training_options = [True, False]
                selected_training = st.multiselect("Training Completed", options=training_options, default=training_options)
        
        # Apply Filters
        filtered_df = df_drivers.copy()
        if selected_status:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        filtered_df = filtered_df[
            (filtered_df['punctuality_score'] >= selected_punctuality[0]) & 
            (filtered_df['punctuality_score'] <= selected_punctuality[1])
        ]
        if start_date is not None and end_date is not None:
            filtered_df = filtered_df[
                (filtered_df['joined_date'] >= start_date) & 
                (filtered_df['joined_date'] <= end_date)
            ]
        if selected_training:
            filtered_df = filtered_df[filtered_df['training_completed'].isin(selected_training)]
        
        # Display Filtered Table
        desired_columns = [
            "id", "name", "license_number", "total_deliveries",
            "punctuality_score", "incident_count", "status",
            "training_completed", "joined_date", "contact_number"
        ]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Driver Insights")
        
        # Status Distribution (Bar Chart)
        status_counts = filtered_df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        fig_status = px.bar(
            status_counts,
            x='status',
            y='count',
            color='status',
            title="Driver Status Distribution",
            labels={'status': 'Status', 'count': 'Number of Drivers'}
        )
        fig_status.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Punctuality Score Distribution (Histogram)
        fig_punctuality = px.histogram(
            filtered_df,
            x='punctuality_score',
            nbins=20,
            title="Punctuality Score Distribution",
            labels={'punctuality_score': 'Punctuality Score', 'count': 'Number of Drivers'}
        )
        fig_punctuality.update_layout(height=400)
        st.plotly_chart(fig_punctuality, use_container_width=True)
        
        # Training Completion Proportion (Pie Chart)
        training_counts = filtered_df['training_completed'].value_counts().reset_index()
        training_counts.columns = ['training_completed', 'count']
        fig_training = px.pie(
            training_counts,
            names='training_completed',
            values='count',
            title="Training Completion Proportion",
            hole=0.3  # Donut chart
        )
        fig_training.update_layout(height=400)
        st.plotly_chart(fig_training, use_container_width=True)
    else:
        st.warning("No driver data available. Check FastAPI logs and API response.")

# Weather Section
elif section == "Weather":
    st.header("Weather")
    weather = fetch_data("weather")
    df_weather = pd.DataFrame(weather)
    
    if not df_weather.empty:
        # Convert datetime fields
        df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp']).dt.date
        
        # KPI Cards
        st.subheader("Weather KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_temp = df_weather['temperature'].mean()
            st.metric("Avg Temperature (°C)", f"{avg_temp:.1f}", delta=None)
        with col2:
            high_severity_rate = (len(df_weather[df_weather['severity'].isin(['Severe', 'Extreme'])]) / len(df_weather)) * 100
            st.metric("High Severity Events", f"{high_severity_rate:.1f}%", delta=None)
        with col3:
            avg_wind = df_weather['wind_speed'].mean()
            st.metric("Avg Wind Speed (km/h)", f"{avg_wind:.1f}", delta=None)
        with col4:
            avg_humidity = df_weather['humidity'].mean()
            st.metric("Avg Humidity (%)", f"{avg_humidity:.1f}", delta=None)
        
        # Filters
        with st.expander("Filter Weather", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                location_options = sorted(df_weather['location'].unique())
                selected_location = st.multiselect("Location", options=location_options, default=location_options)
            
            with col2:
                min_date = df_weather['timestamp'].min()
                max_date = df_weather['timestamp'].max()
                if pd.isna(min_date) or pd.isna(max_date):
                    st.warning("Invalid timestamp range. Showing all dates.")
                    start_date, end_date = None, None
                else:
                    selected_dates = st.date_input(
                        "Timestamp Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        start_date, end_date = selected_dates
                    else:
                        start_date = end_date = selected_dates
            
            with col3:
                condition_options = sorted(df_weather['condition'].unique())
                selected_condition = st.multiselect("Condition", options=condition_options, default=condition_options)
            
            with col4:
                severity_options = sorted(df_weather['severity'].unique())
                selected_severity = st.multiselect("Severity", options=severity_options, default=severity_options)
        
        # Apply Filters
        filtered_df = df_weather.copy()
        if selected_location:
            filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]
        if start_date is not None and end_date is not None:
            filtered_df = filtered_df[
                (filtered_df['timestamp'] >= start_date) & 
                (filtered_df['timestamp'] <= end_date)
            ]
        if selected_condition:
            filtered_df = filtered_df[filtered_df['condition'].isin(selected_condition)]
        if selected_severity:
            filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
        
        # Display Filtered Table
        desired_columns = [
            "id", "location", "timestamp", "temperature",
            "condition", "wind_speed", "humidity", "severity"
        ]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Weather Insights")
        
        # Condition Distribution (Bar Chart)
        condition_counts = filtered_df['condition'].value_counts().reset_index()
        condition_counts.columns = ['condition', 'count']
        fig_condition = px.bar(
            condition_counts,
            x='condition',
            y='count',
            color='condition',
            title="Weather Condition Distribution",
            labels={'condition': 'Condition', 'count': 'Number of Records'}
        )
        fig_condition.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_condition, use_container_width=True)
        
        # Temperature Trends (Line Chart)
        temp_trends = filtered_df.groupby('timestamp')['temperature'].mean().reset_index()
        fig_temp = px.line(
            temp_trends,
            x='timestamp',
            y='temperature',
            title="Average Temperature Trends",
            labels={'timestamp': 'Date', 'temperature': 'Temperature (°C)'}
        )
        fig_temp.update_layout(height=400)
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Severity Proportion (Pie Chart)
        severity_counts = filtered_df['severity'].value_counts().reset_index()
        severity_counts.columns = ['severity', 'count']
        fig_severity = px.pie(
            severity_counts,
            names='severity',
            values='count',
            title="Weather Severity Proportion",
            hole=0.3  # Donut chart
        )
        fig_severity.update_layout(height=400)
        st.plotly_chart(fig_severity, use_container_width=True)
    else:
        st.warning("No weather data available. Check FastAPI logs and API response.")

# Maintenance Section
elif section == "Maintenance":
    st.header("Maintenance")
    maintenance = fetch_data("maintenance")
    df_maintenance = pd.DataFrame(maintenance)
    
    if not df_maintenance.empty:
        # Convert datetime fields
        df_maintenance['date'] = pd.to_datetime(df_maintenance['date']).dt.date
        
        # KPI Cards
        st.subheader("Maintenance KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_cost = df_maintenance['cost'].mean()
            st.metric("Avg Maintenance Cost ($)", f"{avg_cost:.2f}", delta=None)
        with col2:
            vehicle_count = df_maintenance['vehicle_id'].nunique()
            freq_per_vehicle = len(df_maintenance) / vehicle_count if vehicle_count > 0 else 0
            st.metric("Maintenance per Vehicle", f"{freq_per_vehicle:.2f}", delta=None)
        with col3:
            open_issues_rate = (len(df_maintenance[df_maintenance['status'].isin(['Open', 'In Progress'])]) / len(df_maintenance)) * 100
            st.metric("Open Issues (%)", f"{open_issues_rate:.1f}%", delta=None)
        with col4:
            preventive_ratio = (len(df_maintenance[df_maintenance['type'] == 'Preventive']) / len(df_maintenance)) * 100
            st.metric("Preventive Maintenance (%)", f"{preventive_ratio:.1f}%", delta=None)
        
        # Filters
        with st.expander("Filter Maintenance", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                vehicle_options = sorted(df_maintenance['vehicle_id'].unique())
                selected_vehicle = st.multiselect("Vehicle ID", options=vehicle_options, default=vehicle_options)
            
            with col2:
                min_date = df_maintenance['date'].min()
                max_date = df_maintenance['date'].max()
                if pd.isna(min_date) or pd.isna(max_date):
                    st.warning("Invalid date range. Showing all dates.")
                    start_date, end_date = None, None
                else:
                    selected_dates = st.date_input(
                        "Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        start_date, end_date = selected_dates
                    else:
                        start_date = end_date = selected_dates
            
            with col3:
                type_options = sorted(df_maintenance['type'].unique())
                selected_type = st.multiselect("Maintenance Type", options=type_options, default=type_options)
            
            with col4:
                status_options = sorted(df_maintenance['status'].unique())
                selected_status = st.multiselect("Status", options=status_options, default=status_options)
        
        # Apply Filters
        filtered_df = df_maintenance.copy()
        if selected_vehicle:
            filtered_df = filtered_df[filtered_df['vehicle_id'].isin(selected_vehicle)]
        if start_date is not None and end_date is not None:
            filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) & 
                (filtered_df['date'] <= end_date)
            ]
        if selected_type:
            filtered_df = filtered_df[filtered_df['type'].isin(selected_type)]
        if selected_status:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        
        # Display Filtered Table
        desired_columns = ["id", "vehicle_id", "date", "type", "cost", "description", "status"]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Maintenance Insights")
        
        # Box Plot (Cost by Maintenance Type)
        fig_cost = px.box(
            filtered_df,
            x='type',
            y='cost',
            color='type',
            title="Maintenance Cost by Type",
            labels={'type': 'Maintenance Type', 'cost': 'Cost ($)'}
        )
        fig_cost.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # Gantt Chart (Maintenance Timeline by Vehicle)
        gantt_df = filtered_df[['vehicle_id', 'date', 'status']].copy()
        gantt_df['end_date'] = gantt_df['date']  # Assume 1-day duration
        gantt_df['vehicle_id'] = gantt_df['vehicle_id'].astype(str)
        fig_gantt = px.timeline(
            gantt_df,
            x_start='date',
            x_end='end_date',
            y='vehicle_id',
            color='status',
            title="Maintenance Timeline by Vehicle",
            labels={'vehicle_id': 'Vehicle ID', 'date': 'Date'}
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(height=400)
        st.plotly_chart(fig_gantt, use_container_width=True)
        
        # Stacked Bar Chart (Status by Month)
        filtered_df['month'] = pd.to_datetime(filtered_df['date']).dt.to_period('M').astype(str)
        status_by_month = filtered_df.groupby(['month', 'status']).size().reset_index(name='count')
        fig_status = px.bar(
            status_by_month,
            x='month',
            y='count',
            color='status',
            title="Maintenance Status by Month",
            labels={'month': 'Month', 'count': 'Number of Events', 'status': 'Status'}
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.warning("No maintenance data available. Check FastAPI logs and API response.")

# Routes Section
elif section == "Routes":
    st.header("Routes")
    routes = fetch_data("routes")
    df_routes = pd.DataFrame(routes)
    
    if not df_routes.empty:
        # Calculate Geographic Spread (simplified Euclidean distance in degrees)
        def calc_geo_spread(df):
            if len(df) < 2:
                return 0
            lat_diff = df['origin_lat'].max() - df['origin_lat'].min()
            lng_diff = df['origin_lng'].max() - df['origin_lng'].min()
            return ((lat_diff ** 2 + lng_diff ** 2) ** 0.5)
        
        # KPI Cards
        st.subheader("Route KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_distance = df_routes['distance_km'].mean()
            st.metric("Avg Route Distance (km)", f"{avg_distance:.1f}", delta=None)
        with col2:
            high_traffic_rate = (len(df_routes[df_routes['typical_traffic'] == 'High']) / len(df_routes)) * 100
            st.metric("High Traffic Routes (%)", f"{high_traffic_rate:.1f}%", delta=None)
        with col3:
            total_routes = len(df_routes)
            st.metric("Total Routes", f"{total_routes}", delta=None)
        with col4:
            geo_spread = calc_geo_spread(df_routes)
            st.metric("Geographic Spread (deg)", f"{geo_spread:.2f}", delta=None)
        
        # Filters
        with st.expander("Filter Routes", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                name_options = sorted(df_routes['route_name'].unique())
                selected_name = st.multiselect("Route Name", options=name_options, default=name_options)
            
            with col2:
                min_distance = float(df_routes['distance_km'].min())
                max_distance = float(df_routes['distance_km'].max())
                selected_distance = st.slider(
                    "Distance (km)",
                    min_value=min_distance,
                    max_value=max_distance,
                    value=(min_distance, max_distance),
                    step=0.1
                )
            
            with col3:
                traffic_options = sorted(df_routes['typical_traffic'].unique())
                selected_traffic = st.multiselect("Typical Traffic", options=traffic_options, default=traffic_options)
            
            with col4:
                min_lat = float(df_routes['origin_lat'].min())
                max_lat = float(df_routes['origin_lat'].max())
                selected_lat = st.slider(
                    "Origin Latitude",
                    min_value=min_lat,
                    max_value=max_lat,
                    value=(min_lat, max_lat),
                    step=0.01
                )
        
        # Apply Filters
        filtered_df = df_routes.copy()
        if selected_name:
            filtered_df = filtered_df[filtered_df['route_name'].isin(selected_name)]
        filtered_df = filtered_df[
            (filtered_df['distance_km'] >= selected_distance[0]) & 
            (filtered_df['distance_km'] <= selected_distance[1])
        ]
        if selected_traffic:
            filtered_df = filtered_df[filtered_df['typical_traffic'].isin(selected_traffic)]
        filtered_df = filtered_df[
            (filtered_df['origin_lat'] >= selected_lat[0]) & 
            (filtered_df['origin_lat'] <= selected_lat[1])
        ]
        
        # Display Filtered Table
        desired_columns = ["id", "route_name", "origin_lat", "origin_lng", "dest_lat", "dest_lng", "distance_km", "typical_traffic"]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Route Insights")
        
        # Scatter Map (Origins and Destinations)
        # Note: Requires Mapbox token (free at mapbox.com)
        map_data = []
        for _, row in filtered_df.iterrows():
            map_data.extend([
                {'lat': row['origin_lat'], 'lng': row['origin_lng'], 'type': 'Origin', 'route': row['route_name']},
                {'lat': row['dest_lat'], 'lng': row['dest_lng'], 'type': 'Destination', 'route': row['route_name']}
            ])
        map_df = pd.DataFrame(map_data)
        fig_map = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lng',
            color='type',
            hover_data=['route'],
            title="Route Origins and Destinations",
            mapbox_style="open-street-map",  # Fallback; use 'mapbox' with token
            zoom=10
        )
        fig_map.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Violin Plot (Distance by Traffic Level)
        fig_violin = px.violin(
            filtered_df,
            x='typical_traffic',
            y='distance_km',
            color='typical_traffic',
            title="Route Distance by Traffic Level",
            labels={'typical_traffic': 'Traffic Level', 'distance_km': 'Distance (km)'}
        )
        fig_violin.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)
        
        # Heatmap (Traffic Intensity by Route)
        filtered_df['traffic_value'] = filtered_df['typical_traffic'].map({'Low': 1, 'Medium': 2, 'High': 3})
        heatmap_data = filtered_df[['route_name', 'traffic_value']].pivot_table(
            values='traffic_value', index='route_name', aggfunc='mean'
        ).fillna(0)
        fig_heatmap = px.imshow(
            heatmap_data,
            title="Traffic Intensity by Route",
            labels={'x': 'Route', 'y': 'Route Name', 'color': 'Traffic Intensity'},
            color_continuous_scale='Reds'
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("No route data available. Check FastAPI logs and API response.")

# SLAs Section
elif section == "SLAs":
    st.header("SLAs")
    slas = fetch_data("slas")
    df_slas = pd.DataFrame(slas)
    
    if not df_slas.empty:
        # Fetch deliveries for compliance
        deliveries = fetch_data("deliveries")
        df_deliveries = pd.DataFrame(deliveries)
        
        # KPI Cards
        st.subheader("SLA KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_max_hours = df_slas['max_hours'].mean()
            st.metric("Avg Max Hours", f"{avg_max_hours:.1f}", delta=None)
        with col2:
            avg_penalty = df_slas['penalty'].mean()
            st.metric("Avg Penalty ($)", f"{avg_penalty:.2f}", delta=None)
        with col3:
            compliance_rate = (df_deliveries['sla_compliance'].mean() * 100) if not df_deliveries.empty and 'sla_compliance' in df_deliveries.columns else 0
            st.metric("Compliance Rate (%)", f"{compliance_rate:.1f}%", delta=None)
        with col4:
            total_slas = len(df_slas)
            st.metric("Number of SLAs", f"{total_slas}", delta=None)
        
        # Filters
        with st.expander("Filter SLAs", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                name_options = sorted(df_slas['name'].unique())
                selected_name = st.multiselect("SLA Name", options=name_options, default=name_options)
            
            with col2:
                min_hours = float(df_slas['max_hours'].min())
                max_hours = float(df_slas['max_hours'].max())
                selected_hours = st.slider(
                    "Max Hours",
                    min_value=min_hours,
                    max_value=max_hours,
                    value=(min_hours, max_hours),
                    step=0.1
                )
            
            with col3:
                min_penalty = float(df_slas['penalty'].min())
                max_penalty = float(df_slas['penalty'].max())
                selected_penalty = st.slider(
                    "Penalty ($)",
                    min_value=min_penalty,
                    max_value=max_penalty,
                    value=(min_penalty, max_penalty),
                    step=1.0
                )
            
            with col4:
                compliance_options = ["All", "Compliant", "Non-Compliant"]
                selected_compliance = st.multiselect("Compliance Status", options=compliance_options, default=compliance_options)
        
        # Apply Filters to SLAs
        filtered_slas = df_slas.copy()
        if selected_name:
            filtered_slas = filtered_slas[filtered_slas['name'].isin(selected_name)]
        filtered_slas = filtered_slas[
            (filtered_slas['max_hours'] >= selected_hours[0]) & 
            (filtered_slas['max_hours'] <= selected_hours[1])
        ]
        filtered_slas = filtered_slas[
            (filtered_slas['penalty'] >= selected_penalty[0]) & 
            (filtered_slas['penalty'] <= selected_penalty[1])
        ]
        
        # Filter Deliveries based on SLA names and compliance
        filtered_deliveries = df_deliveries.copy() if not df_deliveries.empty else pd.DataFrame()
        if not filtered_deliveries.empty and 'sla_type' in filtered_deliveries.columns:
            filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_type'].isin(filtered_slas['name'])]
            if "All" not in selected_compliance:
                if "Compliant" in selected_compliance and "Non-Compliant" not in selected_compliance:
                    filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_compliance'] == 1]
                elif "Non-Compliant" in selected_compliance and "Compliant" not in selected_compliance:
                    filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_compliance'] == 0]
                elif selected_compliance:
                    filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_compliance'].isin([1 if c == "Compliant" else 0 for c in selected_compliance])]
        
        # Display Filtered Table
        desired_columns = ["id", "name", "max_hours", "penalty"]
        available_columns = [col for col in desired_columns if col in filtered_slas.columns]
        st.dataframe(
            filtered_slas[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("SLA Insights")
        
        # Parallel Coordinates Plot (SLA Attributes)
        fig_parallel = px.parallel_coordinates(
            filtered_slas,
            dimensions=['max_hours', 'penalty', 'id'],
            title="SLA Attributes Comparison",
            labels={'max_hours': 'Max Hours', 'penalty': 'Penalty ($)', 'id': 'SLA ID'}
        )
        fig_parallel.update_layout(height=400)
        st.plotly_chart(fig_parallel, use_container_width=True)
        
        # Bubble Chart (Max Hours vs. Penalty)
        if not filtered_deliveries.empty and 'sla_type' in filtered_deliveries.columns:
            delivery_counts = filtered_deliveries.groupby('sla_type').size().reset_index(name='delivery_count')
            bubble_df = filtered_slas.merge(delivery_counts, left_on='name', right_on='sla_type', how='left').fillna({'delivery_count': 0})
        else:
            bubble_df = filtered_slas.assign(delivery_count=0)
        fig_bubble = px.scatter(
            bubble_df,
            x='max_hours',
            y='penalty',
            size='delivery_count',
            hover_data=['name'],
            title="Max Hours vs. Penalty (Bubble Size: Delivery Count)",
            labels={'max_hours': 'Max Hours', 'penalty': 'Penalty ($)'}
        )
        fig_bubble.update_layout(height=400)
        st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Sunburst Chart (Compliance by SLA)
        if not filtered_deliveries.empty and 'sla_type' in filtered_deliveries.columns and 'sla_compliance' in filtered_deliveries.columns:
            filtered_deliveries['compliance_label'] = filtered_deliveries['sla_compliance'].map({1: 'Compliant', 0: 'Non-Compliant'})
            sunburst_data = filtered_deliveries.groupby(['sla_type', 'compliance_label']).size().reset_index(name='count')
            sunburst_data = sunburst_data[sunburst_data['sla_type'].isin(filtered_slas['name'])]
            fig_sunburst = px.sunburst(
                sunburst_data,
                path=['sla_type', 'compliance_label'],
                values='count',
                title="Compliance by SLA",
                labels={'sla_type': 'SLA Name', 'compliance_label': 'Compliance'}
            )
            fig_sunburst.update_layout(height=400)
            st.plotly_chart(fig_sunburst, use_container_width=True)
        else:
            st.warning("No delivery data available for compliance visualization.")
    else:
        st.warning("No SLA data available. Check FastAPI logs and API response.")

# Traffic Section
elif section == "Traffic":
    st.header("Traffic")
    traffic = fetch_data("traffic")
    df_traffic = pd.DataFrame(traffic)
    
    if not df_traffic.empty:
        # Convert datetime fields
        df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp']).dt.date
        
        # KPI Cards
        st.subheader("Traffic KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_traffic_index = df_traffic['traffic_index'].mean()
            st.metric("Avg Traffic Index", f"{avg_traffic_index:.1f}", delta=None)
        with col2:
            avg_delay = df_traffic['delay_minutes'].mean()
            st.metric("Avg Delay (min)", f"{avg_delay:.1f}", delta=None)
        with col3:
            high_severity_rate = (len(df_traffic[df_traffic['severity'].isin(['High', 'Extreme'])]) / len(df_traffic)) * 100
            st.metric("High Severity Events (%)", f"{high_severity_rate:.1f}%", delta=None)
        with col4:
            high_traffic_locations = len(df_traffic[df_traffic['traffic_index'] > 75]['location'].unique())
            st.metric("High Traffic Locations", f"{high_traffic_locations}", delta=None)
        
        # Filters
        with st.expander("Filter Traffic", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                location_options = sorted(df_traffic['location'].unique())
                selected_location = st.multiselect("Location", options=location_options, default=location_options)
            
            with col2:
                min_date = df_traffic['timestamp'].min()
                max_date = df_traffic['timestamp'].max()
                if pd.isna(min_date) or pd.isna(max_date):
                    st.warning("Invalid timestamp range. Showing all dates.")
                    start_date, end_date = None, None
                else:
                    selected_dates = st.date_input(
                        "Timestamp Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                        start_date, end_date = selected_dates
                    else:
                        start_date = end_date = selected_dates
            
            with col3:
                severity_options = sorted(df_traffic['severity'].unique())
                selected_severity = st.multiselect("Severity", options=severity_options, default=severity_options)
            
            with col4:
                min_index = float(df_traffic['traffic_index'].min())
                max_index = float(df_traffic['traffic_index'].max())
                selected_index = st.slider(
                    "Traffic Index",
                    min_value=min_index,
                    max_value=max_index,
                    value=(min_index, max_index),
                    step=0.1
                )
        
        # Apply Filters
        filtered_df = df_traffic.copy()
        if selected_location:
            filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]
        if start_date is not None and end_date is not None:
            filtered_df = filtered_df[
                (filtered_df['timestamp'] >= start_date) & 
                (filtered_df['timestamp'] <= end_date)
            ]
        if selected_severity:
            filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
        filtered_df = filtered_df[
            (filtered_df['traffic_index'] >= selected_index[0]) & 
            (filtered_df['traffic_index'] <= selected_index[1])
        ]
        
        # Display Filtered Table
        desired_columns = ["id", "location", "timestamp", "traffic_index", "delay_minutes", "severity"]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        st.subheader("Traffic Insights")
        
        # Area Chart (Traffic Index Over Time)
        traffic_trends = filtered_df.groupby('timestamp')['traffic_index'].mean().reset_index()
        fig_area = px.area(
            traffic_trends,
            x='timestamp',
            y='traffic_index',
            title="Traffic Index Over Time",
            labels={'timestamp': 'Date', 'traffic_index': 'Traffic Index'}
        )
        fig_area.update_layout(height=400)
        st.plotly_chart(fig_area, use_container_width=True)
        
        # Treemap (Delays by Location and Severity)
        treemap_data = filtered_df.groupby(['location', 'severity'])['delay_minutes'].sum().reset_index()
        fig_treemap = px.treemap(
            treemap_data,
            path=['location', 'severity'],
            values='delay_minutes',
            title="Delays by Location and Severity",
            labels={'delay_minutes': 'Total Delay (min)'}
        )
        fig_treemap.update_layout(height=400)
        st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Density Heatmap (Traffic Index vs. Delay Minutes)
        fig_density = px.density_heatmap(
            filtered_df,
            x='traffic_index',
            y='delay_minutes',
            title="Traffic Index vs. Delay Minutes",
            labels={'traffic_index': 'Traffic Index', 'delay_minutes': 'Delay (min)'},
            color_continuous_scale='Viridis'
        )
        fig_density.update_layout(height=400)
        st.plotly_chart(fig_density, use_container_width=True)
    else:
        st.warning("No traffic data available. Check FastAPI logs and API response.")

# Metrics Section
elif section == "Metrics":
    st.header("Metrics")
    
    # Fetch data from multiple endpoints
    deliveries = fetch_data("deliveries")
    vehicles = fetch_data("vehicles")
    drivers = fetch_data("drivers")
    maintenance = fetch_data("maintenance")
    traffic = fetch_data("traffic")
    slas = fetch_data("slas")
    
    df_deliveries = pd.DataFrame(deliveries)
    df_vehicles = pd.DataFrame(vehicles)
    df_drivers = pd.DataFrame(drivers)
    df_maintenance = pd.DataFrame(maintenance)
    df_traffic = pd.DataFrame(traffic)
    df_slas = pd.DataFrame(slas)
    
    if not (df_deliveries.empty or df_vehicles.empty):
        # Convert datetime fields
        if not df_deliveries.empty:
            df_deliveries['date'] = pd.to_datetime(df_deliveries['date']).dt.date
        if not df_traffic.empty:
            df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp']).dt.date
        
        # KPI Cards
        st.subheader("Fleet Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sla_rate = df_deliveries['sla_compliance'].mean() if 'sla_compliance' in df_deliveries.columns else 0
            st.metric("SLA Compliance Rate (%)", f"{sla_rate:.2f}%", delta=None)
        with col2:
            fuel_eff = df_vehicles['fuel_efficiency'].mean() if 'fuel_efficiency' in df_vehicles.columns else 0
            st.metric("Avg Fuel Efficiency (km/L)", f"{fuel_eff:.1f}", delta=None)
        with col3:
            total_delay = (df_deliveries['delay_minutes'].sum() if 'delay_minutes' in df_deliveries.columns else 0) + \
                         (df_traffic['delay_minutes'].sum() if not df_traffic.empty and 'delay_minutes' in df_traffic.columns else 0)
            st.metric("Total Delay (min)", f"{total_delay:.1f}", delta=None)
        with col4:
            maint_cost = df_maintenance['cost'].sum() / df_maintenance['vehicle_id'].nunique() if not df_maintenance.empty and df_maintenance['vehicle_id'].nunique() > 0 else 0
            st.metric("Maint Cost/Vehicle ($)", f"{maint_cost:.2f}", delta=None)
        
        # Filters
        with st.expander("Filter Metrics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if not df_deliveries.empty:
                    min_date = min(df_deliveries['date'].min(), df_traffic['timestamp'].min() if not df_traffic.empty else df_deliveries['date'].max())
                    max_date = max(df_deliveries['date'].max(), df_traffic['timestamp'].max() if not df_traffic.empty else df_deliveries['date'].min())
                    if pd.isna(min_date) or pd.isna(max_date):
                        st.warning("Invalid date range. Showing all dates.")
                        start_date, end_date = None, None
                    else:
                        selected_dates = st.date_input(
                            "Date Range",
                            value=(min_date, max_date),
                            min_value=min_date,
                            max_value=max_date
                        )
                        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                            start_date, end_date = selected_dates
                        else:
                            start_date = end_date = selected_dates
                else:
                    start_date, end_date = None, None
            
            with col2:
                sla_options = sorted(df_deliveries['sla_type'].unique()) if 'sla_type' in df_deliveries.columns else []
                selected_sla = st.multiselect("SLA Type", options=sla_options, default=sla_options)
            
            with col3:
                driver_status_options = sorted(df_drivers['status'].unique()) if not df_drivers.empty else []
                selected_driver_status = st.multiselect("Driver Status", options=driver_status_options, default=driver_status_options)
            
            with col4:
                vehicle_status_options = sorted(df_vehicles['status'].unique()) if not df_vehicles.empty else []
                selected_vehicle_status = st.multiselect("Vehicle Status", options=vehicle_status_options, default=vehicle_status_options)
        
        # Apply Filters
        filtered_deliveries = df_deliveries.copy()
        filtered_vehicles = df_vehicles.copy()
        filtered_drivers = df_drivers.copy()
        filtered_maintenance = df_maintenance.copy()
        filtered_traffic = df_traffic.copy()
        
        if start_date is not None and end_date is not None:
            if not filtered_deliveries.empty:
                filtered_deliveries = filtered_deliveries[
                    (filtered_deliveries['date'] >= start_date) & 
                    (filtered_deliveries['date'] <= end_date)
                ]
            if not filtered_traffic.empty:
                filtered_traffic = filtered_traffic[
                    (filtered_traffic['timestamp'] >= start_date) & 
                    (filtered_traffic['timestamp'] <= end_date)
                ]
        if selected_sla and not filtered_deliveries.empty:
            filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_type'].isin(selected_sla)]
        if selected_driver_status and not filtered_deliveries.empty and not filtered_drivers.empty:
            filtered_deliveries = filtered_deliveries[filtered_deliveries['driver_id'].isin(
                filtered_drivers[filtered_drivers['status'].isin(selected_driver_status)]['id']
            )]
        if selected_vehicle_status and not filtered_deliveries.empty and not filtered_vehicles.empty:
            filtered_deliveries = filtered_deliveries[filtered_deliveries['vehicle_id'].isin(
                filtered_vehicles[filtered_vehicles['status'].isin(selected_vehicle_status)]['id']
            )]
            filtered_vehicles = filtered_vehicles[filtered_vehicles['status'].isin(selected_vehicle_status)]
        
        # Visualizations
        st.subheader("Fleet Insights")
        
        # Gauge Chart (SLA Compliance Rate)
        if not filtered_deliveries.empty and 'sla_compliance' in filtered_deliveries.columns:
            sla_rate = filtered_deliveries['sla_compliance'].mean()
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sla_rate,
                title={'text': "SLA Compliance Rate (%)"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}, 'threshold': {
                    'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': sla_rate}}
            ))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Radar Chart (Driver Performance Metrics)
        if not filtered_drivers.empty:
            driver_metrics = filtered_drivers.groupby('status').agg({
                'punctuality_score': 'mean',
                'total_deliveries': 'mean',
                'incident_count': 'mean'
            }).reset_index()
            fig_radar = go.Figure()
            for status in driver_metrics['status']:
                metrics = driver_metrics[driver_metrics['status'] == status]
                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        metrics['punctuality_score'].iloc[0] / 100,  # Normalize to 0-1
                        metrics['total_deliveries'].iloc[0] / driver_metrics['total_deliveries'].max(),
                        metrics['incident_count'].iloc[0] / (driver_metrics['incident_count'].max() + 1)
                    ],
                    theta=['Punctuality', 'Deliveries', 'Incidents'],
                    fill='toself',
                    name=status
                ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Driver Performance by Status",
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Waterfall Chart (Cost Breakdown)
        if not (filtered_deliveries.empty or filtered_maintenance.empty or df_slas.empty):
            fuel_cost = filtered_deliveries['fuel_consumed'].sum() * 1.5 if 'fuel_consumed' in filtered_deliveries.columns else 0  # Assume $1.5/L
            maint_cost = filtered_maintenance['cost'].sum() if 'cost' in filtered_maintenance.columns else 0
            penalty_cost = 0
            if (
                'sla_type' in filtered_deliveries.columns and
                'sla_compliance' in filtered_deliveries.columns and
                'name' in df_slas.columns and
                'penalty' in df_slas.columns
            ):
                non_compliant = filtered_deliveries[filtered_deliveries['sla_compliance'] == 0]
                if not non_compliant.empty:
                    merged = non_compliant.merge(df_slas[['name', 'penalty']], left_on='sla_type', right_on='name', how='left')
                    penalty_cost = merged['penalty'].fillna(0).sum()
            total_cost = fuel_cost + maint_cost + penalty_cost

            fig_waterfall = go.Figure(go.Waterfall(
                name="Cost Breakdown",
                orientation="v",
                measure=["relative", "relative", "relative", "total"],
                x=["Fuel", "Maintenance", "Penalties", "Total"],
                y=[fuel_cost, maint_cost, penalty_cost, total_cost],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                text=[f"${fuel_cost:.2f}", f"${maint_cost:.2f}", f"${penalty_cost:.2f}", f"${total_cost:.2f}"]
            ))
            fig_waterfall.update_layout(title="Cost Breakdown ($)", height=400)
            st.plotly_chart(fig_waterfall, use_container_width=True)
else:
    st.warning("Insufficient data for cost breakdown.")