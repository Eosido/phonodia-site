# Image inventory — which photograph sits in which place

Every image URL observed during the harvest, attributed to the page/object it appears on.
All URLs verbatim. Compiled from captured `content.rendered` HTML, rendered-page fetches,
the WooCommerce Store API and the media endpoint.

## Site chrome (appears on every page)

| URL | Role |
|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2025/04/Φωνωδία-mavro.png | Header logo (black) |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/04/Φωνωδία-aspro.png | Header logo (white), front page |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/04/Φωνωδία-mavro-1024x391.png | Footer logo |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/11/e0b4cdc54800b9d7abcb9c012990662978eb39d4.png | Payment method badge |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/11/d51f7a234af740dcf1ad7dc9619e18c065a31cf7.png | Payment method badge |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/11/274751750325e062f8530373699503fbbfa16b58.png | Payment method badge |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/11/c7b56c359755790e7604b830a8a7390d172dc900.png | Payment method badge |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/11/IRIS-online-payments-logo-4283025463-1024x420.jpg | IRIS payments logo |

## Front page — https://phonodiavocalensemble.com/ (id 2940)

| URL / ref | Role |
|---|---|
| https://phonodia.com/wp-content/uploads/2026/04/bannerlite.mp4 | Hero background video (injected by base64 script; hosted on phonodia.com) |
| https://cdn.phonodia.com/hero-vid.webm | Hero video, commented out in source |
| YouTube `G_Zlht0m1Oo` | "Παρακολουθήστε το βίντεο" play button |
| https://phonodiavocalensemble.com/wp-content/uploads/2020/06/20171218_Christmas_Concert_Bach-64-600x600.jpg | "Λιγά λόγια για το σύνολο" portrait |
| media id 4000 | `vc_single_image` beside the About text (circle crop) |
| media ids 4098, 4048, 4021, 4004, 3997, 3993 | Six-image `vc_media_grid` band at page bottom |

## Photo gallery — https://phonodiavocalensemble.com/gallery/ (album covers)

| URL | Album |
|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2025/05/IMG_0500δ-scaled.jpg | Οι σπόροι της Σμύρνης |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/05/81693049_825010451293576_1527516139708481536_o.jpg | Λιλιπούπολη |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/05/270746021_1338943499900266_1769204994445011124_n.jpg | Η συνέλευση των ζώων |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/05/Agios_Titos_Choir_2024-61-scaled.jpg | Άγιος Τίτος |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/05/IMG_0290-3-scaled.jpg | Η νέα γη |

## Merch Store page — https://phonodiavocalensemble.com/en/store/ (id 5162)

| URL | Role |
|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2026/01/New-Project32.png | "Gentlemen" category tile (600x800) |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/01/New-Project31.png | "Ladies" category tile (600x800) |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/01/New-Project33.png | "Kids" category tile (600x800) |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/01/New-Project6.png | "Accessories" banner (1200x400) |

## Product images (full-size, from the WooCommerce Store API)

| URL | Product | ID |
|---|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/white.png | Φωνη – Kids | 6538 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/Untitled-1.png | Φωνη – Hoodie – Unisex | 6525 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/GYN_white.webp | Φωνη – Ladies | 6016 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/FONI_MEN_white_EMPROS.png | Φωνη – Gents | 5880 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/KIDS_TOKYO2_white-1.webp | Phonodia in Tokyo – Kids | 5415 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/GYN_TOKYO1_white.webp | The Great Journey in Tokyo – Ladies | 5389 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/GYN_TOKYO2_white.webp | Phonodia in Tokyo – Ladies | 5359 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/TOKYO1_MEN_white.webp | The Great Journey in Tokyo – Gents | 5313 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/TOKYO2_MEN_white.webp | Phonodia in Tokyo – Gents | 5292 |

Thumbnail derivatives (`-300x300`, `-150x150`, `-100x100`, `-50x50`) of each of the above appear in
the product-loop HTML on pages 6523 and 5162; WordPress generates them from the full-size file.

## Blog post 4434 — «Στο Θέατρο»: Ρεσιτάλ … στο ΕΛ.ΜΕ.ΠΑ

| URL | Role |
|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2025/04/ELMEPA-1-scaled.png | Concert poster, full size (1810w) |
| https://phonodiavocalensemble.com/wp-content/uploads/2025/04/ELMEPA-1-724x1024.png | Poster as displayed (wp-image-4435) |

Also available at widths 600x849, 212x300, 768x1086, 1086x1536, 1448x2048.

## Media library items captured

| URL | id | dims | attached to |
|---|---|---|---|
| https://phonodiavocalensemble.com/wp-content/uploads/2026/04/tt.webp | 6561 | 1086x1448 | — |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/06/a.webp | 6554 | 1218x2048 | — |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/blk.png | 6544 | 1706x1280 | product 6538 |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/blk.webp | 6543 | 1706x1280 | — |
| https://phonodiavocalensemble.com/wp-content/uploads/2026/07/trq.png | 6542 | 1706x1280 | product 6538 |

## Not recoverable

Member/artist portraits (93 js_artist entries), event posters (11 js_events), photo-album interiors
(5 js_photo_albums) and video thumbnails (7 js_videos) are injected client-side by theme AJAX and are
absent from the server-rendered HTML. Their post types are not exposed over REST. Only their
permalinks were recoverable — see the `cpt-*-urls.json` files.

Photo credit stated in the site footer: **Photos by Graham Hodgetts**.
