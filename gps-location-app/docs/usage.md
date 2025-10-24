# Usage Instructions for GPS Location App

## Overview
The GPS Location App allows users to retrieve their current GPS location using their device's GPS hardware. This document provides instructions on how to set up and use the application.

## Setup Instructions

1. **Clone the Repository**
   Clone the repository to your local machine using the following command:
   ```
   git clone https://github.com/yourusername/gps-location-app.git
   ```

2. **Navigate to the Project Directory**
   Change into the project directory:
   ```
   cd gps-location-app
   ```

3. **Install Dependencies**
   Install the required Python packages using pip:
   ```
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the root directory and add any necessary environment variables. You can use the `.env.example` file as a reference.

## Running the Application

### Desktop
To run the application on a desktop environment, execute the following script:
```
bash scripts/run_desktop.sh
```

### Android
To run the application on an Android device, use the following command:
```
bash scripts/run_android.sh
```

## Features
- **Real-time GPS Location Retrieval**: The app continuously fetches the current GPS location.
- **User Interface**: A simple and intuitive UI built with Kivy.
- **Background Location Updates**: The app can run in the background to provide location updates.

## Usage
1. Launch the application using the appropriate script for your platform.
2. Allow the app to access your device's location services when prompted.
3. The current GPS coordinates will be displayed on the screen.

## Troubleshooting
- Ensure that location services are enabled on your device.
- Check that the app has the necessary permissions to access GPS.
- If you encounter any issues, refer to the logs for error messages.

For further assistance, please refer to the project's README.md or contact the project maintainers.