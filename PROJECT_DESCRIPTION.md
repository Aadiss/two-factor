# Aplikacja Uwierzytelniania Dwuskładnikowego - Opis Projektu

## Czym jest ten projekt?

To aplikacja internetowa, która dodaje dodatkową warstwę bezpieczeństwa do kont użytkowników, wymagając **dwóch różnych dowodów tożsamości** przed udostępnieniem dostępu. Zamiast samego wpisywania hasła, użytkownicy muszą również udowodnić, że są tymi, za których się podają, używając drugiej metody.

Można to porównać do banku - aby wypłacić pieniądze, potrzebujesz zarówno karty bankowej (coś, co posiadasz), jak i kodu PIN (coś, co znasz). Ta aplikacja działa w podobny sposób.

---

## Stack Technologiczny (Jakie narzędzia zostały użyte do budowy)

### Backend („mózg" aplikacji)

| Technologia | Co robi |
|-------------|---------|
| **Python** | Język programowania używany do pisania logiki serwera |
| **FastAPI** | Framework pomagający budować API sieciowe („posłaniec" między frontendem a backendem) |
| **MongoDB** | Baza danych przechowująca konta użytkowników i ustawienia 2FA |
| **Docker** | Narzędzie pakujące aplikację tak, aby działała tak samo na każdym komputerze |

### Frontend (Co użytkownik widzi i z czym interaguje)

| Technologia | Co robi |
|-------------|---------|
| **Vue.js 3** | Framework do budowania interfejsu użytkownika (przyciski, formularze, strony) |
| **Vite** | Narzędzie kompilujące i serwujące pliki frontendu |
| **Axios** | Biblioteka wysyłająca żądania z frontendu do backendu |
| **SimpleWebAuthn** | Biblioteka obsługująca komunikację kluczy bezpieczeństwa (passkey) z przeglądarką |

### Infrastruktura

| Technologia | Co robi |
|-------------|---------|
| **Docker Compose** | Zarządza wieloma usługami (baza danych, backend, frontend) pracującymi razem |
| **Nginx** | Serwer WWW serwujący pliki frontendu w środowisku produkcyjnym |

---

## Metody Uwierzytelniania Dwuskładnikowego

### Metoda 1: Aplikacja Autentykująca (TOTP)

**Czym jest TOTP?**
TOTP oznacza „Time-based One-Time Password" (Jednorazowe Hasło oparte na Czasie). Jest to system generujący **6-cyfrowy kod, który zmienia się co 30 sekund**.

**Jak to działa (krok po kroku):**

1. **Konfiguracja:**
   - Użytkownik klika „Skonfiguruj aplikację autentykującą" na pulpicie
   - Aplikacja generuje **klucz tajny** (długi ciąg znaków) unikalny dla danego użytkownika
   - Tworzony jest **kod QR** (kwadratowy kod kreskowy) zawierający ten klucz tajny
   - Użytkownik skanuje kod QR aplikacją autentykującą na telefonie:
     - Microsoft Authenticator
     - Google Authenticator
     - Authy
     - Lub dowolną aplikacją obsługującą TOTP
   - Aplikacja na telefonie zna teraz klucz tajny

2. **Podczas logowania:**
   - Użytkownik wprowadza nazwę użytkownika i hasło (pierwszy składnik)
   - Aplikacja prosi o 6-cyfrowy kod z aplikacji autentykującej (drugi składnik)
   - Zarówno aplikacja, jak i aplikacja na telefonie używają tego samego klucza tajnego + bieżącego czasu, aby obliczyć ten sam 6-cyfrowy kod
   - Jeśli kody się zgadzają, użytkownik otrzymuje dostęp

3. **Dlaczego jest to bezpieczne:**
   - Kod zmienia się co 30 sekund, więc nawet jeśli ktoś go zobaczy, będzie bezużyteczny wkrótce potem
   - Klucz tajny nigdy nie opuszcza telefonu (nie jest wysyłany przez internet)

---

### Metoda 2: Klucze Bezpieczeństwa / Passkey

**Czym są Passkey?**
Passkey to fizyczne urządzenia bezpieczeństwa (jak **YubiKey**) lub wbudowane w urządzenie authenticatory (jak **Touch ID** lub **Face ID**), które potwierdzają Twoją tożsamość za pomocą kryptografii.

**Jak to działa (krok po kroku):**

1. **Konfiguracja (Rejestracja):**
   - Użytkownik klika „Skonfiguruj klucze bezpieczeństwa" na pulpicie
   - Aplikacja wysyła „wyzwanie" (losową liczbę) do przeglądarki użytkownika
   - Przeglądarka prosi urządzenie bezpieczeństwa o podpisanie wyzwania
   - Urządzenie bezpieczeństwa tworzy **parę kluczy**:
     - **Klucz prywatny** - pozostaje na urządzeniu, nigdy nie jest udostępniany
     - **Klucz publiczny** - wysyłany do aplikacji w celu przechowania
   - Aplikacja przechowuje klucz publiczny w bazie danych

2. **Podczas logowania (Uwierzytelnianie):**
   - Użytkownik wprowadza nazwę użytkownika i hasło (pierwszy składnik)
   - Aplikacja prosi użytkownika o dotknięcie/włożenie klucza bezpieczeństwa
   - Przeglądarka prosi urządzenie bezpieczeństwa o podpisanie nowego wyzwania za pomocą klucza prywatnego
   - Aplikacja weryfikuje podpis za pomocą przechowanego klucza publicznego
   - Jeśli jest prawidłowy, użytkownik otrzymuje dostęp

3. **Dlaczego jest to bezpieczne:**
   - Klucz prywatny nigdy nie opuszcza urządzenia
   - Wyzwanie jest za każdym razem inne, co uniemożliwia ataki typu replay
   - Nawet jeśli ktoś ukradnie klucz publiczny, nie może go użyć do zalogowania się

---

## Przepływ Użytkownika (Jak ktoś korzysta z aplikacji)

### 1. Tworzenie Konta (Rejestracja)
- Użytkownik przechodzi na stronę rejestracji
- Wprowadza nazwę użytkownika i hasło
- Hasło jest **haszowane** (zamieniane na nieczytelny format) przed zapisaniem
- Użytkownik jest przekierowywany na pulpit

### 2. Logowanie (Pierwszy raz, bez ustawionego 2FA)
- Użytkownik wprowadza nazwę użytkownika i hasło
- Aplikacja sprawdza, czy hasło zgadza się z zapisanym hashem
- Jeśli jest poprawne, użytkownik loguje się bezpośrednio

### 3. Konfiguracja 2FA
- Z poziomu pulpitu użytkownik może wybrać:
  - **Aplikację autentykującą** - skanuje kod QR telefonem
  - **Klucze bezpieczeństwa** - rejestruje fizyczny klucz
- Użytkownik może skonfigurować obie metody jako kopię zapasową

### 4. Logowanie (Z włączonym 2FA)
- Użytkownik wprowadza nazwę użytkownika i hasło
- Aplikacja wykrywa, że 2FA jest włączone
- Aplikacja prosi o drugi składnik:
  - **TOTP**: Użytkownik otwiera aplikację autentykującą i wpisuje 6-cyfrowy kod
  - **Passkey**: Użytkownik dotyka klucza bezpieczeństwa
- Jeśli oba składniki zostaną zweryfikowane, użytkownik otrzymuje dostęp

---

## Funkcje Bezpieczeństwa

| Funkcja | Opis |
|---------|------|
| **Haszowanie Haseł** | Hasła są przechowywane jako nieczytelne hashe przy użyciu bcrypt |
| **Tokeny JWT** | Po zalogowaniu użytkownicy otrzymują tymczasowy cyfrowy „przepust" (JSON Web Token) |
| **TOTP z 30-sekundowym oknem** | Kodty są ważne tylko przez krótki czas |
| **Challenge-Response** | Klucze bezpieczeństwa używają wyzwań kryptograficznych, których nie można ponownie wykorzystać |
| **Tymczasowe Tokeny 2FA** | Podczas weryfikacji 2FA używany jest krótkotrwały token (wygasa po 10 minutach) |

---

## Struktura Projektu (Organizacja plików)

```
two-factor/
├── backend/                    # Kod serwera
│   ├── app/
│   │   ├── main.py            # Punkt wejścia aplikacji
│   │   ├── config.py          # Ustawienia (URL bazy danych, tajne klucze, itp.)
│   │   ├── database.py        # Połączenie z bazą danych
│   │   ├── models/            # Struktury danych (użytkownik, itp.)
│   │   ├── routes/            # Punkty końcowe API (o co frontend może prosić)
│   │   │   ├── auth.py        # Logowanie i rejestracja
│   │   │   └── two_factor.py  # Konfiguracja i weryfikacja 2FA
│   │   └── services/          # Logika biznesowa
│   │       ├── auth_service.py     # Haszowanie haseł, tokeny JWT
│   │       ├── totp_service.py     # Generowanie i weryfikacja TOTP
│   │       └── passkey_service.py  # Obsługa kluczy bezpieczeństwa
│   └── requirements.txt       # Zależności Pythona
├── frontend/                   # Interfejs użytkownika
│   ├── src/
│   │   ├── views/             # Strony
│   │   │   ├── LoginView.vue      # Strona logowania
│   │   │   ├── RegisterView.vue   # Strona rejestracji
│   │   │   ├── DashboardView.vue  # Pulpit użytkownika
│   │   │   ├── TOTPSetup.vue      # Konfiguracja aplikacji autentykującej
│   │   │   └── PasskeySetup.vue   # Konfiguracja klucza bezpieczeństwa
│   │   └── stores/            # Zarządzanie stanem
│   └── package.json           # Zależności JavaScript
├── docker-compose.yml         # Orkiestracja usług
└── README.md                  # Szybki start
```

---

## Punkty Końcowe API (Trasy komunikacji)

To adresy URL, których frontend używa do komunikacji z backendem:

### Uwierzytelnianie
- `POST /api/auth/register` - Utworzenie nowego konta
- `POST /api/auth/login` - Logowanie (zwraca informację, czy potrzebne jest 2FA)
- `GET /api/auth/me` - Uzyskanie informacji o bieżącym użytkowniku

### TOTP (Aplikacja Autentykująca)
- `POST /api/2fa/totp/setup` - Wygenerowanie kodu QR i klucza tajnego
- `POST /api/2fa/totp/verify` - Weryfikacja konfiguracji pierwszym kodem
- `POST /api/2fa/totp/validate` - Walidacja kodu podczas logowania
- `DELETE /api/2fa/totp` - Wyłączenie aplikacji autentykującej

### Passkey (Klucze Bezpieczeństwa)
- `POST /api/2fa/passkey/register/begin` - Rozpoczęcie rejestracji
- `POST /api/2fa/passkey/register/complete` - Zakończenie rejestracji
- `POST /api/2fa/passkey/authenticate/begin` - Rozpoczęcie uwierzytelniania
- `POST /api/2fa/passkey/authenticate/complete` - Zakończenie uwierzytelniania
- `GET /api/2fa/passkey/list` - Lista zarejestrowanych kluczy
- `DELETE /api/2fa/passkey/:id` - Usunięcie klucza

---

## Szczegóły Implementacji (Jak to działa w kodzie)

### Implementacja TOTP (Aplikacje Autentykujące)

**Używana biblioteka:** `pyotp` (Python)

Biblioteka `pyotp` to standardowa implementacja TOTP w Pythonie. Oto jak jest używana w projekcie:

#### Generowanie sekretu
```python
import pyotp

def generate_totp_secret() -> str:
    return pyotp.random_base32()
```
- `pyotp.random_base32()` generuje losowy 32-znakowy klucz w formacie Base32 (litery A-Z i cyfry 2-7)
- Ten klucz jest przechowywany w bazie danych i udostępniany aplikacji na telefonie

#### Tworzenie URI do skanowania
```python
def get_totp_uri(secret: str, username: str) -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="TwoFactorApp"
    )
```
- Funkcja tworzy URI w formacie `otpauth://totp/...`
- Zawiera nazwę użytkownika i nazwę aplikacji ("TwoFactorApp")
- URI jest kodowany w QR kodzie do skanowania przez telefon

#### Generowanie kodu QR
```python
import qrcode
import base64

def generate_qr_code_base64(uri: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Konwersja do base64 do wyświetlenia w przeglądarce
    return base64.b64encode(img_bytes).decode()
```
- Biblioteka `qrcode` generuje obraz QR
- Obraz jest konwertowany na base64 (tekst) aby można go było wyświetlić w przeglądarce

#### Weryfikacja kodu
```python
def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
```
- `TOTP(secret)` tworzy obiekt TOTP z kluczem tajnym
- `verify(code, valid_window=1)` sprawdza, czy kod jest poprawny
- `valid_window=1` oznacza, że akceptuje kody z poprzedniej i następnej rundy (±30 sekund)
- Biblioteka automatycznie oblicza kod na podstawie bieżącego czasu i porównuje go z podanym kodem

---

### Implementacja Passkey (Klucze Bezpieczeństwa)

**Używane biblioteki:**
- **Backend:** `fido2` (Python) - implementacja serwera WebAuthn
- **Frontend:** `@simplewebauthn/browser` (JavaScript) - implementacja klienta w przeglądarce

#### Standard WebAuthn
Passkey opiera się na standardzie **WebAuthn** (Web Authentication API), który jest wbudowany w nowoczesne przeglądarki. Standard ten definiuje, jak przeglądarki i urządzenia bezpieczeństwa komunikują się z serwerami.

#### Inicjalizacja serwera FIDO2
```python
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity

rp = PublicKeyCredentialReEntity(id="localhost", name="TwoFactorApp")
server = Fido2Server(rp, verify_origin=verify_origin)
```
- `PublicKeyCredentialRpEntity` definiuje "Relying Party" (serwer ufający) - czyli naszą aplikację
- `Fido2Server` to główny obiekt serwera obsługujący rejestrację i uwierzytelnianie
- `verify_origin` sprawdza, czy żądanie pochodzi z dozwolonego adresu URL

#### Rejestracja klucza (krok 1 - generowanie opcji)
```python
from fido2.webauthn import PublicKeyCredentialUserEntity

def generate_registration_options(username: str, user_id: str) -> dict:
    user = PublicKeyCredentialUserEntity(
        id=user_id.encode(),
        name=username,
        display_name=username
    )
    
    options, state = server.register_begin(
        user,
        [],  # lista istniejących kluczy (do unikania duplikatów)
        user_verification="discouraged"
    )
    return {"options": options_dict, "_state": state}
```
- `register_begin()` tworzy wyzwanie (challenge) dla przeglądarki
- Zwraca obiekt `options` z danymi do wysłania do przeglądarki
- Zwraca `state` (stan), który jest przechowywany na serwerze do weryfikacji

#### Rejestracja klucza (krok 2 - finalizacja)
```python
def complete_registration(state_b64: str, credential_data: dict) -> dict:
    state = json.loads(base64.b64decode(state_b64))
    auth_data = server.register_complete(state, credential_data)
    
    return {
        "credential_id": credential_id,
        "public_key": public_key,
        "credential_data": credential_data,
        "sign_count": auth_data.counter
    }
```
- `register_complete()` weryfikuje odpowiedź przeglądarki
- Sprawdza, czy podpis jest poprawny
- Zwraca dane uwierzytelniające (credential data) do przechowania w bazie danych
- Zawiera licznik podpisów (sign_count) do wykrywania ataków

#### Uwierzytelnianie (krok 1 - generowanie opcji)
```python
def generate_authentication_options(credentials: list) -> dict:
    attested_creds = []
    for cred in credentials:
        blob = cred.get("credential_data", "")
        if blob:
            attested_creds.append(AttestedCredentialData(base64.b64decode(blob)))
    
    options, state = server.authenticate_begin(
        credentials=attested_creds or None,
        user_verification="discouraged"
    )
    return {"options": options_dict, "_state": state}
```
- `authenticate_begin()` tworzy wyzwanie dla uwierzytelniania
- Lista `credentials` zawiera zarejestrowane klucze użytkownika
- Przeglądarka wybiera odpowiedni klucz i prosi urządzenie o podpisanie

#### Uwierzytelnianie (krok 2 - finalizacja)
```python
def complete_authentication(state_b64: str, full_response: dict, 
                          credential_data_blob: str, current_count: int) -> dict:
    state = json.loads(base64.b64decode(state_b64))
    cred = AttestedCredentialData(base64.b64decode(credential_data_blob))
    
    server.authenticate_complete(state, [cred], full_response)
    return {"verified": True, "new_count": current_count + 1}
```
- `authenticate_complete()` weryfikuje podpis z urządzenia
- Sprawdza, czy podpis jest poprawny i czy licznik się zgadza
- Zwiększa licznik, aby wykryć potencjalne ataki typu replay

---

### Komunikacja Frontend-Backend

#### Strona rejestracji TOTP (Vue.js)
```javascript
// Frontend generuje kod QR
const response = await axios.post('/api/2fa/totp/setup')
const qrCodeBase64 = response.data.qr_code
// Wyświetla kod QR w HTML
<img :src="'data:image/png;base64,' + qrCodeBase64" />
```

#### Strona rejestracji Passkey (Vue.js + SimpleWebAuthn)
```javascript
// Frontend rozpoczyna rejestrację
const { options, state } = await axios.post('/api/2fa/passkey/register/begin')

// SimpleWebAuthn wywołuje WebAuthn API w przeglądarce
const credential = await startRegistration(options)

// Frontend finalizuje rejestrację
await axios.post('/api/2fa/passkey/register/complete', {
    id: credential.id,
    rawId: credential.rawId,
    response: credential.response,
    state: state
})
```

#### Przepływ danych podczas logowania z 2FA
```
Użytkownik → Frontend → Backend
    │              │           │
    │  Wprowadza   │           │
    │  login/hasło │           │
    │──────────────│───────────│
    │              │           │
    │              │  Sprawdza │
    │              │  hasło    │
    │              │───────────│
    │              │           │
    │              │  Zwraca   │
    │              │  "potrzebne│
    │              │  2FA"    │
    │◄─────────────│───────────│
    │              │           │
    │  Wprowadzuje │           │
    │  kod 2FA     │           │
    │──────────────│───────────│
    │              │           │
    │              │  Weryfikuje│
    │              │  kod 2FA  │
    │              │───────────│
    │              │           │
    │              │  Zwraca   │
    │              │  token    │
    │◄─────────────│───────────│
```

---

### Bezpieczeństwo Implementacji

| Aspekt | Jak jest zabezpieczone |
|--------|------------------------|
| **Przechowywanie sekretów TOTP** | Sekret jest przechowywany w MongoDB, nigdy nie jest wysyłany do przeglądarki |
| **Kody QR** | Zawierają tylko URI do skanowania, nie sam sekret w formie tekstowej |
| **Klucze prywatne Passkey** | Nigdy nie opuszczają urządzenia (YubiKey, Touch ID, itp.) |
| **Wyzwania (Challenges)** | Są losowe i jednorazowe, zapobiegają atakom typu replay |
| **Liczniki podpisów** | Wykrywają, czy ktoś próbuje użyć tego samego podpisu wielokrotnie |
| **Tymczasowe tokeny** | Tokeny 2FA wygasa po 10 minutach, tokeny sesji po 60 minutach |

---

## Podsumowanie

Ten projekt pokazuje, jak działa **uwierzytelnianie dwuskładnikowe** w praktyce, implementując dwie popularne metody:

1. **TOTP (Aplikacje Autentykujące)** - Używa biblioteki `pyotp` do generowania i weryfikacji kodów opartych na czasie
2. **Passkey (Klucze Bezpieczeństwa)** - Używa biblioteki `fido2` do implementacji standardu WebAuthn z fizycznymi kluczami bezpieczeństwa

Aplikacja została zbudowana przy użyciu nowoczesnych technologii internetowych i przestrzega najlepszych praktyk bezpieczeństwa, takich jak haszowanie haseł, uwierzytelnianie oparte na tokenach i wyzwania kryptograficzne.