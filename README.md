**CryptoPulse**

CryptoPulse is an AI-powered crypto social intelligence platform that turns raw social media chatter into structured, actionable market intelligence. It continuously monitors crypto-related posts, runs them through a dual sentiment engine (CryptoBERT and FinBERT), identifies which cryptocurrencies are being discussed, scores the poster's social influence, and combines all of this into a trading signal strength score. It then tracks how the market actually reacted in the minutes and hours after the post, using live Binance price data. Everything is served through a FastAPI backend backed by SQLite, and visualized through a React + TypeScript dashboard, giving a near-real-time view of how social sentiment correlates with price movement. New posts are ingested automatically every 10 minutes, so the dataset keeps growing on its own without any manual intervention.

---

**Features**

**AI-Powered Sentiment Analysis**

CryptoPulse uses two specialized transformer-based NLP models to analyze the sentiment of cryptocurrency-related social media posts:

- **CryptoBERT** — A cryptocurrency-focused language model used to identify market-oriented sentiment such as bullish, bearish, or neutral signals from crypto-specific terminology and discussions.
- **FinBERT** — A financial-domain language model that provides an additional sentiment perspective based on financial language and market context.
- **Dual-model analysis** — Both models analyze the same post independently, allowing CryptoPulse to compare crypto-specific and broader financial sentiment.
- **Confidence scoring** — Each prediction includes a confidence score, providing an indication of how strongly the model supports its classification.
- **Structured sentiment output** — Results are normalized into consistent sentiment labels and confidence values for use throughout the dashboard.
- **Signal integration** — Sentiment confidence from CryptoBERT is incorporated into the platform's overall signal-strength calculation, alongside social influence.
- **Manual & live analysis** — The same sentiment pipeline can analyze both continuously ingested tweets and posts submitted manually through the analysis interface.

**External APIs**

- **TwitterAPI.io** — Fetches crypto-related tweets for the live/continuous ingestion pipeline, supplying the social media data analyzed every 10 minutes.
- **CoinMarketCap API** — Provides cryptocurrency metadata and market information, supporting asset identification and classification.
- **Binance Market Data API** — Provides historical price/candle data used to calculate 5-minute, 15-minute, and 1-hour market reactions following a post.

**Cryptocurrency Detection**
- Automatically identifies cryptocurrencies mentioned in posts
- Determines a primary asset
- Tracks additionally mentioned assets
- Supports symbols such as BTC, ETH, SOL, XRP, DOGE, and more

**Social Influence Analysis**

Calculates an influence score using:
- Followers
- Likes
- Retweets
- Account/tweet engagement

**Signal Strength**

Combines social influence and sentiment confidence to generate a trading signal strength score. Signals are categorized into:
- Very Strong
- Strong
- Moderate
- Weak

**Market Reaction Analysis**

Tracks cryptocurrency price movement after a social media post:
- 5-minute reaction
- 15-minute reaction
- 1-hour reaction
- Base price
- Percentage change

Market data is retrieved through Binance market data.

**Continuous Live Intelligence**

CryptoPulse continuously collects new crypto-related tweets while the backend is running.

The ingestion pipeline:

```
TwitterAPI.io
      ↓
Latest crypto tweets
      ↓
Duplicate detection
      ↓
Crypto relevance detection
      ↓
Cryptocurrency identification
      ↓
CryptoBERT + FinBERT
      ↓
Social influence
      ↓
Signal strength
      ↓
Market reaction
      ↓
SQLite database
      ↓
React dashboard
```

New tweets are checked every 10 minutes, while previously analyzed tweets are skipped using their unique tweet ID.

**Live Intelligence Dashboard**

The frontend provides:
- Live tweet feed
- Signal strength
- Social influence
- Sentiment indicators
- Market reactions
- Filtering
- Detailed tweet intelligence modal

**Manual Analysis**

Users can submit a crypto-related post manually and receive:

```
Cryptocurrency detection
        ↓
CryptoBERT sentiment
        ↓
FinBERT sentiment
        ↓
Social influence
        ↓
Signal strength
        ↓
Market reaction
```

---

**Architecture**

```
                    ┌─────────────────┐
                    │  TwitterAPI.io  │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Tweet Collection    │
                  │ & Deduplication     │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Crypto Detection    │
                  └──────────┬──────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌────────────────┐      ┌────────────────┐
        │   CryptoBERT   │      │    FinBERT     │
        │    Sentiment   │      │    Sentiment   │
        └───────┬────────┘      └───────┬────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
                  ┌─────────────────────┐
                  │ Social Influence    │
                  │ & Signal Strength   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Binance Market Data │
                  └──────────┬──────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ SQLite Database│
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │ React Frontend │
                    └────────────────┘
```

