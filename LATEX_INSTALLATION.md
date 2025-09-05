# LaTeX Installation Guide

To enable professional PDF generation with LaTeX formatting, you need to install a LaTeX distribution.

## Windows (Recommended: MiKTeX)

1. **Download MiKTeX**:

   - Go to https://miktex.org/download
   - Download the MiKTeX Installer for Windows

2. **Install MiKTeX**:

   - Run the installer as Administrator
   - Choose "Install MiKTeX for all users" (recommended)
   - Select "Complete MiKTeX" installation
   - Follow the installation wizard

3. **Verify Installation**:
   - Open Command Prompt
   - Run: `pdflatex --version`
   - You should see version information

## Alternative: TeX Live

1. **Download TeX Live**:

   - Go to https://www.tug.org/texlive/
   - Download the TeX Live installer

2. **Install TeX Live**:
   - Run the installer
   - Follow the installation wizard
   - This is a larger download (~4GB) but includes all packages

## macOS

```bash
# Using Homebrew
brew install --cask mactex

# Or using MacTeX directly
# Download from: https://www.tug.org/mactex/
```

## Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install texlive-full
```

## Verification

After installation, restart your application and test PDF generation. The application will:

1. **With LaTeX installed**: Generate professional PDF reports with:

   - Table of contents
   - Professional formatting
   - Tables and charts
   - Headers and footers
   - Hyperlinks

2. **Without LaTeX**: Fall back to text files (.txt) with the same content

## Features

The LaTeX PDF reports include:

- ✅ Professional document structure
- ✅ Table of contents
- ✅ Proper section numbering
- ✅ Formatted tables
- ✅ Bullet points and lists
- ✅ Headers and footers
- ✅ Hyperlinks
- ✅ Mathematical expressions support
- ✅ Professional typography

## Troubleshooting

If you encounter issues:

1. **Path Issues**: Ensure `pdflatex` is in your system PATH
2. **Permission Issues**: Run as Administrator (Windows) or with sudo (Linux/macOS)
3. **Package Issues**: LaTeX will automatically download missing packages on first use

## Benefits

LaTeX provides:

- 🎯 **Professional Quality**: Publication-ready documents
- 📊 **Advanced Tables**: Complex table formatting
- 🔗 **Hyperlinks**: Clickable links and references
- 📑 **Table of Contents**: Automatic generation
- 🎨 **Typography**: Professional font rendering
- 📐 **Mathematical**: Support for equations and formulas
