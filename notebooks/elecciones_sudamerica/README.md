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
| `data/pib_crecimiento.csv` | Crecimiento del PIB real (% anual). Hasta 2022 viene del Maddison Project 2023 (vía Our World in Data); 2023 y 2024 se cargaron a mano con cifras oficiales o del FMI. Se corrigieron dos saltos de serie de Maddison con la tasa oficial: Perú 1993 (Maddison −16,6%, oficial 4,8%) y Paraguay 2002 (Maddison +15,4%, oficial 0,0%). |
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
| 3-4% | 69% (11/16) |
| 4-5% | 47% (9/19) |
| > 5% | 20% (3/15) |

El corte que mejor separa los dos grupos está en **≈ 4,5% anual**. Debajo de ese
nivel el incumbente pierde el 72% de las veces; encima, sólo el 24%. La
diferencia es estadísticamente significativa (p = 0,001). Para calcular ese
p-valor se repitió todo el procedimiento 5.000 veces con los resultados
mezclados al azar dentro de cada país, así que ya descuenta que el umbral se
"buscó" en los datos y que algunos países alternan más que otros.

**Esto es lo que plantea la hipótesis: cuando el crecimiento promedio cae debajo
de ≈ 4,5%, la alternancia salta de 24% a 72%.** La forma de los datos también
apoya un umbral más que una relación gradual: entre 0% y 4% la tasa de
alternancia es bastante pareja (67% a 80%) y cae de golpe por encima de 4-5%.
Lo llamativo es que el umbral es alto: un crecimiento "razonable" de 2-3% no
alcanza para proteger al oficialismo.

**¿Qué pasa debajo del umbral?**

| Debajo de ~4,5% | Elecciones | El oficialismo pierde |
|---|---|---|
| Todas | 65 | **72%** (47) |
| Sin presidente candidato | 57 | **79%** (45) |
| Con presidente candidato | 8 | 25% (2) |

Debajo del umbral el oficialismo pierde 7 de cada 10 veces, y 8 de cada 10 si
el presidente no es candidato. La reelección no genera este resultado: es la
excepción que permitió a algunos oficialismos sobrevivir con poco crecimiento
(Uribe 2006, Chávez 2000, 2006 y 2012, Maduro 2013, Noboa 2025). Encima del
umbral, los 11 presidentes que fueron por la reelección ganaron.

**¿Cambia el resultado según qué elecciones se incluyan?**

| Base | Elecciones | Debajo de ~4,5% | Encima de ~4,5% | ¿Significativo? |
|---|---|---|---|---|
| **Todas** | 90 | pierde el 72% | pierde el 24% | **Sí** (p = 0,001) |
| Sin interinos ni anticipadas | 75 | 73% | 21% | **Sí** (p = 0,001) |
| Todas, ajustando por si el presidente era candidato | 90 | +28 puntos de probabilidad de perder | | **Sí** (p = 0,005) |
| Sacando las reelecciones | 71 | 79% | 43% | No (p = 0,14) |

La tercera fila deja las 90 elecciones y descuenta estadísticamente el efecto
de que el presidente sea candidato. Aun así, estar debajo del umbral suma unos
28 puntos de probabilidad de alternancia, así que el umbral no se explica sólo
por las reelecciones. La cuarta fila deja de ser significativa sobre todo
porque encima del umbral quedan apenas 14 casos; la diferencia sigue siendo
grande.

Advertencias:
* El umbral no es nítido. El gráfico de la derecha en `figuras/h1_umbral.png`
  muestra varios picos cercanos (entre 4% y 5%). Lo más honesto es decir
  "alrededor de 4-5%", no "4,49%".
* Parte del efecto viene de **reelecciones presidenciales durante el boom de
  las commodities** (Lula, Evo, Correa, Santos, Cristina); ver las tablas de
  arriba. Que el presidente sea candidato resta unos 44 puntos de probabilidad
  de alternancia: es el factor individual más fuerte de toda la base.
* Un modelo con escalón ajusta mejor que una curva suave, pero esa comparación
  favorece al escalón porque el corte se eligió con los mismos datos. La curva
  suave dice que cada punto de crecimiento promedio adicional reduce la
  probabilidad de alternancia en unos 7 puntos porcentuales.

