# Guía rápida: ejecutar Prosil en PC local (Windows)

## Objetivo
Levantar la app en tu PC del taller con código del repo, sin depender de la VPS.

---

## 1) Requisitos

- Python 3.11+ (ideal 3.12)
- Git
- Acceso de red al PLC S7-1200
- (Opcional) entorno virtual de Python

Verificación rápida en CMD:

```bat
python --version
git --version
```

---

## 2) Clonar/actualizar repo

```bat
cd "C:\Users\TU_USUARIO\Desktop"
git clone https://github.com/Mendex87/Prosil.git
cd Prosil
```

Si ya lo tenés:

```bat
cd "C:\ruta\a\Prosil"
git pull origin master
```

---

## 3) Backend local

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Configurar `.env` de backend (si aplica en tu versión):

- `HOST=127.0.0.1`
- `PORT=8010`

Levantar backend:

```bat
uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

Probar health:

```bat
curl http://127.0.0.1:8010/api/v1/health
```

Debe responder `{"ok":true}`.

---

## 4) Poller PLC en PC

En otra terminal:

```bat
cd "C:\ruta\a\Prosil\backend"
.venv\Scripts\activate
python -m plc_poller.main
```

### Variables clave (`backend\plc_poller\env.example` / `.env`)

- `PLC_HOST=192.168.10.77`
- `PLC_RACK=0`
- `PLC_SLOT=1`
- `BACKEND_URL=http://127.0.0.1:8010/api/v1`
- `PLC_POLL_INTERVAL_SECONDS=0.5`

### Mapping esperado (`backend\plc_poller\mapping.example.json`)

Usar el mapping acordado (L1/L2 + `l2_input_tph_a` y `l2_input_tph_b` en DB14).

---

## 5) Frontend preview local

Abrir en navegador:

- `http://127.0.0.1:8010/app-preview/`

En login, API base URL:

- `http://127.0.0.1:8010/api/v1`

---

## 6) Checklist de validación mínima

1. Backend health OK
2. Poller sin errores de conexión Snap7
3. `GET /api/v1/measurements/latest` devuelve canales de L1/L2
4. Dashboard muestra datos reales (no fallback)
5. L2:
   - `simple` => protagonista = A
   - `blend` => protagonista = A+B

---

## 7) Problemas típicos

### A) `S7ConnectionError: TCP connection failed`
- Revisar IP del PLC, rack/slot
- Verificar red local (misma subred / rutas)

### B) Dashboard en Backend OFF
- Confirmar API base URL correcta (`/api/v1` en local)
- Verificar backend levantado en 8010

### C) No se ven cambios visuales
- Forzar recarga `Ctrl + F5`
- Revisar que estés en la URL local correcta

---

## 8) Comando rápido de arranque (resumen)

Terminal 1 (backend):

```bat
cd C:\ruta\a\Prosil\backend
.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

Terminal 2 (poller):

```bat
cd C:\ruta\a\Prosil\backend
.venv\Scripts\activate
python -m plc_poller.main
```

Navegador:

- `http://127.0.0.1:8010/app-preview/`

---

## Nota operativa
Cuando cierres versión funcional en VPS, con `git pull` en PC + `.env` correctos + dependencias instaladas, ya podés correr local sin problema.
