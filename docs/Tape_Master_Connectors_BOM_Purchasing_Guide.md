# TAPE MASTER EXERCISER & SIGNAL DIGITIZER v2
## GUIDA DEFINITIVA E DISTINTA BASE DI ACQUISTO CONNETTORI (BOM INTERCONNECT)
**Autore / Hardware Designer**: Alessio Iodice (<alessio67@gmail.com>)  
**Data**: 2026-11-06  
**Revisione**: 2.0  
**Licenza**: CC BY-NC-SA 4.0  

---

## 1. Jack Audio 3.5 mm Orizzontali da Circuito Stampato (THT)
Utilizzati sulle cartucce audio: **#04 (Sinclair ZX Spectrum)**, **#10 (Apple II)**, **#12 (Sharp MZ)**.

| Componente / Serie | Codice Produttore (MPN) | Descrizione Tecnica | N. Pin | Foratura / Footprint Compatibile | Distributore e Codice Ordine |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Jack Audio 3.5 mm Universale (CONSIGLIATO)** | **Same Sky (ex CUI) `SJ1-3525N`** | Presa Jack Stereo 3.5 mm ad angolo retto THT, corpo PBT nero, boccola ottone nichelato, **doppio interruttore interno normalmente chiuso (Tip + Ring switches)** | 5 pin | Foratura standard 5 pin ad asse trasversale ($X=\pm 5\text{ mm}$, $Y=-5\text{ mm}$) | • **Mouser**: `490-SJ1-3525N`<br>• **DigiKey**: `CP-3525N-ND`<br>• **LCSC**: `C319356` |
| **Jack Audio 3.5 mm (Variante 4 Pin)** | **Same Sky (ex CUI) `SJ1-3524N`** | Presa Jack Stereo 3.5 mm ad angolo retto THT, **singolo interruttore (solo Tip switch)** | 4 pin | Compatibile con l'impronta `SJ1-3525N` a 5 fori (il 5° foro resta libero) | • **Mouser**: `490-SJ1-3524N`<br>• **DigiKey**: `CP-3524N-ND` |
| **Jack Audio 3.5 mm Semplice (Variante 3 Pin)** | **Same Sky (ex CUI) `SJ1-3523N`** | Presa Jack Stereo 3.5 mm ad angolo retto THT, **senza interruttori** (TRS puro: Tip, Ring, Sleeve) | 3 pin | Compatibile con l'impronta `SJ1-3525N` a 5 fori (i 2 fori switch restano liberi) | • **Mouser**: `490-SJ1-3523N`<br>• **DigiKey**: `CP-3523N-ND` |

> [!IMPORTANT]
> **Compatibilità Universale Footprint**: L'impronta KiCad adotta la configurazione a **5 fori dell'SJ1-3525N**. In questo modo, l'utente o il laboratorio di restauro può montare indifferentemente la versione a 5 pin (`SJ1-3525N`), a 4 pin (`SJ1-3524N`) o a 3 pin (`SJ1-3523N`) reperita a stock senza dover modificare il circuito stampato o piegare i terminali.

---

## 2. Prese Circolari DIN da Circuito Stampato (THT Orizzontali)
Utilizzate sulle cartucce per personal computer vintage europei e giapponesi.

| Piattaforma Target | Tipo DIN | Angolo | Codice Produttore (MPN) | Descrizione Tecnica | Distributore e Codice Ordine |
| :--- | :---: | :---: | :--- | :--- | :--- |
| • **#03 Thomson / Olivetti PC128**<br>• **#05 Amstrad CPC 464/664/6128**<br>• **#08 Tandy CoCo / Dragon 32/64** | **DIN 5 poli** | $180^\circ$ | **Same Sky `SDS-50J`** | Connettore femmina circolare DIN 5 pin 180°, montaggio orizzontale a 90° THT, contatti placcati argento, alette di fissaggio a telaio GND | • **Mouser**: `490-SDS-50J`<br>• **DigiKey**: `CP-SDS-50J-ND`<br>• **Farnell**: `2112448` |
| • **#07 Acorn BBC Micro / Electron**<br>• **#11 Oric 1 / Oric Atmos / Telestrat** | **DIN 7 poli** | $270^\circ$ | **Same Sky `SDS-70J`** | Connettore femmina circolare DIN 7 pin 270°, montaggio orizzontale a 90° THT, schermatura metallica continua | • **Mouser**: `490-SDS-70J`<br>• **DigiKey**: `CP-SDS-70J-ND`<br>• **Farnell**: `2112450` |
| • **#06 MSX Standard (MSX 1 / 2 / 2+ / turbo R)** | **DIN 8 poli** | $270^\circ$ | **Same Sky `SDS-80J`** | Connettore femmina circolare DIN 8 pin 270° (disposizione a ferro di cavallo esteso), montaggio orizzontale 90° THT | • **Mouser**: `490-SDS-80J`<br>• **DigiKey**: `CP-SDS-80J-ND`<br>• **Farnell**: `2112451` |
| • **#01 Commodore C16 / Plus4 (Porta Datassette 1531)** | **Mini-DIN 8** | Circolare | **Same Sky `MD-80`** (o `MD-80SM`) | Connettore femmina circolare Mini-DIN 8 pin, corpo schermato orizzontale THT | • **Mouser**: `490-MD-80`<br>• **DigiKey**: `CP-MD-80-ND` |

