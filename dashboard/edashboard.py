import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

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
    ["Delivery & Driver Performance", "Vehicle & Maintenance Management", "Route & External Impacts", "Summary Dashboard"]
)

# Delivery & Driver Performance Section
if section == "Delivery & Driver Performance":
    st.header("Delivery & Driver Performance")
    
    # Fetch data
    deliveries = fetch_data("deliveries")
    drivers = fetch_data("drivers")
    slas = fetch_data("slas")
    
    df_deliveries = pd.DataFrame(deliveries)
    df_drivers = pd.DataFrame(drivers)
    df_slas = pd.DataFrame(slas)
    
    if not (df_deliveries.empty or df_drivers.empty or df_slas.empty):
        # Data preprocessing
        df_deliveries['scheduled_time'] = pd.to_datetime(df_deliveries['scheduled_time'])
        df_deliveries['actual_time'] = pd.to_datetime(df_deliveries['actual_time'])
        df_deliveries['date'] = pd.to_datetime(df_deliveries['date']).dt.date
        df_drivers['joined_date'] = pd.to_datetime(df_drivers['joined_date']).dt.date
        df_drivers['training_completed'] = df_drivers['training_completed'].astype(bool)
        
        # Merge data
        merged_df = df_deliveries.merge(
            df_drivers[['id', 'punctuality_score', 'incident_count', 'training_completed', 'status']],
            left_on='driver_id', right_on='id', how='left', suffixes=('', '_driver')
        ).merge(
            df_slas[['name', 'max_hours', 'penalty']],
            left_on='sla_type', right_on='name', how='left'
        )
        
        # KPI Cards
        st.subheader("Performance KPIs")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            sla_rate = merged_df['sla_compliance'].mean() * 100
            st.metric("SLA Compliance Rate (%)", f"{sla_rate:.2f}%")
        with col2:
            on_time_rate = (len(merged_df[(merged_df['status'] == 'Delivered') & (merged_df['delay_minutes'] <= 0)]) / len(merged_df)) * 100
            st.metric("On-Time Delivery Rate (%)", f"{on_time_rate:.2f}%")
        with col3:
            avg_delay = merged_df['delay_minutes'].mean()
            st.metric("Avg Delay (min)", f"{avg_delay:.1f}")
        with col4:
            avg_punctuality = merged_df['punctuality_score'].mean()
            st.metric("Avg Punctuality Score", f"{avg_punctuality:.1f}")
        with col5:
            avg_incidents = merged_df['incident_count'].mean()
            st.metric("Avg Incidents/Driver", f"{avg_incidents:.2f}")
        with col6:
            training_rate = (merged_df['training_completed'].sum() / len(merged_df)) * 100
            st.metric("Training Completion Rate (%)", f"{training_rate:.1f}%")
        
        # Filters
        with st.expander("Filter Data", expanded=True):
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                status_options = sorted(merged_df['status'].unique())
                selected_status = st.multiselect("Delivery Status", status_options, default=status_options)
            with col2:
                sla_type_options = sorted(merged_df['sla_type'].unique())
                selected_sla_type = st.multiselect("SLA Type", sla_type_options, default=sla_type_options)
            with col3:
                min_date = merged_df['date'].min()
                max_date = merged_df['date'].max()
                selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                start_date, end_date = selected_dates if isinstance(selected_dates, tuple) and len(selected_dates) == 2 else (min_date, max_date)
            with col4:
                compliance_options = ["All", "Compliant", "Non-Compliant"]
                selected_compliance = st.selectbox("Compliance Status", compliance_options)
            with col5:
                min_punctuality = float(merged_df['punctuality_score'].min())
                max_punctuality = float(merged_df['punctuality_score'].max())
                selected_punctuality = st.slider("Punctuality Score", min_punctuality, max_punctuality, (min_punctuality, max_punctuality), step=0.1)
            with col6:
                training_options = [True, False]
                selected_training = st.multiselect("Training Completed", training_options, default=training_options)
        
        # Apply Filters
        filtered_df = merged_df.copy()
        if selected_status:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        if selected_sla_type:
            filtered_df = filtered_df[filtered_df['sla_type'].isin(selected_sla_type)]
        filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
        if selected_compliance != "All":
            filtered_df = filtered_df[filtered_df['sla_compliance'] == (1 if selected_compliance == "Compliant" else 0)]
        filtered_df = filtered_df[
            (filtered_df['punctuality_score'] >= selected_punctuality[0]) & 
            (filtered_df['punctuality_score'] <= selected_punctuality[1])
        ]
        if selected_training:
            filtered_df = filtered_df[filtered_df['training_completed'].isin(selected_training)]
        
        # Display Table
        desired_columns = [
            "id", "vehicle_id", "driver_id", "scheduled_time", "actual_time", "status", "sla_type",
            "delay_minutes", "sla_compliance", "punctuality_score", "incident_count", "training_completed"
        ]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(filtered_df[available_columns], use_container_width=True, height=400)
        
        # Visualizations
        st.subheader("Performance Insights")
        # Sankey Diagram
        sankey_data = filtered_df.groupby(['sla_type', 'sla_compliance']).size().reset_index(name='count')
        sankey_data['compliance_label'] = sankey_data['sla_compliance'].map({1: 'Compliant', 0: 'Non-Compliant'})
        labels = list(sankey_data['sla_type'].unique()) + list(sankey_data['compliance_label'].unique())
        source = [labels.index(sla) for sla in sankey_data['sla_type']]
        target = [labels.index(comp) for comp in sankey_data['compliance_label']]
        value = sankey_data['count']
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels),
            link=dict(source=source, target=target, value=value)
        )])
        fig_sankey.update_layout(title="Delivery Flow by SLA Type and Compliance", height=400)
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        # Box Plot
        fig_box = px.box(filtered_df, x='status', y='delay_minutes', color='status',
                        title="Delay Minutes by Delivery Status",
                        labels={'status': 'Status', 'delay_minutes': 'Delay (min)'})
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
        # Sunburst Chart
        filtered_df['compliance_label'] = filtered_df['sla_compliance'].map({1: 'Compliant', 0: 'Non-Compliant'})
        sunburst_data = filtered_df.groupby(['sla_type', 'compliance_label']).size().reset_index(name='count')
        fig_sunburst = px.sunburst(sunburst_data, path=['sla_type', 'compliance_label'], values='count',
                                  title="Compliance by SLA")
        fig_sunburst.update_layout(height=400)
        st.plotly_chart(fig_sunburst, use_container_width=True)
        
        # Radar Chart
        driver_metrics = filtered_df.groupby('status_driver').agg({
            'punctuality_score': 'mean', 'incident_count': 'mean'
        }).reset_index()
        fig_radar = go.Figure()
        for status in driver_metrics['status_driver']:
            metrics = driver_metrics[driver_metrics['status_driver'] == status]
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    metrics['punctuality_score'].iloc[0] / 100,
                    metrics['incident_count'].iloc[0] / (driver_metrics['incident_count'].max() + 1)
                ],
                theta=['Punctuality', 'Incidents'],
                fill='toself',
                name=status
            ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                               showlegend=True, title="Driver Performance by Status", height=400)
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("No data available for Delivery & Driver Performance.")

