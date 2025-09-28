# Luk-chan Discord Bot 🤖

A Discord bot for the **LUK.GG** gaming community, designed to enhance user experience with welcome messages, member management, and community features.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Discord.py](https://img.shields.io/badge/Discord.py-2.6.3+-blue?logo=discord)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Welcome System**: Automated welcome messages for new members
- **Server Boost Recognition**: Special messages for server boosters
- **Role Management**: Automated role assignment based on guild membership
- **Interactive Components**: Modern Discord UI components and buttons
- **Modular Architecture**: Extensible cog-based system
- **Custom Emojis & Styling**: Branded visual elements for LUK.GG

## 🚀 Quick Start

### Prerequisites

- Python 3.13
- Discord Bot Token
- PDM (Python Dependency Manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/luk-gg/luk-gg.bot.git
   cd luk-gg.bot
   ```

2. **Install dependencies**

   ```bash
   pip install pdm
   pdm install
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your Discord bot token
   ```

4. **Run the bot**

   ```bash
   pdm run start
   ```

### Docker Deployment

1. **Build and run with Docker Compose**

   ```bash
   docker-compose up -d
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
TOKEN=your_discord_bot_token_here
API_URL=https://api.luk.gg
GUILD_ID=862600196704829440
```

### Settings

The bot configuration is managed through `src/_settings.py`:

- **TOKEN**: Discord bot token (required)
- **API_URL**: LUK.GG API endpoint
- **GUILD_ID**: Target Discord server ID

## 🏗️ Architecture

### Project Structure

```t
src/
├── bot.py              # Main bot class
├── cogs/               # Bot extensions
│   ├── commands/       # Slash and text commands
│   ├── events/         # Event handlers
│   └── handlers/       # Command handlers
├── components/         # Discord UI components
├── _channels.py        # Channel configurations
├── _colors.py          # Brand colors
├── _emojis.py          # Custom emojis
├── _logging.py         # Logging setup
└── _settings.py        # Configuration
```

### Core Components

- **LukChan Bot Class**: Main bot instance with custom intents
- **Cog System**: Modular extensions for commands and events
- **Welcome System**: Automated greeting for new members
- **Boost Detection**: Recognition system for server boosters
- **UI Components**: Modern Discord layout views and buttons

## 🔧 Development

### Adding New Features

1. **Create a new cog** in `src/cogs/commands/` or `src/cogs/events/`
2. **Implement the setup function** for automatic loading
3. **Add UI components** in `src/components/` if needed
4. **Test locally** with `pdm run start`

### Code Quality

The project uses **Ruff** for linting and formatting:

```bash
# Install dev dependencies
pdm install --dev

# Run linting
ruff check src/

# Format code
ruff format src/
```

## 🎮 LUK.GG Community

This bot is specifically designed for the **LUK.GG** gaming community:

- **Website**: [luk.gg](https://luk.gg)
- **Guild**: Bapharia
- **Focus**: Theorycrafting, guides, and gaming resources
- **Community**: Players of all skill levels welcome

### Guild Roles

- 🎯 **Guest**: Non-guild members
- ⭐ **Initiate/Ascendant/VIP**: Guild members by activity level
- 👑 **Staff**: Moderators and administrators
- 🚀 **Legend**: Server boosters
- 🤖 **Null**: Bot accounts

## 📋 Commands

### Owner Commands

- `!cv2` - Test component views (owner only)

### Automatic Features

- Welcome messages on member join
- Server boost recognition
- Role assignment based on guild membership
- Interactive help and information panels

## 🐳 Docker Support

### Build Image

```bash
docker build -t luk-chan .
```

### Run Container

```bash
docker run -d --name luk-chan --env-file .env luk-chan
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write descriptive commit messages
- Test your changes locally
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Gabriel Nobrega**

- [Email](gabrieltkdnobrega63@gmail.com)
- [GitHub](https://github.com/biellSilva)

## 🙏 Acknowledgments

- **LUK.GG Community** for inspiration and feedback
- **Discord.py** developers for the amazing library
- **Python** community for excellent tooling and resources

---

_Built with ❤️ for the LUK.GG gaming community_
