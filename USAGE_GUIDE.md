# Arkansas Registry Processor - Usage Guide

## Overview
The Arkansas Registry Processor is a GUI application that automates searching names from Excel files against the Arkansas Sex Offender Registry website. It provides a user-friendly interface for non-technical staff to process large batches of names efficiently.

## For End Users (Non-Technical Staff)

### System Requirements
- Windows 10 or later
- Internet connection
- Chrome browser installed
- Excel files in .xlsx format

### Using the Application
1. **Launch**: Double-click `Arkansas_Registry_Processor.exe`
2. **Select File**: Click "Browse..." and select your Excel file
3. **Verify Format**: Ensure your Excel file has:
   - Column B: First Name
   - Column D: Last Name
   - Column G: Gender (male/female/unknown)
   - Data starting from row 4 (headers in row 3)
4. **Output Location**: Default saves to Desktop with timestamp, or click "Change..." to choose location
5. **Start Processing**: Click "Start Processing" and monitor progress
6. **View Results**: When complete, click "Open Results" to view the Excel file

### Understanding Results
The output Excel file contains:
- **First Name, Last Name, Gender**: Original data from input file
- **Result**: Either "no results found" (clear) or "warning" (match found)
- **Processed Date**: Timestamp of when the search was performed

### Troubleshooting
- **"Error initializing browser"**: Ensure Chrome browser is installed
- **"No valid data found"**: Check Excel file format and column layout
- **Processing stops**: Check internet connection, restart application if needed

## For IT/Technical Staff

### Development and Testing
```bash
# Test the GUI locally (Mac/Linux)
cd ar-registry-processor
python3 gui/test_gui.py

# Install dependencies
pip install -r requirements_gui.txt
```

### Building the Windows Executable
```bash
# From project root directory
python3 build_executable.py
```

This creates:
- `dist/Arkansas_Registry_Processor.exe` - The standalone executable
- `dist/README.txt` - User documentation

### Deployment
1. Copy the entire `dist/` folder to target Windows machine
2. Ensure Chrome browser is installed on target machine  
3. No Python installation required on target machine
4. Executable is self-contained with all dependencies

### Technical Architecture
- **GUI Framework**: tkinter (built-in to Python)
- **Web Automation**: Selenium with headless Chrome
- **Excel Processing**: openpyxl and pandas
- **Packaging**: PyInstaller for standalone executable
- **Threading**: Background processing prevents GUI freezing

### File Structure
```
gui/
├── main_app.py              # Main GUI application
├── registry_processor.py    # Core processing logic
└── test_gui.py             # Development test script

build_executable.py          # Packaging script
requirements_gui.txt         # Dependencies
```

### Customization
To modify the application:
1. Edit `gui/main_app.py` for UI changes
2. Edit `gui/registry_processor.py` for processing logic
3. Rebuild executable with `python3 build_executable.py`

### Error Handling
The application includes comprehensive error handling:
- Browser initialization failures
- Network connection issues
- Excel file format problems
- Individual search failures (continues processing)
- User cancellation support

### Performance Considerations
- Processing speed: ~1-2 names per minute (including delays)
- Memory usage: ~100-200MB during operation
- Executable size: ~50-100MB (includes all dependencies)
- Network: Requires stable internet connection

## Support and Maintenance

### Common Issues
1. **ChromeDriver incompatibility**: Update Chrome browser
2. **Excel format errors**: Verify column layout matches requirements
3. **Network timeouts**: Check firewall/proxy settings
4. **Performance issues**: Close other applications, ensure sufficient RAM

### Updates
To update the application:
1. Update source code in development environment
2. Test with `python3 gui/test_gui.py`
3. Rebuild executable with `python3 build_executable.py`
4. Distribute new `dist/` folder to users

### Monitoring
- Application logs processing status in real-time
- Results include timestamps for audit trails
- Failed searches are logged with error details
- Processing can be stopped and resumed with different files

## Legal and Compliance
- Application only searches publicly available registry information
- No data is stored permanently by the application
- Results should be verified manually for critical decisions
- Complies with automated access guidelines for public websites 