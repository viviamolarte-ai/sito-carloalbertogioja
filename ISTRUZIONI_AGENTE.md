# Regole per l'aggiornamento automatico del sito

Sito: https://carloalbertogioja.com (Netlify, progetto starlit-sfogliatella-201c65), HTML statico bilingue IT/EN.

## Cosa aggiornare
- **index.html**
  - Hero `.h-news`: solo eventi FUTURI, max 4, in ordine cronologico crescente.
  - `#appuntamenti`: eventi futuri in `.event-row` (testi IT + EN con classe `en-s` e `style="display:none"`).
  - Archivio eventi passati: righe compatte `opacity:.6`, ordine cronologico DECRESCENTE; quando un evento passa, spostalo qui.
  - Bio, premi, teatri, media: solo con fatti verificati (email di Carlo, articoli, CV).
- **direttore.html** "Direzioni selezionate": aggiungere i concerti in cui Carlo dirige.
- **cantante.html** repertorio: aggiungere ruoli nuovi.

## Regole
- Voce: sempre **Basso** (non basso-baritono).
- NON inserire eventi in cui Carlo canta solo come artista del coro (es. Carmina Burana 2026).
- Mai compensi, IBAN, dati personali, indirizzi privati.
- Scarta omonimi e notizie non pertinenti.
- Lavorare su un branch `bozza-AAAA-MM-GG` e aprire una Pull Request: Netlify genera l'anteprima. Mai pubblicare su `main` senza l'ok di Carlo.
