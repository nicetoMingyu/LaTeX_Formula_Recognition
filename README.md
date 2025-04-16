# LaTeX Formula Recognition

A powerful desktop application for recognizing and converting mathematical formulas from images to LaTeX code.

## Features

- 📸 Image-based formula recognition
- 🔄 Convert mathematical formulas to LaTeX code
- 🎨 Modern and user-friendly GUI interface
- 🔒 Secure API key management using system keyring
- 📝 Export to multiple formats (PNG, SVG, PDF, DOCX, Latex, Markdown)
- 🖼️ Support for various image formats(PNG, JPG, JPEG)
- 🔍 High-accuracy formula detection

## Screenshots

### Main Interface
![Main Interface](assets/screenshots/main_interface.png)

### Export Options
![Export Options](assets/screenshots/export_options.png)

## Quick Start (For Users)

### Download Pre-built Application

You can download the latest version of FormulaPro from our [GitHub Releases](https://github.com/nicetoMingyu/LaTeX_Formula_Recognition/releases/latest) page.

Available versions:
- macOS: `FormulaPro.zip`
- Windows: Coming soon
- Linux: Coming soon

### Installation (macOS)

1. Download `FormulaPro.zip` from the [latest release](https://github.com/nicetoMingyu/LaTeX_Formula_Recognition/releases/latest)
2. Unzip the file
3. When you try to open the app and see the security warning:
   - Click "Cancel" on the warning dialog
   - Go to System Settings > Privacy & Security
   - Scroll down to the "Security" section
   - You should see a message about FormulaPro being blocked
   - Click "Open Anyway"
   - In the new dialog that appears, click "Open"
4. The app will now open and remember your choice
5. Enter your Qwen API key when prompted

Note: The security warning appears because the app is not signed with an Apple Developer ID. This is normal for open-source applications distributed outside the Mac App Store. The app is completely safe to use, and you can verify this by checking our source code.

## Installation (For Developers)

If you want to run from source code or contribute to the project:

1. Clone the repository:
```bash
git clone https://github.com/nicetoMingyu/LaTeX_Formula_Recognition.git
cd LaTeX_Formula_Recognition
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Building from Source

### macOS

To build the application on macOS:

1. Make sure you have all dependencies installed:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

2. Make the deployment script executable:
```bash
chmod +x deploy_mac.sh
```

3. Run the deployment script:
```bash
./deploy_mac.sh
```

The script will:
- Create a clean virtual environment
- Install all required dependencies
- Package the application with PyInstaller
- Set up all necessary permissions and attributes
- Create `FormulaPro.zip` in the `dist` directory

The packaged application will be available at:
- `dist/FormulaPro.app` (unzipped application)
- `dist/FormulaPro.zip` (zipped application for distribution)

### Windows & Linux

Support for Windows and Linux coming soon.

## Configuration

1. Create a `.env` file in the project root:
```
Qwen_API_KEY=your_api_key_here
```

2. The application will securely store your API key using the system keyring.

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Use the GUI to:
   - Upload images containing mathematical formulas
   - View and edit recognized LaTeX code
   - Export results in various formats

## Development

The project structure is organized as follows:
```
src/
├── core/       # Core functionality and business logic
├── gui/        # GUI components and windows
├── config/     # Configuration files
└── main.py     # Application entry point
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Qwen for providing the API
- PyQt6 for the GUI framework
- All other open-source libraries used in this project 