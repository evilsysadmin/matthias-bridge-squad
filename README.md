# Matthias Bridge Squad

**ShadowOps arcade táctico**, versión inicial jugable, inspirado en la mecánica de puertas, rescate y jefe de Bridge Squad de noclipepe. Código y gráficos dibujados desde cero.

## Jugar

La dirección de producción solicitada es **https://bridgesquad.shadowops.dpdns.org/**, pendiente de activación autenticada por ShadowOps Infra. El juego todavía puede ejecutarse sin conexión abriendo `index.html` en Firefox/Chromium; eso no equivale a acceder a la versión protegida.

- **Ratón o dedo:** desliza horizontalmente para dirigir la escuadra.
- **A/D o flechas:** mover a Matthias.
- **P o Escape:** pausa; **R:** reinicio; **M:** sonido.
- El escuadrón dispara automáticamente cuando está alineado con los enemigos o el prisionero.
- **Tiradores enemigos:** cuando entras en su alcance, fijan tu posición y señalan con una marca roja el punto de impacto. Dispones de un segundo para esquivarla, o puedes neutralizar al enemigo antes de que abra fuego. El disparo no te persigue después de fijarte.
- Cruza puertas verdes para sumar/multiplicar tropas: la puerta más próxima muestra una **previsión de tropas** (se recalcula si tu escuadrón cambia). Evita trampas, recoge cajas ATK y dispara a la jaula para rescatar al héroe. **El héroe liberado acompaña a Matthias y bloquea exactamente una salva de tirador o artillería**: el indicador `🛡 HÉROE · ESCUDO LISTO` desaparece al gastarlo. No bloquea barriles ni pinchos, y recuperarlo requiere rescatarlo de nuevo en otra partida.
- En la batalla final, **centra la escuadra para tener al jefe en la línea de tiro**. Fuera del carril central el daño se reduce hasta cero. En cuanto aparezca el aviso rojo de artillería, muévete al lateral para esquivarlo y vuelve al centro para atacar. El texto «EN MIRA» te confirma cuándo disparas con fuerza.

## Contenido

- 12 niveles desbloqueables con nombres y jefes distintos.
- Puertas de suma, multiplicación, sustracción y división.
- Enemigos, barriles, pinchos, mejoras de ataque, liberación de héroe y jefes que disparan.
- Hasta tres estrellas por nivel, récord de puntos y persistencia local (localStorage).
- Diseño adaptable para PC y móviles, controles táctiles y sonido sintetizado opcional.

## Desarrollo

El juego es autónomo y está incluido en `index.html` (Canvas 2D + JS + CSS). El workflow `.github/workflows/pages.yml` **solo ejecuta pruebas Chromium**, sin publicación pública en GitHub Pages. La entrega autenticada en Cloudflare es responsabilidad exclusiva de `evilsysadmin/shadowops-infra`. Un despliegue anterior de GitHub Pages, de existir, requiere retirada explícita en Settings → Pages para eliminar el acceso alternativo.

En la URL protegida el progreso local reside en `shadowops.mbs.progress.v1:<UUIDv4 verificado por el edge>`, separado por cuenta en el navegador; en modo offline conserva `shadowops.mbs.progress.v1`. El sonido sigue en `shadowops.mbs.settings.v1`. **No hay todavía sincronización cloud** entre dispositivos ni importación automática del progreso offline a una cuenta.

El juego no copia el código, imágenes ni otros activos del original. El alcance es una primera versión jugable, pendiente de playtesting, iteraciones de balance y posible integración con el ecosistema ShadowOps.
### Ejecutar el smoke test local

```sh
python -m pip install playwright
python -m playwright install chromium
python smoke_test.py
```

Comprueba menús, controles, pausa, pronóstico de puertas, victoria/estrellas y una ruta ganadora por nivel en móvil y escritorio. También verifica que disparar desde fuera del carril no daña al jefe y que el regreso al centro sí permite atacar, con esquivas tácticas deterministas en los 12 niveles. La prueba de tiradores comprueba impacto contra un jugador inmóvil, esquiva durante el aviso y cancelación del disparo al eliminar al enemigo.

## Candidato de release protegido

Tras superar el smoke de Chromium de `main`, CI genera **solo un artefacto privado de GitHub Actions** llamado `bridgesquad-private-release-<SHA>` (retención 30 días) con `index.html` byte-a-byte y `release.json` que ancla repositorio, commit, SHA-256, tamaño y audiencia de Identity. Se comprueba la política de empaquetado en CI sin secretos. **No despliega a GitHub Pages ni a Cloudflare**, no verifica Identity y no constituye una URL jugable. ShadowOps Infra debe admitir exactamente ese SHA/digest en un futuro despliegue autenticado.