# Vehicle & Maintenance Management Section
elif section == "Vehicle & Maintenance Management":
    st.header("Vehicle & Maintenance Management")
    
    # Fetch data
    vehicles = fetch_data("vehicles")
    maintenance = fetch_data("maintenance")
    
    df_vehicles = pd.DataFrame(vehicles)
    df_maintenance = pd.DataFrame(maintenance)
    
    if not (df_vehicles.empty or df_maintenance.empty):
        # Data preprocessing
        df_vehicles['last_maintenance_date'] = pd.to_datetime(df_vehicles['last_maintenance_date']).dt.date
        df_maintenance['date'] = pd.to_datetime(df_maintenance['date']).dt.date
        
        # Rename 'id' to 'vehicle_id' in df_vehicles for consistency
        if 'id' in df_vehicles.columns and 'vehicle_id' not in df_vehicles.columns:
            df_vehicles = df_vehicles.rename(columns={'id': 'vehicle_id'})
        
        # Validate merge columns
        if 'vehicle_id' not in df_vehicles.columns or 'vehicle_id' not in df_maintenance.columns:
            st.error(f"Merge failed: 'vehicle_id' missing. "
                     f"Vehicle columns: {list(df_vehicles.columns)}, "
                     f"Maintenance columns: {list(df_maintenance.columns)}")
            st.stop()
        
        # Merge data
        try:
            merged_df = df_vehicles.merge(
                df_maintenance[['vehicle_id', 'date', 'cost', 'type', 'status']],
                on='vehicle_id', how='left'
            )
        except KeyError as e:
            st.error(f"Merge failed: {e}. Please check column names in API response.")
            st.stop()
        
        # KPI Cards
        st.subheader("Vehicle & Maintenance KPIs")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            fuel_eff = merged_df['fuel_efficiency'].mean() if 'fuel_efficiency' in merged_df.columns else 0
            st.metric("Avg Fuel Efficiency (km/L)", f"{fuel_eff:.1f}")
        with col2:
            idle_hours = merged_df['idle_hours'].mean() if 'idle_hours' in merged_df.columns else 0
            st.metric("Avg Idle Hours", f"{idle_hours:.1f}")
        with col3:
            overdue_maint = len(merged_df[
                (pd.Timestamp.now().normalize() - pd.to_datetime(merged_df['last_maintenance_date'])).dt.days > 180
            ].drop_duplicates('vehicle_id')) if 'last_maintenance_date' in merged_df.columns else 0
            st.metric("Vehicles Overdue Maintenance", f"{overdue_maint}")
        with col4:
            maint_cost = (merged_df['cost'].sum() / merged_df['vehicle_id'].nunique() 
                         if 'cost' in merged_df.columns and merged_df['vehicle_id'].nunique() > 0 else 0)
            st.metric("Maint Cost/Vehicle ($)", f"{maint_cost:.2f}")
        with col5:
            poor_battery = (len(merged_df[merged_df['battery_health'] < 70].drop_duplicates('vehicle_id')) / 
                           len(merged_df.drop_duplicates('vehicle_id')) * 100 
                           if 'battery_health' in merged_df.columns and not merged_df.empty else 0)
            st.metric("Poor Battery Health (%)", f"{poor_battery:.1f}%")
        
        # Filters
        with st.expander("Filter Data", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                status_options = sorted(merged_df['status'].unique()) if 'status' in merged_df.columns else []
                selected_status = st.multiselect("Vehicle Status", status_options, default=status_options)
            with col2:
                vehicle_options = sorted(merged_df['vehicle_id'].unique())
                selected_vehicle = st.multiselect("Vehicle ID", vehicle_options, default=vehicle_options)
            with col3:
                min_fuel_eff = float(merged_df['fuel_efficiency'].min()) if 'fuel_efficiency' in merged_df.columns else 0
                max_fuel_eff = float(merged_df['fuel_efficiency'].max()) if 'fuel_efficiency' in merged_df.columns else 0
                selected_fuel_eff = st.slider("Fuel Efficiency (km/L)", min_fuel_eff, max_fuel_eff, 
                                             (min_fuel_eff, max_fuel_eff), step=0.1)
            with col4:
                min_date = merged_df['last_maintenance_date'].min() if 'last_maintenance_date' in merged_df.columns else datetime.now().date()
                max_date = merged_df['last_maintenance_date'].max() if 'last_maintenance_date' in merged_df.columns else datetime.now().date()
                selected_dates = st.date_input("Maintenance Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                start_date, end_date = selected_dates if len(selected_dates) == 2 else (min_date, max_date)
            with col5:
                type_options = sorted(merged_df['type'].dropna().unique()) if 'type' in merged_df.columns else []
                selected_type = st.multiselect("Maintenance Type", type_options, default=type_options)
        
        # Apply Filters
        filtered_df = merged_df.copy()
        if selected_status and 'status' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['status'].isin(selected_status)]
        if selected_vehicle:
            filtered_df = filtered_df[filtered_df['vehicle_id'].isin(selected_vehicle)]
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
        if selected_type and 'type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['type'].isin(selected_type)]
        
        # Display Table
        desired_columns = [
            "vehicle_id", "model", "fuel_efficiency", "last_maintenance_date", "mileage",
            "idle_hours", "status", "cost", "type"
        ]
        available_columns = [col for col in desired_columns if col in filtered_df.columns]
        st.dataframe(filtered_df[available_columns], use_container_width=True, height=400)
        
        # Visualizations
        st.subheader("Vehicle & Maintenance Insights")
        # Bubble Chart
        if all(col in filtered_df.columns for col in ['mileage', 'fuel_efficiency', 'idle_hours', 'status']):
            fig_bubble = px.scatter(filtered_df, x='mileage', y='fuel_efficiency', size='idle_hours', color='status',
                                   hover_data=['vehicle_id'], title="Fuel Efficiency vs. Mileage",
                                   labels={'mileage': 'Mileage (km)', 'fuel_efficiency': 'Fuel Efficiency (km/L)'})
            fig_bubble.update_layout(height=400)
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Line Chart
        if 'last_maintenance_date' in filtered_df.columns and 'type' in filtered_df.columns:
            filtered_df['maintenance_age_days'] = [(datetime.now().date() - d).days if pd.notna(d) else 0 for d in filtered_df['last_maintenance_date']]
            fig_line = px.line(filtered_df, x='last_maintenance_date', y='maintenance_age_days', color='type',
                              title="Days Since Last Maintenance by Type",
                              labels={'last_maintenance_date': 'Maintenance Date', 'maintenance_age_days': 'Days'})
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Gantt Chart
        if all(col in filtered_df.columns for col in ['vehicle_id', 'date', 'status']):
            gantt_df = filtered_df[['vehicle_id', 'date', 'status']].copy()
            gantt_df['end_date'] = gantt_df['date']
            gantt_df['vehicle_id'] = gantt_df['vehicle_id'].astype(str)
            fig_gantt = px.timeline(gantt_df, x_start='date', x_end='end_date', y='vehicle_id', color='status',
                                   title="Maintenance Timeline by Vehicle")
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(height=400)
            st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.warning("No data available for Vehicle & Maintenance Management.")


# Route & External Impacts Section
elif section == "Route & External Impacts":
    st.header("Route & External Impacts")
    
    # Fetch data
    routes = fetch_data("routes")
    traffic = fetch_data("traffic")
    weather = fetch_data("weather")
    
    df_routes = pd.DataFrame(routes)
    df_traffic = pd.DataFrame(traffic)
    df_weather = pd.DataFrame(weather)
    
    if not (df_routes.empty or df_traffic.empty or df_weather.empty):
        # Data preprocessing
        df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp']).dt.date
        df_weather['timestamp'] = pd.to_datetime(df_weather['timestamp']).dt.date
        
        # KPI Cards
        st.subheader("Route & External KPIs")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_distance = df_routes['distance_km'].mean()
            st.metric("Avg Route Distance (km)", f"{avg_distance:.1f}")
        with col2:
            avg_delay = df_traffic['delay_minutes'].mean()
            st.metric("Avg Traffic Delay (min)", f"{avg_delay:.1f}")
        with col3:
            high_severity = (len(df_traffic[df_traffic['severity'].isin(['High', 'Extreme'])]) + 
                            len(df_weather[df_weather['severity'].isin(['Severe', 'Extreme'])])) / (len(df_traffic) + len(df_weather)) * 100
            st.metric("High Severity Events (%)", f"{high_severity:.1f}%")
        with col4:
            high_traffic_locs = len(df_traffic[df_traffic['traffic_index'] > 75]['location'].unique())
            st.metric("High Traffic Locations", f"{high_traffic_locs}")
        
        # Filters
        with st.expander("Filter Data", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                location_options = sorted(set(df_traffic['location'].unique()).union(df_weather['location'].unique()))
                selected_location = st.multiselect("Location", location_options, default=location_options)
            with col2:
                min_date = min(df_traffic['timestamp'].min(), df_weather['timestamp'].min())
                max_date = max(df_traffic['timestamp'].max(), df_weather['timestamp'].max())
                selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                start_date, end_date = selected_dates if len(selected_dates) == 2 else (min_date, max_date)
            with col3:
                severity_options = sorted(set(df_traffic['severity'].unique()).union(df_weather['severity'].unique()))
                selected_severity = st.multiselect("Severity", severity_options, default=severity_options)
            with col4:
                traffic_options = sorted(df_routes['typical_traffic'].unique())
                selected_traffic = st.multiselect("Traffic Level", traffic_options, default=traffic_options)
            with col5:
                min_distance = float(df_routes['distance_km'].min())
                max_distance = float(df_routes['distance_km'].max())
                selected_distance = st.slider("Route Distance (km)", min_distance, max_distance, (min_distance, max_distance), step=0.1)
        
        # Apply Filters
        filtered_traffic = df_traffic.copy()
        filtered_weather = df_weather.copy()
        filtered_routes = df_routes.copy()
        if selected_location:
            filtered_traffic = filtered_traffic[filtered_traffic['location'].isin(selected_location)]
            filtered_weather = filtered_weather[filtered_weather['location'].isin(selected_location)]
        filtered_traffic = filtered_traffic[(filtered_traffic['timestamp'] >= start_date) & (filtered_traffic['timestamp'] <= end_date)]
        filtered_weather = filtered_weather[(filtered_weather['timestamp'] >= start_date) & (filtered_weather['timestamp'] <= end_date)]
        if selected_severity:
            filtered_traffic = filtered_traffic[filtered_traffic['severity'].isin(selected_severity)]
            filtered_weather = filtered_weather[filtered_weather['severity'].isin(selected_severity)]
        if selected_traffic:
            filtered_routes = filtered_routes[filtered_routes['typical_traffic'].isin(selected_traffic)]
        filtered_routes = filtered_routes[
            (filtered_routes['distance_km'] >= selected_distance[0]) & 
            (filtered_routes['distance_km'] <= selected_distance[1])
        ]
        
        # Display Table
        merged_df = filtered_routes.copy()
        desired_columns = ["id", "route_name", "distance_km", "typical_traffic"]
        available_columns = [col for col in desired_columns if col in merged_df.columns]
        st.dataframe(merged_df[available_columns], use_container_width=True, height=400)
        
        # Visualizations
        st.subheader("Route & External Insights")
        # Scatter Map
        map_data = []
        for _, row in filtered_routes.iterrows():
            map_data.extend([
                {'lat': row['origin_lat'], 'lng': row['origin_lng'], 'type': 'Origin', 'route': row['route_name']},
                {'lat': row['dest_lat'], 'lng': row['dest_lng'], 'type': 'Destination', 'route': row['route_name']}
            ])
        map_df = pd.DataFrame(map_data)
        fig_map = px.scatter_mapbox(map_df, lat='lat', lon='lng', color='type', hover_data=['route'],
                                   title="Route Origins and Destinations", mapbox_style="open-street-map", zoom=10)
        fig_map.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Treemap
        treemap_data = filtered_traffic.groupby(['location', 'severity'])['delay_minutes'].sum().reset_index()
        fig_treemap = px.treemap(treemap_data, path=['location', 'severity'], values='delay_minutes',
                                title="Delays by Location and Severity")
        fig_treemap.update_layout(height=400)
        st.plotly_chart(fig_treemap, use_container_width=True)
        
        # Violin Plot
        fig_violin = px.violin(filtered_routes, x='typical_traffic', y='distance_km', color='typical_traffic',
                              title="Route Distance by Traffic Level",
                              labels={'typical_traffic': 'Traffic Level', 'distance_km': 'Distance (km)'})
        fig_violin.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)
    else:
        st.warning("No data available for Route & External Impacts.")

# Summary Dashboard Section
elif section == "Summary Dashboard":
    st.header("Summary Dashboard")
    
    # Fetch data
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
    
    if not (df_deliveries.empty or df_vehicles.empty or df_drivers.empty):
        # Data preprocessing
        df_deliveries['date'] = pd.to_datetime(df_deliveries['date']).dt.date
        df_traffic['timestamp'] = pd.to_datetime(df_traffic['timestamp']).dt.date
        
        # KPI Cards
        st.subheader("Fleet Performance Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            sla_rate = df_deliveries['sla_compliance'].mean()
            st.metric("SLA Compliance Rate", f"{sla_rate:.2f}%")
        with col2:
            fuel_eff = df_vehicles['fuel_efficiency'].mean()
            st.metric("Avg Fuel Efficiency (km/L)", f"{fuel_eff:.1f}")
        with col3:
            total_delay = df_deliveries['delay_minutes'].sum() + df_traffic['delay_minutes'].sum()
            st.metric("Total Delay (min)", f"{total_delay:.1f}")
        with col4:
            maint_cost = df_maintenance['cost'].sum() / df_maintenance['vehicle_id'].nunique()
            st.metric("Maint Cost/Vehicle ($)", f"{maint_cost:.2f}")
        with col5:
            incident_rate = df_drivers['incident_count'].mean()
            st.metric("Driver Incident Rate", f"{incident_rate:.2f}")
        
        # Filters
        with st.expander("Filter Data", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                min_date = min(df_deliveries['date'].min(), df_traffic['timestamp'].min())
                max_date = max(df_deliveries['date'].max(), df_traffic['timestamp'].max())
                selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                start_date, end_date = selected_dates if len(selected_dates) == 2 else (min_date, max_date)
            with col2:
                sla_options = sorted(df_deliveries['sla_type'].unique())
                selected_sla = st.multiselect("SLA Type", sla_options, default=sla_options)
            with col3:
                status_options = sorted(set(df_vehicles['status'].unique()).union(df_drivers['status'].unique()))
                selected_status = st.multiselect("Status", status_options, default=status_options)
        
        # Apply Filters
        filtered_deliveries = df_deliveries[(df_deliveries['date'] >= start_date) & (df_deliveries['date'] <= end_date)]
        filtered_traffic = df_traffic[(df_traffic['timestamp'] >= start_date) & (df_traffic['timestamp'] <= end_date)]
        if selected_sla:
            filtered_deliveries = filtered_deliveries[filtered_deliveries['sla_type'].isin(selected_sla)]
        if selected_status:
            filtered_deliveries = filtered_deliveries[
                filtered_deliveries['driver_id'].isin(df_drivers[df_drivers['status'].isin(selected_status)]['id']) &
                filtered_deliveries['vehicle_id'].isin(df_vehicles[df_vehicles['status'].isin(selected_status)]['id'])
            ]
        
        # Visualizations
        st.subheader("Fleet Insights")
        # Waterfall Chart
        fuel_cost = filtered_deliveries['fuel_consumed'].sum() * 1.5
        maint_cost = df_maintenance['cost'].sum()
        penalty_cost = filtered_deliveries[filtered_deliveries['sla_compliance'] == 0].merge(
            df_slas[['name', 'penalty']], left_on='sla_type', right_on='name', how='left'
        )['penalty'].fillna(0).sum()
        total_cost = fuel_cost + maint_cost + penalty_cost
        fig_waterfall = go.Figure(go.Waterfall(
            name="Cost Breakdown", orientation="v", measure=["relative", "relative", "relative", "total"],
            x=["Fuel", "Maintenance", "Penalties", "Total"], y=[fuel_cost, maint_cost, penalty_cost, total_cost],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            text=[f"${fuel_cost:.2f}", f"${maint_cost:.2f}", f"${penalty_cost:.2f}", f"${total_cost:.2f}"]
        ))
        fig_waterfall.update_layout(title="Cost Breakdown ($)", height=400)
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
        # Gauge Chart
        sla_rate = filtered_deliveries['sla_compliance'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=sla_rate, title={'text': "SLA Compliance Rate (%)"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}, 'threshold': {
                'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': sla_rate}}
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.warning("No data available for Summary Dashboard.")