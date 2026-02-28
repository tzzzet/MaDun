# 🛡️ MaDun - macOS Clipboard Privacy Guardian

A lightweight macOS menu bar application that protects your sensitive data by detecting and automatically sanitizing API keys, credentials, and private functions before they're accidentally copied to the clipboard.

## ✨ Key Features

- **🔍 Real-time Clipboard Monitoring** - Continuously monitors clipboard activity
- **🔐 Multi-layer Detection** - Detects API keys from OpenAI, AWS, GitHub, Azure, Google, Slack, and more
- **🛡️ Automatic Sanitization** - Automatically replaces sensitive data with `[Type·Sanitized]` markers
- **⏱️ 30-Second Undo Window** - Accidentally sanitized something safe? Restore it within 30 seconds
- **🔌 100% Offline** - Zero network connectivity, completely privacy-focused
- **⚡ Lightweight** - Uses <0.1% CPU, minimal system impact
- **🎯 Zero Configuration** - Works out of the box with smart defaults

## 🎬 How It Works

1. **Copy as usual** - MaDun silently monitors your clipboard
2. **Detection** - When you copy sensitive data (API key, database password, etc.)
3. **Sanitization** - The clipboard is automatically cleared and replaced with a safe marker
4. **Notification** - You get a subtle notification telling you what was detected
5. **Undo** - Click "Restore" in the notification if it was a false positive

### Detection Examples

```
✅ Detected and Sanitized:
- sk-proj-abc123...xyz → [OpenAI Key·Sanitized]
- AKIA123ABC456XYZ → [AWS Key·Sanitized]
- ghp_abc123...xyz → [GitHub Token·Sanitized]

✅ Allowed (Safe to Copy):
- Regular text, URLs, code snippets
- Configuration values
- Public information
```

## 📋 Detected Sensitive Data

| Type | Pattern | Example |
|------|---------|---------|
| OpenAI API Key | `sk-proj-[a-zA-Z0-9]{20,}` | `sk-proj-abc123xyz` |
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| GitHub Token | `ghp_[A-Za-z0-9]{36,}` | `ghp_abc123xyz...` |
| Azure Key | `[a-zA-Z0-9]{32}` | Various Azure secrets |
| Google API Key | `AIza[0-9A-Za-z\-_]{35}` | Google service keys |
| Slack Token | `xox[baprs]-[a-zA-Z0-9\-]{10,}` | Slack bot/user tokens |

## 🚀 Installation

### Prerequisites
- macOS 10.13 or later
- Python 3.7+

### Quick Start

1. **Download the latest release** from [Releases](../../releases)
2. **Double-click** `MaDun.app` to install
3. The app will appear in your menu bar as 🔒

### Build from Source

```bash
# 1. Clone the repository
git clone https://github.com/tzzzet/MaDun.git
cd MaDun

# 2. Install dependencies
pip install rumps

# 3. Run directly
python3 madun.py

# 4. (Optional) Package as macOS app
pyinstaller madun.spec
```

## 💻 Usage

### Menu Bar Controls

Click the 🔒 icon in your menu bar to access:

- **⚙️ Settings** - Configure detection rules and app behavior
- **📋 View Logs** - See interception history
- **⏸ Pause Protection** - Temporarily disable monitoring
- **🚀 Launch on Startup** - Enable auto-launch at boot
- **📊 Statistics** - View daily interception count

### Settings Window

The settings interface allows you to:

- ✅ **Whitelist trusted apps** - Disable monitoring for specific applications
- 🚫 **Manage detection rules** - Add custom patterns for your needs
- 📝 **Configure logging** - Enable/disable activity logging
- 🔄 **Real-time updates** - Changes apply immediately

## 📊 Performance

| Metric | Value |
|--------|-------|
| CPU Usage | <0.1% at idle |
| Memory Usage | ~50-80 MB |
| Clipboard Detection | <10ms response time |
| Battery Impact | Negligible |

*Tested on MacBook Pro M1 running macOS 13*

## 🔒 Privacy & Security

- **100% Offline** - No data is sent anywhere
- **No Network Connectivity** - Zero tracking, zero telemetry
- **Local Processing Only** - All detection happens on your device
- **Open Source** - Audit the code yourself
- **MIT Licensed** - Free to use and modify

## 🛠 Technical Details

### Architecture

```
madun.py (Main Application)
├── Clipboard Monitoring (Real-time)
├── Multi-layer Detection Engine
│   ├── Layer 1: Pattern Matching
│   ├── Layer 2: Contextual Analysis
│   └── Layer 3: Entropy Analysis
├── Menu Bar Interface (rumps)
└── Settings Manager (Tkinter)
```

### Detection Layers

1. **Pattern Matching** - Regex-based detection for known secret formats
2. **Contextual Analysis** - Analyzes surrounding context (variable names, env vars)
3. **Entropy Analysis** - Measures randomness to identify high-entropy secrets
4. **Undo Manager** - Maintains 30-second restore capability

## 📝 Configuration

Create `~/.madun/config.json` to customize:

```json
{
  "trusted_apps": [
    "com.microsoft.VSCode",
    "com.apple.Terminal"
  ],
  "dangerous_apps": [
    "com.google.Chrome",
    "com.tencent.xinWeChat"
  ],
  "rules": [
    ["custom_pattern", "Custom Secret Name"]
  ]
}
```

## 🔄 Update Logs

### v1.3.0 (Current)
- ✅ Menu bar icon + double-click to open settings
- ✅ Real-time clipboard monitoring
- ✅ 30-second undo window
- ✅ Zero network connectivity
- ✅ Open source release

### Roadmap
- 🔮 Multi-layer detection enhancement
- 🔮 Enterprise whitelist management
- 🔮 Custom detection rule builder
- 🔮 System preferences integration

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support & Feedback

- **Issues** - Report bugs or request features on [GitHub Issues](../../issues)
- **Discussions** - Share ideas and ask questions in [GitHub Discussions](../../discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

MaDun is provided "as is" without any warranty. While we strive to detect all sensitive data, no system is 100% perfect. Always review what you copy before pasting in public/untrusted contexts.

## 🙏 Acknowledgments

- Built with [rumps](https://github.com/jmooring/rumps) - Python library for macOS menu bar apps
- Icons designed with care for security-conscious developers
- Inspired by the need to prevent accidental secret leaks

---

**Made with ❤️ for developers who care about security**

⭐ If this project helps you, consider giving it a star on GitHub!
