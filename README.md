# Azure Alerts Visualization and Analysis

This project provides a Flask-based web application that interacts with Azure's monitoring data to visualize and analyze alert metrics. The application allows you to view fired, resolved, and unresolved alerts in your Azure subscription over a given time period, along with other insights like alert distribution by severity, resource, and time.

## Features

- **Azure Authentication**: Logs in to Azure using the Azure CLI (`az login`).
- **Custom Time Range**: Allows users to specify a start and end time for the alerts they wish to retrieve.
- **Alert Data Visualization**: Generates interactive visualizations using Plotly for various alert metrics.
- **Interactive Dashboards**: Displays charts for fired, resolved, and unresolved alerts, as well as hourly and severity-based distributions.

## Requirements

This project uses the following technologies:

- **Python 3.11+** (ensure Python 3.11 is installed on your system)
- **Flask**: Web framework for serving the application.
- **Pandas**: Used for data manipulation and analysis.
- **Plotly**: For interactive data visualizations.
- **Azure CLI**: Required to run Azure commands (`az login`, `az graph query`).
  
### System Requirements

- **Azure CLI**: You must have the Azure CLI installed and be logged in to your Azure account to query Azure Graph.
- **Python 3.11+**: Make sure Python 3.11 or higher is installed.
- **Pip**: Python package manager for installing dependencies.

## Installation

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd <project-directory>
```

### Step 2: Set Up a Virtual Environment

It is recommended to create a virtual environment for managing your project dependencies:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# For Linux/macOS
source venv/bin/activate
# For Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

Install the required packages by running:

```bash
pip install -r requirements.txt
```

### Step 4: Install Azure CLI

If you don't have Azure CLI installed, you can install it using the following commands:

#### For macOS:
```bash
brew install azure-cli
```

#### For Windows:
Download the installer from the [Azure CLI download page](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) and follow the instructions.

#### For Linux:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

After installation, you can log in to Azure using:

```bash
az login
```

Follow the instructions in your browser to complete the login process.

### Step 5: Run the Flask Application

Once the dependencies are installed and Azure CLI is set up, you can run the Flask application:

```bash
python app.py
```

This will start the Flask development server, and you can open your browser and navigate to `http://127.0.0.1:5000/` to access the application.

## Usage

### 1. **Login to Azure**
   - When you first navigate to the application, it will prompt you to log in using the Azure CLI (`az login`).
   
### 2. **Enter Time Range**
   - In the web interface, you'll be asked to enter a start and end time for the alert data you want to retrieve.
   - The time format should be in `YYYY-MM-DDTHH:MM:SS` format (e.g., `2023-01-01T00:00:00`).

### 3. **View Alerts**
   - Once you've entered the time range, the app will query Azure Graph for alerts that meet the criteria.
   - The results will be displayed as interactive plots such as:
     - **Fired Alerts by Subscription**
     - **Resolved Alerts by Subscription**
     - **Alerts by Severity**
     - **Alerts by Resource**
     - **Unresolved Alerts**
     - **Alerts by Hour**
     - **Fired, Resolved, and Unresolved Alerts by Hour for all the subscriptions under your azure account**
   - These visualizations help you understand the alert patterns across different Azure subscriptions, resources, and times.

### 4. **Interactive Dashboards**
   - You can interact with the visualizations in the browser by zooming in, hovering over data points, and viewing tooltips with additional details.

## Folder Structure

```plaintext
/
├── app.py               # The main Flask application
├── requirements.txt     # List of Python dependencies
├── templates/
│   ├── index.html       # The homepage template
│   ├── azure.html       # The template for displaying alert visualizations
└── static/              # Static files like CSS, JavaScript, and images
```

## Troubleshooting

### Common Errors:

1. **UnicodeDecodeError**: This can happen if there are encoding issues when processing the output from the Azure CLI. The `data = result.stdout.encode('utf-8', 'ignore').decode('utf-8', 'ignore')` line in the code helps to handle these issues by ignoring characters that can't be decoded. If you still encounter issues, check if there is any malformed data from the Azure CLI query.
   
2. **Azure CLI Authentication**: If the `az login` command fails, make sure you're properly logged into Azure using the `az login` command in your terminal.

3. **Missing Data**: If you don't see any data, ensure that the time range you specified has data for the specified alerts in your Azure account.

4. **Error: `No data found within the provided time range.`**: This message appears if no alerts exist within the provided start and end times. Double-check your date-time format.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