### Hipótesis 2: la recesión sí; la desaceleración no

Se probaron dos versiones de "economía que empeora" en los 2 años previos a la
elección:
* **Recesión:** al menos uno de esos dos años con crecimiento negativo.
* **Desaceleración:** el crecimiento promedio de esos dos años es menor que el
  de los dos anteriores. Se probó con cualquier caída, y también exigiendo que
  la caída sea de más de 1, 2 o 3 puntos.

**Recesión: se confirma, y con fuerza**

| | Con recesión | Sin recesión | Diferencia | ¿Significativo? |
|---|---|---|---|---|
| Todas las elecciones | pierde el **78%** (18/23) | 52% (35/67) | +26 puntos | **Sí** (p = 0,02) |
| Sin interinos ni anticipadas | **83%** (15/18) | 47% (27/57) | +36 puntos | **Sí** (p = 0,007) |
| Sin presidente candidato | **89%** (16/18) | 66% (35/53) | +23 puntos | Al límite (p = 0,05) |

Cuando el presidente no es candidato y hubo recesión, el oficialismo perdió 16
de 18 veces. Las dos excepciones fueron Argentina 2003 (Kirchner, con un
gobierno interino surgido de la crisis de 2001) y Ecuador 2017 (Moreno, con una
caída leve de 1,2%). Con el presidente como candidato, la recesión también
pesa: los únicos dos presidentes que perdieron la reelección en toda la base
(Macri 2019, Bolsonaro 2022) lo hicieron después de una recesión.

**Desaceleración sin recesión: no se confirma, en ninguna versión**

| Desaceleración en los 2 años previos | Con | Sin |
|---|---|---|
| Cualquier caída | pierde el 63% (31/49) | 54% (22/41) |
| Caída de más de 1 punto | 57% (20/35) | 60% (33/55) |
| Caída de más de 2 puntos | 53% (16/30) | 62% (37/60) |
| Caída de más de 3 puntos | 55% (11/20) | 60% (42/70) |
| Se frenó pero siguió creciendo | 54% (15/28) | 61% (38/62) |

Ninguna diferencia es significativa, y cuanto más fuerte la desaceleración,
menos se nota (incluso se invierte un poco). La explicación probable: una
desaceleración fuerte casi siempre viene después de años de mucho crecimiento
(por ejemplo, de 7% a 3%), y esos gobiernos llegan a la elección con un
promedio alto que los protege. **Lo que castiga el votante no es que la economía
crezca menos que antes, sino que deje de crecer.**

**Recesión y umbral juntos**

| | Con recesión | Sin recesión |
|---|---|---|
| Debajo de ~4,5% | pierde el 81% (17/21) | 68% (30/44) |
| Encima de ~4,5% | 50% (1/2) | 22% (5/23) |

Debajo del umbral, una recesión cerca de la elección suma unos 13 puntos más de
probabilidad de alternancia. Pero cuando se mete la recesión en un mismo modelo
junto con el promedio de 4 años y la reelección, su efecto propio deja de ser
significativo: las dos cosas se superponen mucho, porque una recesión baja el
promedio. Con 90 elecciones no se puede separar bien cuánto pesa cada una.

Otras observaciones:
* El crecimiento de los 2 últimos años no pesa significativamente más que el de
  los 2 anteriores (p = 0,23 a 0,81). No hay evidencia firme de "memoria corta"
  del votante.
* La definición de recesión ("algún año negativo") cuenta como recesión a
  Argentina 2011 (−5,5% en 2009, pero +11,3% en 2010). Ese caso es un rebote más
  que una recesión, y Cristina ganó.
* El resultado se mantiene si, para las elecciones del segundo semestre, se
  incluye el crecimiento del propio año electoral (76% contra 51%, p = 0,03).

### En una frase

Debajo de un crecimiento promedio de 4-5% el oficialismo sudamericano pierde
la mayoría de las veces. Una recesión cerca de la elección lo complica todavía
más; una simple desaceleración, no.

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
