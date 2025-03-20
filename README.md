# CS_Stockers

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![API](https://img.shields.io/badge/live%20API-integrated-orange.svg)
![AI](https://img.shields.io/badge/AI%20assistants-enabled-blueviolet.svg)

## Overview

CS_Stockers is a cutting-edge Flask web application that simulates real-time stock market trading. By integrating live API data with interactive user interfaces, the platform provides an authentic trading experience for both beginners and experienced investors. The application features dynamic portfolio tracking, AI-powered assistance, and visual analytics to help users make informed investment decisions.

### Key Features

- **Live Stock Market Data**: Real-time integration with financial APIs for accurate market information
- **Interactive Trading Simulator**: Buy and sell virtual stocks with realistic market conditions
- **Dual AI Assistants**: Receive expert guidance and answer investment queries through specialized AI chat interfaces
- **Dynamic Chart Visualization**: Track portfolio performance with automatically updating charts
- **User-Friendly Interface**: Intuitive design suitable for all experience levels
- **Educational Resources**: Access to market news and investment learning materials

## Architecture

CS_Stockers follows a modern web application architecture with these components:

### Backend (Flask)

- RESTful API integration for live stock data
- SQLite database for user accounts and portfolio management
- Session management for secure user authentication
- AI model integration for intelligent chat assistants
- Data processing for performance tracking and visualization

### Frontend

- Responsive design for optimal viewing on all devices
- Dynamic JavaScript charts for real-time data visualization
- Interactive user interface for trading simulation
- Chat interfaces for AI assistant interaction
- News and resource feeds for market information

## Project Structure

```plaintext
CS_Stockers/
├── app.py                  # Main Flask application
├── helpers.py              # Helper functions for application logic
├── finance.db              # SQLite database
├── requirements.txt        # Python dependencies
├── Procfile                # Deployment configuration
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Image assets
├── templates/              # HTML templates
│   ├── layout.html         # Base template
│   ├── index.html          # Homepage
│   ├── portfolio.html      # User portfolio page
│   ├── quote.html          # Stock quote page
│   ├── buy.html            # Buy stocks page
│   ├── sell.html           # Sell stocks page
│   ├── history.html        # Transaction history page
│   ├── assistant.html      # AI assistant interface
│   └── news.html           # Market news and resources
└── flask_session/          # Flask session data
```

## Getting Started

### Prerequisites

- Python 3.9+
- Flask 3.0.0+
- SQLite
- OpenAI API access (for AI assistants)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/CS_Stockers.git
cd CS_Stockers

# Create and activate virtual environment
python -m venv virEnv
source virEnv/bin/activate  # On Windows: virEnv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
flask run
```
## Usage

1. Register for an account or log in to existing account
2. Add funds to your virtual trading account
3. Browse available stocks and view current prices
4. Purchase stocks to build your portfolio
5. Monitor your investments with dynamic charts
6. Consult with AI assistants for investment advice
7. Sell stocks as needed based on market conditions
8. Track your transaction history and performance

## AI Assistants

CS_Stockers features two specialized AI chat assistants:

1. **Investment Expert**: Provides professional stock recommendations, market analysis, and investment strategies
2. **Educational Guide**: Helps beginners understand stock market concepts, terminology, and best practices

## Technologies Used

- **Flask**: Web application framework
- **SQLite**: Database management
- **JavaScript/HTML/CSS**: Frontend development
- **Chart.js**: Interactive data visualization
- **OpenAI API**: AI assistant integration
- **Financial APIs**: Live stock market data
- **Flask-Session**: Server-side session management

## Screenshots

![image](https://github.com/user-attachments/assets/a5ceefda-351f-49fc-84bc-959134d0025c)
![image](https://github.com/user-attachments/assets/c9f86c1a-79cd-438b-9370-0c2276753e71)
![image](https://github.com/user-attachments/assets/65709193-233e-4d8a-8a27-3796f4ec0496)
![image](https://github.com/user-attachments/assets/304e9b61-5292-48db-93e9-c79a4f3cd474)
![image](https://github.com/user-attachments/assets/0c4a4654-b32d-492a-993a-c9d1a0f33b18)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Commit Message Guidelines

We follow a simple commit message format to make the project history readable:

`<emoji> <type>: <subject>`

### Types and Emojis

| Emoji | Type | Description |
|-------|------|-------------|
| ✨ | `feat` | New feature or enhancement |
| 🐛 | `fix` | Bug fix |
| 📝 | `docs` | Documentation changes |
| 💄 | `style` | Code formatting and styling |

### Examples

- ✨ feat: add portfolio performance analytics
- 🐛 fix: resolve login authentication issue
- 📝 docs: update installation instructions
- 💄 style: improve responsive design for mobile

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Project Link: [https://github.com/yourusername/CS_Stockers](https://github.com/yourusername/CS_Stockers)

---

**Note**: This project is currently under development. Features and capabilities are subject to change.