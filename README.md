# Binance Auto Trading Bot (Webhook)
Déploiement automatique sur Render pour recevoir des alertes TradingView et passer des ordres sur Binance.

## 🚀 Déploiement Render
1. Fork ce repo sur GitHub
2. Va sur [https://render.com](https://render.com)
3. Crée un nouveau Web Service lié à ce repo
4. Renseigne les variables d'environnement :
   - BINANCE_API_KEY
   - BINANCE_API_SECRET
   - SIMULATE (true/false)

## 📤 Webhook
Configure une alerte TradingView :
- URL Webhook : `https://tonbot.onrender.com/webhook`
- Message :
```json
{
  "action": "buy",
  "symbol": "BTCUSDT",
  "qty": 0.01
}
```

## ✅ Mode simulation
Pour tester sans passer d’ordre réel, mets `SIMULATE=true`.