---

## 3. Connettore Bus Universale 40 Pin ($2 \times 20$, Passo $2.54\text{ mm}$)
Interfaccia di accoppiamento complanare rigida tra Mainboard e Cartucce.

| Ruolo / Posizione | Tipo Connettore | Codice Produttore (MPN) | Descrizione Tecnica | Distributore e Codice Ordine |
| :--- | :--- | :--- | :--- | :--- |
| **Mainboard Base (`J5`)** | **Maschio ad Angolo Retto 90° con Leve** | **Würth Elektronik `61204021721`** (o serie WR-BHD / Harting `09185407324`) | Boxed Latched Header Maschio $2 \times 20$ pin passo $2.54\text{ mm}$, contatti ad angolo retto 90°, leve di ritenuta corte (*Short Latches*) per estrazione cartuccia | • **Mouser**: `710-61204021721`<br>• **DigiKey**: `732-5369-ND`<br>• **Farnell**: `1841457` |
| **Tutte le 12 Cartucce (`J1`)** | **Femmina ad Angolo Retto 90° a Bordo Scheda** | **Samtec `SSW-120-02-G-D-RA`**<br>*(o Harwin `M20-7812045` / Sullins `PPPC202LJBN-RC`)* | Connettore Femmina doppia fila $2 \times 20$ pin (40 poli) ad angolo retto 90°, passo $2.54\text{ mm}$, profilo basso, contatti placcati oro/stagno | • **Mouser**: `200-SSW12002GDRA`<br>• **DigiKey**: `SAM1040-20-ND`<br>• **Harwin**: `M20-7812045` |

> [!CAUTION]
> **Regola Meccanica di Allineamento a Filo**:
> - La battuta frontale in plastica della presa femmina `J1` deve trovarsi esattamente a **$Y = 0.00\text{ mm}$ (a filo del contorno fresato `Edge.Cuts`)**.
> - I pad THT devono risiedere a quota $Y = 12.57\text{ mm}$ (e $10.03\text{ mm}$ per la seconda fila), eliminando ogni sbalzo di vetronite che impedirebbe il completo innesto nel maschio della Mainboard.

---

## 4. Altri Connettori Specifici delle Cartucce

| Cartuccia | Funzione | Tipo Connettore | Codice Produttore (MPN) | Note di Acquisto e Montaggio |
| :--- | :--- | :--- | :--- | :--- |
| **#01 Commodore C2N** | Porta Datassette PET/VIC20/C64 | Connettore Card Edge a pettine passo $3.96\text{ mm}$ ($0.156"$) | **EDAC `306-006-520-102`** o **Sullins `EBC06DRAH`** | 6 pin superiori + 6 pin inferiori (12 contatti totali con polarizzatore a fessura) |
| **#09 TI-99/4A** | Porta Cassette Split D-Sub | Presa D-Sub DE-9 Femmina 90° | **Amphenol ICC `L77SDE09S`** o **TE `5747844-4`** | DE-9 femmina orizzontale a vaschetta metallica THT |
| **Tutte le 12 Cartucce (`J4` / `J3`)** | Header Ausiliario Banco Prova | Maschio dritto verticale passo $2.54\text{ mm}$ | **Molex `0022284063`** (o strip passo 2.54 mm standard) | Pin Header maschio $1 \times 06$ / $1 \times 07$ / $1 \times 09$ a passo $2.54\text{ mm}$ |

---

## 5. Connettori della Mainboard Base e UI Panel

| Scheda | Riferimento | Funzione | Codice Produttore (MPN) | Distributore e Codice Ordine |
| :--- | :---: | :--- | :--- | :--- |
| **Mainboard** | `J1` | Alimentazione e Dati USB-C | **GCT `USB4105-GF-A`** (16P Top Mount Horizontal) | • **Mouser**: `640-USB4105-GF-A`<br>• **DigiKey**: `2073-USB4105-GF-ACT-ND` |
| **Mainboard** | `J2` | Storage MicroSD Push-Pull | **Hirose `DM3D-SF`** | • **Mouser**: `798-DM3D-SF`<br>• **DigiKey**: `H122204CT-ND` |
| **Mainboard** | `J4` | Connessione UI Panel (20P) | **Würth `61202021621`** (Boxed Header Maschio 2x10) | • **Mouser**: `710-61202021621`<br>• **DigiKey**: `732-5347-ND` |
| **UI Panel** | `J1` | Ingresso da Mainboard (20P) | **Würth `61202021621`** (Boxed Header Maschio 2x10) | Collegato con cavo a nastro piatto IDC 20 poli (`Würth 61202023021`) |
