import subprocess
import json
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['GET', 'POST'])
def show_alerts():
    skip = 0
    first = 100
    startDateTime = request.form['start_time']
    endDateTime = request.form['end_time']
    
    try:
        subprocess.run(['az', 'login'], check=True)
        print("Azure login successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error logging in to Azure: {e}")
        return
    
    all_alerts_data = [] 

    while True:
        query = (
            "alertsmanagementresources "
            "| where type == 'microsoft.alertsmanagement/alerts' "
            "| extend severity = tostring(properties['essentials']['severity']) "
            "| where properties['essentials']['monitorCondition'] in~ ('Fired','Resolved') "
            "| where properties['essentials']['startDateTime'] >= datetime({}) and properties['essentials']['startDateTime'] <= datetime({}) "
            "| project id, severity, name, essentials = properties['essentials'], subscriptionId "
            "| order by todatetime(essentials['startDateTime']) desc"
        ).format(startDateTime, endDateTime)

        try:
            result = subprocess.run(
                ['az', 'graph', 'query', '-q', query, '--first', str(first), '--skip', str(skip)],
                capture_output=True,
                text=True,
                check=True
            )
            data = result.stdout.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        except subprocess.CalledProcessError as e:
            print(f"Error running the query: {e}")
            break

        data = result.stdout
        if not data:
            print("No data found within the provided time range.")
            break
        
        try:
            alerts_data = json.loads(data)['data']
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            break
        formatted_data = [
            [
                alert['name'],
                alert['severity'],
                alert.get('resourceGroup', ''),
                alert['essentials']['targetResourceType'],
                alert['essentials']['monitorCondition'],
                alert['essentials'].get('description', ''),
                alert['essentials']['monitorService'],
                alert['essentials']['signalType'],
                alert['essentials']['startDateTime'],
                alert['essentials']['lastModifiedDateTime'],
                alert['subscriptionId'],
                alert['essentials']['targetResourceGroup'],
                alert['essentials']['actionStatus']['isSuppressed']
            ]
            for alert in alerts_data
        ]
        
        all_alerts_data.extend(formatted_data) 

        skip += first
        if len(formatted_data) < first:
            print("Pagination complete. No more data.")
            break
    df = pd.DataFrame(all_alerts_data, columns=[
        'Name', 'Severity', 'Affected resource', 'Target resource type', 
        'Alert condition', 'User response', 'Monitor service', 'Signal type', 
        'Fire time', 'Last modified time', 'Subscription', 'Target resource group', 
        'Suppression status'
    ])
    df['Fire time'] = pd.to_datetime(df['Fire time'], errors='coerce')
    
    plots = {}
    subscriptions = df['Subscription'].unique()
    
    for subscription in subscriptions:
        subscription_data = df[df['Subscription'] == subscription]
        
        alerts_fired = subscription_data[subscription_data['Alert condition'] == 'Fired']
        alerts_resolved = subscription_data[subscription_data['Alert condition'] == 'Resolved']
        alerts_unresolved = alerts_fired[~alerts_fired['Name'].isin(alerts_resolved['Name'])]

        fired_by_name = alerts_fired['Name'].value_counts().reset_index(name='Count')
        fired_by_name.columns = ['Alert Name', 'Count']
        fig_fired = px.bar(fired_by_name, x='Alert Name', y='Count', title=f'Fired Alerts for {subscription}', labels={'Alert Name': 'Alert Name', 'Count': 'Number of Alerts'})
        fig_fired.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_fired = fig_fired.to_html()

        resolved_by_name = alerts_resolved['Name'].value_counts().reset_index(name='Count')
        resolved_by_name.columns = ['Alert Name', 'Count']
        fig_resolved = px.bar(resolved_by_name, x='Alert Name', y='Count', title=f'Resolved Alerts for {subscription}', labels={'Alert Name': 'Alert Name', 'Count': 'Number of Alerts'})
        fig_resolved.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_resolved = fig_resolved.to_html()

        unresolved_by_name = alerts_unresolved['Name'].value_counts().reset_index(name='Count')
        unresolved_by_name.columns = ['Alert Name', 'Count']
        fig_unresolved = px.bar(unresolved_by_name, x='Alert Name', y='Count', title=f'Unresolved Alerts for {subscription}', labels={'Alert Name': 'Alert Name', 'Count': 'Number of Alerts'})
        fig_unresolved.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_unresolved = fig_unresolved.to_html()

        fired_hourly = alerts_fired.groupby([alerts_fired['Fire time'].dt.hour, 'Name']).size().reset_index(name='Count')
        fig_fired_hourly = px.bar(fired_hourly, x='Fire time', y='Count', color='Name', barmode='stack', title=f'Fired Alerts by Hour for {subscription}', labels={'Fire time': 'Hour', 'Count': 'Number of Alerts'})
        fig_fired_hourly.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_fired_hourly = fig_fired_hourly.to_html()

        resolved_hourly = alerts_resolved.groupby([alerts_resolved['Fire time'].dt.hour, 'Name']).size().reset_index(name='Count')
        fig_resolved_hourly = px.bar(resolved_hourly, x='Fire time', y='Count', color='Name', barmode='stack', title=f'Resolved Alerts by Hour for {subscription}', labels={'Fire time': 'Hour', 'Count': 'Number of Alerts'})
        fig_resolved_hourly.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_resolved_hourly = fig_resolved_hourly.to_html()

        unresolved_hourly = alerts_unresolved.groupby([alerts_unresolved['Fire time'].dt.hour, 'Name']).size().reset_index(name='Count')
        fig_unresolved_hourly = px.bar(unresolved_hourly, x='Fire time', y='Count', color='Name', barmode='stack', title=f'Unresolved Alerts by Hour for {subscription}', labels={'Fire time': 'Hour', 'Count': 'Number of Alerts'})
        fig_unresolved_hourly.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        html_fig_unresolved_hourly = fig_unresolved_hourly.to_html()

        plots[subscription] = {
            'fired': html_fig_fired,
            'resolved': html_fig_resolved,
            'unresolved': html_fig_unresolved,
            'fired_hourly': html_fig_fired_hourly,
            'resolved_hourly': html_fig_resolved_hourly,
            'unresolved_hourly': html_fig_unresolved_hourly
        }

    alerts_by_hour = df.groupby(df['Fire time'].dt.hour).size().reset_index(name='Count')
    fig1 = px.bar(alerts_by_hour, x='Fire time', y='Count', title='Alerts by Hour', labels={'Fire time': 'Hour', 'Count': 'Number of Alerts'})
    fig1.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig1 = fig1.to_html()

    alerts_by_severity = df['Severity'].value_counts().reset_index(name='Count')
    fig2 = px.pie(alerts_by_severity, names='Severity', values='Count', title='Alerts by Severity')
    fig2.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig2 = fig2.to_html()

    alerts_by_resource = df['Affected resource'].value_counts().reset_index(name='Count')
    fig3 = px.bar(alerts_by_resource, x='Affected resource', y='Count', title='Alerts by Resource', labels={'Affected resource': 'Resource', 'Count': 'Number of Alerts'})
    fig3.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig3 = fig3.to_html()

    alerts_by_subscription = df['Subscription'].value_counts().reset_index(name='Count')
    fig4 = px.bar(alerts_by_subscription, x='Subscription', y='Count', title='Alerts by Subscription', labels={'Subscription Name': 'Subscription', 'Count': 'Number of Alerts'})
    fig4.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig4 = fig4.to_html()

    alert_types = df.groupby(['Subscription', 'Alert condition']).size().reset_index(name='Count')
    fig5 = px.bar(alert_types, x='Subscription', y='Count', color='Alert condition', barmode='group', title='Alert Types by Subscription')
    fig5.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig5 = fig5.to_html()

    alert_status = df['Alert condition'].value_counts().reset_index(name='Count')
    fig6 = px.pie(alert_status, names='Alert condition', values='Count', title='Fired vs Resolved Alerts')
    fig6.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')
    html_fig6 = fig6.to_html()
    return render_template(
        'azure.html',
        plots=plots,
        overall_plots=[html_fig1, html_fig2, html_fig3, html_fig4, html_fig5, html_fig6]
    )

if __name__ == '__main__':
    app.run(debug=True)

