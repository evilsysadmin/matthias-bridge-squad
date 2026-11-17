# Matthias Bridge Squad

**ShadowOps arcade táctico**, versión inicial jugable, inspirado en la mecánica de puertas, rescate y jefe de Bridge Squad de noclipepe. Código y gráficos dibujados desde cero.

## Jugar

Juega en [GitHub Pages](https://evilsysadmin.github.io/matthias-bridge-squad/) cuando el despliegue esté activo, o abre `index.html` en Firefox/Chromium. El juego no requiere Internet, instalación, servidor ni dependencias.

- **Ratón o dedo:** desliza horizontalmente para dirigir la escuadra.
- **A/D o flechas:** mover a Matthias.
- **P o Escape:** pausa; **R:** reinicio; **M:** sonido.
- El escuadrón dispara automáticamente cuando está alineado con los enemigos o el prisionero.
- Cruza puertas verdes para sumar/multiplicar tropas: la puerta más próxima muestra una **previsión de tropas** (se recalcula si tu escuadrón cambia). Evita trampas, recoge cajas ATK y dispara a la jaula para rescatar al héroe.
- En la batalla final, esquiva el área marcada en rojo mientras disparas al jefe.

## Contenido

- 12 niveles desbloqueables con nombres y jefes distintos.
- Puertas de suma, multiplicación, sustracción y división.
- Enemigos, barriles, pinchos, mejoras de ataque, liberación de héroe y jefes que disparan.
- Hasta tres estrellas por nivel, récord de puntos y persistencia local (localStorage).
- Diseño adaptable para PC y móviles, controles táctiles y sonido sintetizado opcional.

## Desarrollo

El juego es autónomo y está incluido en `index.html` (Canvas 2D + JS + CSS). El workflow `.github/workflows/pages.yml` ejecuta las pruebas de Chromium en cada PR y push; solo despliega a GitHub Pages tras superarlas en `main`.

El progreso reside en `shadowops.mbs.progress.v1` y el ajuste de sonido en `shadowops.mbs.settings.v1`.

El juego no copia el código, imágenes ni otros activos del original. El alcance es una primera versión jugable, pendiente de playtesting, iteraciones de balance y posible integración con el ecosistema ShadowOps.
### Ejecutar el smoke test local

```sh
python -m pip install playwright
python -m playwright install chromium
python smoke_test.py
```

Comprueba menús, controles, pausa, pronóstico de puertas, victoria/estrellas y una ruta ganadora por nivel en móvil y escritorio.
