# GPS Location App

## Overview
The GPS Location App is a Python application designed to retrieve and display the current GPS location of the device. It provides a user-friendly interface built with Kivy, allowing users to easily access their location information.

## Features
- Real-time GPS location retrieval
- User-friendly interface
- Cross-platform support (Desktop and Android)
- Configuration options for customization

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gps-location-app.git
   ```
2. Navigate to the project directory:
   ```
   cd gps-location-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, use the following command:
- For Desktop:
  ```
  ./scripts/run_desktop.sh
  ```
- For Android:
  ```
  ./scripts/run_android.sh
  ```

## Configuration
Before running the application, ensure that you set up the necessary environment variables. You can use the `.env.example` file as a template for your environment variables.

## Testing
To run the unit tests for the GPS functionality, execute:
```
pytest tests/test_gps.py
```

## Documentation
For detailed usage instructions and features, refer to the `docs/usage.md` file.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.