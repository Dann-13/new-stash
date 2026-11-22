# Changelog

## 0.3.0

- Panel de DeepSeek: saldo total, moneda y disponibilidad, actualizado cada 60 s.
- Clave solo por variable de entorno `DEEPSEEK_API_KEY`; nunca se guarda ni se registra.
- Consulta HTTPS en hilo aparte: la UI no espera la red. Sin clave, panel oculto y cero conexiones.
- Errores de red o HTTP con mensajes genéricos que no incluyen la clave.

## 0.2.0

- Costo por día en la gráfica de tokens (línea `▁▂▃` bajo las barras).
- Presupuesto mensual opcional en `config.toml`, con aviso al 80 % y al 100 %.
- Línea de sesión actual: sesión con actividad más reciente, con tokens, costo y tiempo.
- Tecla `e`: exporta CSV (por día) y Markdown (resumen) a la carpeta actual.
- Archivo `config.toml` multiplataforma (`~/.config` en Linux, `%APPDATA%` en Windows).
- CI en GitHub Actions: pruebas y `ruff` en Ubuntu y Windows, Python 3.11 y 3.12.
- Rendimiento: solo se relee la base cuando cambia `opencode.db` o su `-wal`.
- Compatibilidad Linux: ruta de datos respeta `XDG_DATA_HOME`, Python 3.11+.
- Corrección: la ruta de la base SQLite se abre bien aunque tenga espacios o `#`.

## 0.1.0

- Primer MVP: tarjetas, gráfica diaria, heatmap, tablas por modelo y agente.
