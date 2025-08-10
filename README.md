# Twitch Bot

This repository contains a Twitch bot that can be run using Docker. The bot is designed to interact with Twitch's API and can be configured to use HTTPS with a custom domain.

## Environment Variables
The bot requires several environment variables to be set. You can create a `.env` file in the `bot` directory with the following content:

```env
BOT_ID=your_bot_id_here
OWNER_ID=your_owner_id_here
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
DOMAIN=localhost # Domain for the bot's web server
```

## NGINX Certificates
If you want to run the bot with HTTPS, you need to provide SSL certificates. Place your certificates in the `nginx/certs` directory. The bot will use these certificates to serve requests securely.

If you don't have certificates, you can generate self-signed certificates for testing purposes. However, for production use, it's recommended to obtain valid SSL certificates from a trusted Certificate Authority (CA).
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/certs/nginx.key -out nginx/certs/nginx.crt -subj "/CN=YOUR_DOMAIN"
```
## Bot setup when ran

Let's say your domain is `example.com`, once the bot is running, you'll need:
- To Register the twitch bot account:
    - Login to your Twitch account
    - Go to `https://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot&force_verify=true`
    - Authorize the bot
- To Register the bot in your channel:
  - Login to your Twitch account
    - Go to `https://localhost:4343/oauth?scopes=channel:bot&force_verify=true`
    - Authorize the bot
