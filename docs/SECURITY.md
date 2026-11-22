# Seguridad y privacidad

Este proyecto maneja datos de uso y, opcionalmente, una clave de API. Las reglas
de abajo son innegociables.

## Base de datos: solo lectura

- `opencode.db` se abre con `file:` URI y `mode=ro`. **Nunca se escribe.**
- No se modifican ni borran datos de OpenCode. Solo se leen y agregan.
- La ruta respeta `XDG_DATA_HOME` y se construye con `as_uri()` (soporta espacios
  y `#` sin romper la URI).

## Clave de DeepSeek

- Llega **solo** por la variable de entorno `DEEPSEEK_API_KEY`.
- **Nunca** se guarda en archivos, ni se imprime en pantalla, ni se registra en
  logs, ni se incluye en mensajes de error o trazas.
- En `providers/deepseek.py` los errores usan `raise ... from None` para no
  encadenar la traza original (que podría contener la petición con la clave).
- Los mensajes de error son genéricos y pasan por `i18n.t()`.
- Sin clave, el panel está oculto y **no se hace ninguna conexión**.

## Red

- Único destino permitido: `https://api.deepseek.com` (endpoint `/user/balance`).
- Solo **HTTPS**. El código rechaza cualquier URL que no empiece por `https://`.
- Solo lectura de saldo. No se envían tokens de uso ni datos de sesiones.
- La consulta corre en un hilo aparte con timeout; la UI nunca espera la red.
- **Sin telemetría.** No se envía nada a ningún otro servidor.

## Qué se exporta

- La tecla `e` abre un diálogo para **elegir la carpeta** y escribe ahí CSV y
  Markdown. El destino inicial sale de `--export-dir`, o `export_dir` en
  `config.toml`, o la carpeta de trabajo actual. La app recuerda la última usada.
- La carpeta se crea si no existe (`mkdir parents=True`); si no se puede usar, se
  avisa y no se escribe nada. Solo se escriben los archivos de export, nada más.
- Contienen agregados de uso (tokens, costo, modelos). No contienen la clave.
- Los archivos generados `opencode-usage-*.csv` / `*.md` están en `.gitignore`:
  no deben commitearse.

## Presupuesto

- El presupuesto mensual solo informa (aviso al 80 % y 100 %). **Nunca bloquea**
  ni modifica nada. Vive en `config.toml` del usuario, no en el repo.

## Reportar un problema

Si encuentras una fuga de la clave o una escritura accidental en la base, trátalo
como bug crítico: corrige antes que cualquier feature y añade un test que lo cubra.
