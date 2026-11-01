# Regole per l'aggiornamento automatico del sito

Sito: https://carloalbertogioja.com (Netlify, progetto starlit-sfogliatella-201c65), HTML statico bilingue IT/EN.

## Cosa aggiornare
- **index.html**
  - Hero `.h-news`: sempre 4 voci, ordine cronologico DECRESCENTE: prima gli eventi futuri, poi i più recenti passati fino ad arrivare a 4.
  - `#appuntamenti` ("In scena"): tutti gli eventi futuri + i 3 eventi passati più recenti (scelta di Carlo, 01/11/2026), righe complete `.event-row` (testi IT + EN con classe `en-s` e `style="display:none"`), ordine cronologico DECRESCENTE.
  - Archivio eventi passati (a scomparsa): tutti gli eventi passati oltre quei 3, con `opacity:.6` e riquadro data `background:var(--dg)`; il pulsante sta subito sotto i 3 passati recenti, ordine DECRESCENTE.
  - Bio, premi, teatri, media: solo con fatti verificati (email di Carlo, articoli, CV).
- **direttore.html** "Direzioni selezionate": aggiungere i concerti in cui Carlo dirige.
- **cantante.html** repertorio: aggiungere ruoli nuovi.

## Regole
- Voce: sempre **Basso** (non basso-baritono).
- NON inserire eventi in cui Carlo canta solo come artista del coro (es. Carmina Burana 2026).
- Mai compensi, IBAN, dati personali, indirizzi privati.
- Scarta omonimi e notizie non pertinenti.
- Lavorare su un branch `bozza-AAAA-MM-GG` e aprire una Pull Request: Netlify genera l'anteprima. Mai pubblicare su `main` senza l'ok di Carlo.
