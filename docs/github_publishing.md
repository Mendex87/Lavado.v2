# GitHub Publishing Guide

## Objetivo
Subir este proyecto a GitHub para poder continuar el desarrollo desde otra PC sin depender del VPS como único entorno.

## Qué sí conviene subir
- `backend/`
- `db/`
- `docs/`
- `app-preview/` (si quieres conservar la preview)
- SVGs / assets del proyecto que sí formen parte del producto

## Qué NO conviene subir
Quedó cubierto por `.gitignore`:
- archivos personales del workspace OpenClaw
- memoria conversacional
- secretos / `.env`
- caches / entornos locales

## Flujo recomendado
### 1. Crear repo vacío en GitHub
Ejemplo: `planta-lavado-fracking-app`

### 2. En el VPS o en tu PC, conectar el remoto
```bash
cd /data/.openclaw/workspace
git remote add origin <TU-URL-GIT>
```

Si ya existe `origin`:
```bash
git remote set-url origin <TU-URL-GIT>
```

### 3. Confirmar qué entra al repo
```bash
git status
```

### 4. Subir rama principal
```bash
git push -u origin master
```

## Flujo después desde otra PC
```bash
git clone <TU-URL-GIT>
cd <repo>
```

Luego:
- corres backend local
- pruebas UI local
- conectas tu PLC local
- haces commit/push

## Estrategia sugerida
- **GitHub**: fuente central del código
- **PC del taller**: desarrollo y pruebas con PLC
- **VPS**: demo remota, continuidad y despliegue

## Recomendación práctica
Antes del primer push, revisar `git status` y asegurarse de que no aparezcan:
- tokens
- contraseñas
- archivos personales
- notas privadas