---

**Tech Stack**

Backend
- Python
- FastAPI
- SQLite
- Hugging Face Transformers
- PyTorch
- Scikit-learn

NLP / AI
- CryptoBERT
- FinBERT
- Transformer-based sentiment analysis

Data & APIs
- TwitterAPI.io
- CoinMarketCap API
- Binance Market Data API
- REST APIs

Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Lucide React

Development
- Git
- GitHub
- Uvicorn

---

**Project Structure**

```
CryptoPulse/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   │
│   │   └── services/
│   │       ├── analyzer.py
│   │       ├── crypto_detector.py
│   │       ├── crypto_identifer.py
│   │       ├── crypto_sentiment.py
│   │       ├── database.py
│   │       ├── finbert_sentiment.py
│   │       ├── live_analyzer.py
│   │       ├── market_data.py
│   │       ├── social_influence.py
│   │       ├── tweet_processor.py
│   │       ├── twitter_api.py
│   │       └── twitter_profile.py
│   │
│   └── requirements.txt
│
├── cryptopulse-frontend-fixed/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── services/
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── data/
├── .env.example
├── .gitignore
└── README.md
```

---

**Setup**

1. Clone the repository

```
git clone https://github.com/yatharth77686/CryptoPulse.git
cd CryptoPulse
```

2. Create Python environment

```
conda create -n cryptopulse python=3.11
conda activate cryptopulse
```

3. Install backend dependencies

```
pip install -r backend/requirements.txt
```

4. Configure environment variables

Create a `.env` file and add:

```
TWITTERAPI_IO_KEY=your_api_key_here
```

Do not commit the `.env` file.

5. Start the backend

From the project root:

```
uvicorn backend.app.main:app --reload
```

The API will run at:

```
http://localhost:8000
```

6. Start the frontend

Open another terminal:

```
cd cryptopulse-frontend-fixed
npm install
npm run dev
```

The frontend will be available at the URL shown by Vite, normally:

```
http://localhost:5173
```

---

**API Endpoints**

| Endpoint               | Description                            |
| ----------------------- | --------------------------------------- |
| `GET /`                 | API status                              |
| `GET /analysis`         | Retrieve analyzed posts                 |
| `GET /crypto/{symbol}`  | Retrieve analysis for a cryptocurrency  |
| `GET /market/{symbol}`  | Retrieve market reactions               |
| `GET /sentiment`        | Sentiment summary                       |
| `POST /analyze`         | Analyze a social media post             |

---

**Example Analysis**

Input:

```
Bitcoin is showing strong momentum after reclaiming the $64,000 level.
If BTC holds above $64K, the next resistance could be around $66K.
Institutional demand remains strong.
```

CryptoPulse identifies:

```
{
  "assets": {
    "primary": "BTC",
    "mentioned": []
  },
  "sentiment": {
    "cryptobert": {
      "label": "Neutral",
      "confidence": 0.6335
    },
    "finbert": {
      "label": "positive",
      "confidence": 0.9498
    }
  },
  "signal_strength": 45.57
}
```

Market reaction is then calculated for:

```
5m
15m
1h
```

---

**Live Ingestion**

The backend automatically starts a background ingestion worker.

```
Server starts
     ↓
Fetch latest crypto tweets
     ↓
Check tweet ID against SQLite
     ↓
Analyze only new tweets
     ↓
Store results
     ↓
Wait 10 minutes
     ↓
Repeat
```

This allows the database to continuously grow while the backend is running, without requiring the user to manually press a fetch button.

---

**Security**

API credentials are stored in environment variables.

Sensitive files such as:

```
.env
*.db
__pycache__/
node_modules/
```

are excluded using `.gitignore`.

---

**Future Improvements**

- Expand cryptocurrency coverage
- Add additional social media sources
- Improve signal-strength calibration
- Add historical sentiment/price correlation
- Add portfolio monitoring
- Add configurable ingestion intervals
- Add alert notifications for high-confidence signals
- Deploy the backend and frontend to cloud infrastructure

---

**Author**

Yatharth Sharma

B.Tech Electronics & Communication Engineering
Jaypee Institute of Information Technology
