# Crecimiento económico y alternancia en América del Sur

Testea dos hipótesis con 90 elecciones presidenciales (10 países, 1983-2025):

1. **Umbral:** existe un crecimiento promedio en los 4 años previos a la elección
   por debajo del cual el partido incumbente tiende a perder.
2. **Frenazo / recesión:** una desaceleración o una recesión en los 2 años previos
   aumenta la probabilidad de que el incumbente pierda.

## Cómo correrlo

```bash
pip install pandas numpy statsmodels matplotlib scipy
python construir_datos.py   # baja el PIB y arma data/base_analisis.csv
python analisis.py          # escribe resultados.txt y figuras/
```

## Datos

| Archivo | Contenido |
|---|---|
| `data/elecciones.csv` | Base codificada a mano: incumbente, ganador, `alternancia` (1 = perdió el partido de gobierno), `presidente_candidato` (1 = el presidente en ejercicio buscaba la reelección), `caso_especial` (gobiernos interinos y elecciones anticipadas). |
| `data/pib_crecimiento.csv` | Crecimiento del PIB real (% anual). Hasta 2022 viene del Maddison Project 2023 (vía Our World in Data); 2023 y 2024 se cargaron a mano con cifras oficiales o del FMI. |
| `data/base_analisis.csv` | Las dos cosas cruzadas. |

**Convención temporal:** para una elección en el año *t* se usan los años
calendario *t-4* a *t-1*. "Últimos 2 años" son *t-2* y *t-1*.

**Qué quedó afuera:** Venezuela después de 2013 (elecciones no competitivas),
Perú 2000 (fraude), Bolivia 2019 (anulada), Perú 2026 (sin datos de PIB 2025),
y las primeras elecciones tras cada dictadura (no hay partido civil incumbente).
Guyana y Surinam no están.

## Resultados

### Hipótesis 1: se confirma; el umbral está en torno a 4-5% anual

La alternancia es lo normal en la región: pasa en el 59% de las elecciones. Al
ordenarlas por crecimiento promedio, la proporción baja a medida que la economía
crece más:

| Crecimiento promedio 4 años | Alternancia |
|---|---|
| < 1% | 80% (16/20) |
| 1-2% | 67% (6/9) |
| 2-3% | 73% (8/11) |
| 3-4% | 65% (11/17) |
| 4-5% | 47% (9/19) |
| > 5% | 21% (3/14) |

El corte que mejor separa los dos grupos está en **≈ 4,5% anual**. Debajo de ese
nivel el incumbente pierde el 71% de las veces; encima, sólo el 25%. La
diferencia es estadísticamente significativa (p = 0,003). Para calcular ese
p-valor se repitió todo el procedimiento 5.000 veces con los resultados
mezclados al azar dentro de cada país, así que ya descuenta que el umbral se
"buscó" en los datos y que algunos países alternan más que otros.

**Esto es lo que plantea la hipótesis: cuando el crecimiento promedio cae debajo
de ≈ 4,5%, la alternancia salta de 25% a 71%.** La forma de los datos también
apoya un umbral más que una relación gradual: entre 0% y 4% la tasa de
alternancia es bastante pareja (65% a 80%) y cae de golpe por encima de 4-5%.
Lo llamativo es que el umbral es alto: un crecimiento "razonable" de 2-3% no
alcanza para proteger al oficialismo.

Advertencias:
* El umbral no es nítido. El gráfico de la derecha en `figuras/h1_umbral.png`
  muestra varios picos cercanos (entre 4% y 5%). Lo más honesto es decir
  "alrededor de 4-5%", no "4,49%".
* Buena parte del efecto viene de **reelecciones presidenciales durante el
  boom de las commodities** (Lula, Evo, Correa, Uribe, Chávez). Si se miran sólo
  las elecciones donde el presidente no era candidato (n = 71), la diferencia
  sigue siendo grande (79% contra 43%), pero deja de ser significativa
  (p = 0,25), porque encima del umbral quedan apenas 14 casos.
* Al controlar por "presidente candidato a la reelección", estar debajo del
  umbral sigue sumando unos **+28 puntos porcentuales** de probabilidad de
  alternancia (p = 0,007). Que el presidente sea candidato resta unos 46 puntos:
  es el factor individual más fuerte de toda la base.
* Un modelo con escalón ajusta un poco mejor que una curva suave, pero esa
  comparación favorece al escalón porque el corte se eligió con los mismos
  datos. Con 90 elecciones no se puede distinguir bien entre "umbral" y
  "cuanto más crecimiento, mejor para el oficialismo". La curva suave dice que
  cada punto de crecimiento promedio adicional reduce la probabilidad de
  alternancia en unos 7 puntos porcentuales.

### Hipótesis 2: la recesión pesa; el frenazo solo, no

| Situación en los 2 años previos | Alternancia |
|---|---|
| Hubo recesión (algún año negativo) | **75%** (18/24) |
| Sin recesión | 53% (35/66) |
| Sólo frenazo (creció menos que antes, pero positivo) | 54% (15/28) |
| Ni recesión ni frenazo | 53% (20/38) |

* **Recesión:** sube la probabilidad de alternancia en unos 22 puntos
  (p ≈ 0,05). Si se sacan los gobiernos interinos y las elecciones anticipadas,
  el efecto llega a 31 puntos (p = 0,02). Se confirma.
* **Desaceleración sin recesión:** prácticamente no cambia nada (+7 puntos,
  p = 0,32). Un frenazo de 5% a 3% no le cuesta la elección al oficialismo. No
  se confirma.
* **Cuidado:** cuando la recesión entra al modelo junto con el crecimiento
  promedio de los 4 años y la variable de reelección, su efecto deja de ser
  significativo. La recesión importa sobre todo porque baja el promedio, no
  como un castigo extra aparte.
* El crecimiento de los 2 últimos años parece pesar algo más que el de los 2
  anteriores (−3 a −5 puntos por cada punto de crecimiento, contra −2 a −3),
  pero la diferencia no es estadísticamente significativa (p = 0,12 a 0,67).
  No hay evidencia firme de "memoria corta" del votante.

### En una frase

El oficialismo sudamericano necesita una economía que crezca fuerte (más de
4-5% promedio) para sobrevivir; una recesión cerca de la elección lo complica
claramente, y una simple desaceleración no.

## Limitaciones

* **Pocas observaciones (90).** Todos los resultados son frágiles a la
  inclusión o exclusión de unos pocos casos.
* **Codificación de la alternancia.** Hay casos discutibles (Argentina 2003,
  Brasil 1994, Colombia 2002, gobiernos interinos). Están señalados en las
  columnas `caso_especial` y `nota` de `elecciones.csv` para que se puedan
  revisar o recodificar.
* **El PIB no es lo único.** No se controla por inflación, desempleo,
  escándalos de corrupción ni por el ciclo de las commodities, que mueve a
  la vez el crecimiento y la popularidad de toda la región.
* **Datos de 2023-2024** cargados a mano: conviene verificarlos contra el
  WEO del FMI o los bancos centrales antes de citar los números.
* Maddison mide el PIB en paridad de poder de compra. Sus tasas pueden diferir
  algunas décimas de las cuentas nacionales oficiales.
