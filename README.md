# Site Editura TehnoPress

Site static (fără bază de date, fără PHP). Conținutul este în `content/`, imaginile și PDF-urile în `static/media/`.

## Punere în funcțiune (o singură dată)

1. **GitHub**: creează un depozit **privat**, de exemplu `tehnopress-site`. Instalează *GitHub Desktop*, clonează depozitul, copiază în el tot conținutul acestui folder, apoi „Commit” și „Push”. (Încărcarea din browser permite doar 100 de fișiere o dată, de aceea recomand GitHub Desktop.)
2. În fișierul `static/admin/config.yml` înlocuiește `NUMELE-TAU-GITHUB/tehnopress-site` cu numele real al depozitului.
3. **Netlify**: „Add new site” → „Import an existing project” → GitHub → alegi depozitul. Setările de build se citesc automat din `netlify.toml`.
4. **Autentificarea în panou**:
   - pe GitHub: Settings → Developer settings → OAuth Apps → „New OAuth App”; în „Authorization callback URL” pui `https://api.netlify.com/auth/done`;
   - copiază Client ID și Client Secret în Netlify: Site configuration → Access & security → OAuth → „Install provider” → GitHub.
5. Activează autentificarea în doi pași pe contul GitHub (obligatoriu pentru siguranță).
6. **Domeniu**: în Netlify, Domain management → adaugi `tehnopress.ro` și schimbi înregistrările DNS cum îți arată Netlify.

## Adăugarea unei cărți (zilnic)

Deschide `adresa-site/admin` → Cărți → „Carte nouă” → completezi formularul → „Publicare”. Site-ul se actualizează în 1–2 minute.

Dacă autorul nu există, îl adaugi mai întâi la **Autori**.

## Securitate

Pe server nu rulează cod și nu există bază de date. Singura cale de modificare este contul tău GitHub, de aceea parola trebuie să fie unică și lungă, cu autentificare în doi pași.
