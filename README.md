# Matthias Bridge Squad

**ShadowOps arcade táctico**, versión inicial jugable, inspirado en la mecánica de puertas, rescate y jefe de Bridge Squad de noclipepe. Código y gráficos dibujados desde cero.

## Jugar

Abre `index.html` en Firefox/Chromium. No requiere Internet, instalación, servidor ni dependencias.

- **Ratón o dedo:** desliza horizontalmente para dirigir la escuadra.
- **A/D o flechas:** mover a Matthias.
- **P o Escape:** pausa; **R:** reinicio; **M:** sonido.
- El escuadrón dispara automáticamente cuando está alineado con los enemigos o el prisionero.
- Cruza puertas verdes para sumar/multiplicar tropas, evita trampas, recoge cajas ATK y dispara a la jaula para rescatar al héroe.
- En la batalla final, esquiva el área marcada en rojo mientras disparas al jefe.

## Contenido

- 12 niveles desbloqueables con nombres y jefes distintos.
- Puertas de suma, multiplicación, sustracción y división.
- Enemigos, barriles, pinchos, mejoras de ataque, liberación de héroe y jefes que disparan.
- Hasta tres estrellas por nivel, récord de puntos y persistencia local (localStorage).
- Diseño adaptable para PC y móviles, controles táctiles y sonido sintetizado opcional.

## Desarrollo

El juego es autónomo y está incluido en `index.html` (Canvas 2D + JS + CSS). Pensado para servir desde cualquier hosting estático, incluido GitHub Pages y Cloudflare Pages.

El progreso reside en `shadowops.mbs.progress.v1` y el ajuste de sonido en `shadowops.mbs.settings.v1`.

El juego no copia el código, imágenes ni otros activos del original. El alcance es una primera versión jugable, pendiente de playtesting, iteraciones de balance y posible integración con el ecosistema ShadowOps.
