# Regole per l'aggiornamento automatico del sito

Sito: https://carloalbertogioja.com (Netlify, progetto starlit-sfogliatella-201c65), HTML statico bilingue IT/EN.

## Cosa aggiornare
- **index.html**
  - Hero `.h-news`: sempre 4 voci, ordine cronologico DECRESCENTE: prima gli eventi futuri, poi i più recenti passati fino ad arrivare a 4.
  - `#appuntamenti` ("In scena"): tutti gli eventi futuri + SEMPRE almeno gli 8 eventi passati più recenti, righe complete `.event-row` (testi IT + EN con classe `en-s` e `style="display:none"`), ordine cronologico DECRESCENTE.
  - Archivio eventi passati (a scomparsa): solo gli eventi più vecchi oltre quegli 8, righe compatte `opacity:.6`, ordine DECRESCENTE.
  - Bio, premi, teatri, media: solo con fatti verificati (email di Carlo, articoli, CV).
- **direttore.html** "Direzioni selezionate": aggiungere i concerti in cui Carlo dirige.
- **cantante.html** repertorio: aggiungere ruoli nuovi.

## Regole
- Voce: sempre **Basso** (non basso-baritono).
- NON inserire eventi in cui Carlo canta solo come artista del coro (es. Carmina Burana 2026).
- Mai compensi, IBAN, dati personali, indirizzi privati.
- Scarta omonimi e notizie non pertinenti.
- Lavorare su un branch `bozza-AAAA-MM-GG` e aprire una Pull Request: Netlify genera l'anteprima. Mai pubblicare su `main` senza l'ok di Carlo.
