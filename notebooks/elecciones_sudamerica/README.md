# Crecimiento económico y alternancia en América del Sur

Testea cuatro hipótesis con 90 elecciones presidenciales (10 países, 1983-2025):

1. **Umbral:** existe un crecimiento promedio en los 4 años previos a la elección
   por debajo del cual el partido incumbente tiende a perder.
2. **Frenazo / recesión:** una desaceleración o una recesión en los 2 años previos
   aumenta la probabilidad de que el incumbente pierda.
3. **Desempleo:** un aumento del desempleo antes de la elección aumenta la
   probabilidad de que el incumbente pierda.
4. **Escándalos judiciales:** un escándalo con investigación formal durante el
   mandato aumenta la probabilidad de que el incumbente pierda.

## Cómo correrlo

```bash
pip install pandas numpy statsmodels matplotlib scipy pyreadr
python construir_datos.py   # baja PIB, desempleo y V-Dem y arma data/base_analisis.csv
python analisis.py          # escribe resultados.txt y figuras/
```

## Datos

| Archivo | Contenido |
|---|---|
| `data/elecciones.csv` | Base codificada a mano: incumbente, ganador, `alternancia` (1 = perdió el partido de gobierno), `presidente_candidato` (1 = el presidente en ejercicio buscaba la reelección), `caso_especial` (gobiernos interinos y elecciones anticipadas). |
| `data/pib_crecimiento.csv` | Crecimiento del PIB real (% anual), 1978-2025. Banco Mundial, indicador NY.GDP.MKTP.KD.ZG (cuentas nacionales oficiales a precios constantes). |
| `data/desempleo.csv` | Tasa de desempleo (% de la fuerza laboral), 1991-2025. Estimación modelada de la OIT publicada por el Banco Mundial (indicador SL.UEM.TOTL.ZS). Es comparable entre países, pero no existe antes de 1991. |
| `data/escandalos.csv` | Escándalos judiciales durante el mandato, codificados a mano (ver Hipótesis 4): `escandalo_presidente`, `escandalo_gobierno`, `certeza` (alta / media / baja) y una descripción de cada caso. |
| `data/vdem_corrupcion.csv` | Índice de corrupción del Poder Ejecutivo (0 a 1; más alto = más corrupción), V-Dem versión 16 (variable v2x_execorr). Lo elaboran expertos de cada país, año por año. |
| `data/base_analisis.csv` | Todo cruzado. |

Los dos indicadores del Banco Mundial se bajan del espejo
[datasets/world-development-indicators](https://github.com/datasets/world-development-indicators)
en GitHub, actualizado a julio de 2026.

**Convención temporal:** para una elección en el año *t* se usan los años
calendario *t-4* a *t-1*. "Últimos 2 años" son *t-2* y *t-1*.

**Qué quedó afuera:** Venezuela después de 2013 (elecciones no competitivas),
Perú 2000 (fraude), Bolivia 2019 (anulada), Perú 2026 (resultado no
incorporado), y las primeras elecciones tras cada dictadura (no hay partido
civil incumbente). Guyana y Surinam no están.

## Resultados

### Hipótesis 1: se confirma; el umbral está en torno a 3-4% anual

La alternancia es lo normal en la región: pasa en el 59% de las elecciones. Al
ordenarlas por crecimiento promedio, se ve un quiebre claro:

| Crecimiento promedio 4 años | Alternancia |
|---|---|
| < 1% | 76% (16/21) |
| 1-2% | 75% (6/8) |
| 2-3% | 85% (11/13) |
| 3-4% | 62% (8/13) |
| 4-5% | 35% (8/23) |
| > 5% | 33% (4/12) |

El corte que mejor separa los dos grupos está en **≈ 3,7% anual**. Debajo de ese
nivel el incumbente pierde el 80% de las veces; encima, el 34%. La diferencia
es estadísticamente significativa (p < 0,001). Para calcular ese p-valor se
repitió todo el procedimiento 5.000 veces con los resultados mezclados al azar
dentro de cada país, y ninguna de esas repeticiones produjo una separación tan
buena. El p-valor ya descuenta que el umbral se "buscó" en los datos y que
algunos países alternan más que otros.

**Esto es lo que plantea la hipótesis: cuando el crecimiento promedio cae debajo
de ≈ 3,7%, la alternancia salta de 34% a 80%.** La forma de los datos apoya un
umbral más que una relación gradual: entre 0% y 3% la tasa de alternancia es
pareja (75% a 85%) y cae de golpe por encima de 4%. El gráfico de la derecha en
`figuras/h1_umbral.png` muestra un pico claro en 3,7%.

**¿Qué pasa debajo del umbral?**

| Debajo de ~3,7% | Elecciones | El oficialismo pierde |
|---|---|---|
| Todas | 49 | **80%** (39) |
| Sin presidente candidato | 42 | **88%** (37) |
| Con presidente candidato | 7 | 29% (2) |

Debajo del umbral el oficialismo pierde 8 de cada 10 veces, y casi 9 de cada 10
si el presidente no es candidato. La reelección no genera este resultado: es la
excepción que permitió a algunos oficialismos sobrevivir con poco crecimiento
(Lula 2006, Chávez 2000, 2006 y 2012, Maduro 2013). Encima del umbral, los 12
presidentes que fueron por la reelección ganaron.

**¿Cambia el resultado según qué elecciones se incluyan?**

| Base | Elecciones | Umbral | Debajo | Encima | ¿Significativo? |
|---|---|---|---|---|---|
| **Todas** | 90 | 3,7% | pierde el 80% | pierde el 34% | **Sí** (p < 0,001) |
| Sin interinos ni anticipadas | 75 | 2,7% | 89% | 36% | **Sí** (p = 0,001) |
| Sin reelecciones | 71 | 3,7% | 88% | 48% | **Sí** (p = 0,005) |
| Todas, ajustando por si el presidente era candidato | 90 | 3,7% | +32 puntos de probabilidad de perder | | **Sí** (p < 0,001) |

El umbral aparece en todas las versiones, también cuando se sacan las
reelecciones. Lo que se mueve es su ubicación exacta: entre 2,7% y 3,7% según
qué elecciones se incluyan.

Advertencias:
* Lo honesto es decir "alrededor de 3-4%", no "3,73%".
* Que el presidente sea candidato resta unos 47 puntos de probabilidad de
  alternancia: es el factor individual más fuerte de toda la base.
* Un modelo con escalón ajusta mejor que una curva suave, pero esa comparación
  favorece al escalón porque el corte se eligió con los mismos datos. La curva
  suave dice que cada punto de crecimiento promedio adicional reduce la
  probabilidad de alternancia en unos 7 puntos porcentuales.

### Hipótesis 2: sólo las recesiones fuertes pesan, y casi todo lo explica el umbral

Se probaron tres versiones de "economía que empeora" en los 2 años previos a
la elección:
* **Recesión:** al menos uno de esos dos años con crecimiento negativo, aunque
  sea mínimo.
* **Recesión fuerte:** al menos uno de esos dos años con una caída de más de 1%.
* **Desaceleración:** el crecimiento promedio de esos dos años es menor que el
  de los dos anteriores. Se probó con cualquier caída, y también exigiendo que
  la caída sea de más de 1, 2 o 3 puntos.

**Recesión: depende de cuán fuerte sea**

| | Con recesión | Sin recesión | ¿Significativo? |
|---|---|---|---|
| Cualquier año negativo, todas | pierde el 67% (20/30) | 55% (33/60) | No (p = 0,20) |
| Caída de más de 1%, todas | **75%** (15/20) | 54% (38/70) | Al límite (p = 0,08) |
| Caída de más de 1%, sin interinos ni anticipadas | **81%** (13/16) | 49% (29/59) | **Sí** (p = 0,02) |
| Caída de más de 1%, sin presidente candidato | **93%** (13/14) | 67% (38/57) | **Sí** (p = 0,045) |

La definición "cualquier año negativo" no funciona bien porque incluye caídas
mínimas que casi no se sienten: Paraguay 2023 (−0,03%), Brasil 2010 (−0,1%),
Paraguay 2003 (−0,8% y −0,02%). En esos casos el oficialismo ganó. **Con
recesiones de verdad (más de 1% de caída) el efecto es claro:** cuando el
presidente no era candidato, el oficialismo perdió 13 de 14 veces. La única
excepción fue Argentina 2003, con el gobierno interino de Duhalde. Con el
presidente como candidato perdieron 2 de 6 (Macri 2019 y Bolsonaro 2022).

**Pero la recesión pesa sobre todo porque baja el promedio de los 4 años**

| | Con recesión fuerte | Sin recesión fuerte |
|---|---|---|
| Debajo de ~3,7% | pierde el 82% (14/17) | 78% (25/32) |
| Encima de ~3,7% | 33% (1/3) | 34% (13/38) |

Una vez que se sabe de qué lado del umbral está la economía, que además haya
habido una recesión casi no cambia nada (82% contra 78%). En un modelo con el
crecimiento promedio y la reelección, el efecto de la recesión fuerte no es
significativo (p = 0,18). Es decir: **la recesión no parece funcionar como un
castigo aparte; es una de las formas en que la economía cae debajo del
umbral.**

**Desaceleración sin recesión: no se confirma, en ninguna versión**

| Desaceleración en los 2 años previos | Con | Sin |
|---|---|---|
| Cualquier caída | pierde el 62% (30/48) | 55% (23/42) |
| Caída de más de 1 punto | 54% (19/35) | 62% (34/55) |
| Caída de más de 2 puntos | 55% (16/29) | 61% (37/61) |
| Caída de más de 3 puntos | 60% (12/20) | 59% (41/70) |
| Se frenó pero siguió creciendo | 54% (14/26) | 61% (39/64) |

Ninguna diferencia es significativa. Una desaceleración fuerte suele venir
después de años de mucho crecimiento (por ejemplo, de 7% a 3%), y esos
gobiernos llegan a la elección con un promedio alto que los protege.

Otras observaciones:
* El crecimiento de los 2 últimos años no pesa más que el de los 2 anteriores
  (p = 0,40 a 0,98). Lo que cuenta es el período completo, no los últimos años.
  No hay evidencia de "memoria corta" del votante.
* Incluir el crecimiento del propio año electoral para las elecciones del
  segundo semestre no cambia las conclusiones.

### Hipótesis 3: el desempleo no agrega nada; sólo las subas grandes insinúan algo

Como la serie de desempleo empieza en 1991, este análisis usa las **72
elecciones desde 1994**. La variable principal es cuánto cambió la tasa de
desempleo en los 2 años previos a la elección (de *t-3* a *t-1*), en puntos
porcentuales.

| Cambio del desempleo en los 2 años previos | El oficialismo pierde |
|---|---|
| Bajó más de 1 punto | 46% (6/13) |
| Bajó hasta 1 punto | 50% (11/22) |
| Subió hasta 1 punto | 65% (13/20) |
| Subió entre 1 y 2 puntos | 38% (3/8) |
| Subió más de 2 puntos | 67% (6/9) |

No hay un patrón claro: subas moderadas del desempleo no se asocian con más
derrotas del oficialismo. Ninguna comparación es estadísticamente
significativa, tampoco con otras versiones de la variable:

| Versión probada | Efecto por cada punto de suba del desempleo | ¿Significativo? |
|---|---|---|
| Cambio en los 2 años previos | +0,8 puntos de prob. de perder | No (p = 0,82) |
| Ídem, ajustando por reelección | +1,0 | No (p = 0,69) |
| Ídem, ajustando por reelección y crecimiento | −0,7 | No (p = 0,81) |
| Cambio a lo largo del mandato (4 años) | +1,8 | No (p = 0,34) |
| Nivel de desempleo el año anterior | −0,6 | No (p = 0,64) |
| Incluyendo el año electoral | +0,3 | No (p = 0,89) |

**Lo único que insinúa algo son las subas grandes (más de 2 puntos).** Hubo 9
casos:

| Elección | Suba del desempleo | Resultado |
|---|---|---|
| Argentina 1995 | +5,4 | Ganó (Menem, presidente candidato) |
| Colombia 1998 | +3,4 | Perdió |
| Venezuela 2000 | +3,4 | Ganó (Chávez, presidente candidato) |
| Argentina 2003 | +4,6 | Ganó (gobierno interino de Duhalde) |
| Brasil 2018 | +4,3 | Perdió |
| Chile 2021 | +3,3 | Perdió |
| Perú 2021 | +3,7 | Perdió |
| Ecuador 2021 | +2,6 | Perdió |
| Colombia 2022 | +3,6 | Perdió |

Cuando el presidente no era candidato, el oficialismo perdió en 6 de 7 casos.
Pero son muy pocos para sacar conclusiones (p = 0,31), y 4 de ellos son
elecciones de la pandemia, cuando hubo a la vez recesión y suba del desempleo.

**Por qué el desempleo dice tan poco:**
* **Repite lo que ya dice el PIB.** Cuando la economía crece poco, el desempleo
  sube (la correlación entre las dos variables es −0,66). Una vez que se mira el
  crecimiento, el desempleo no agrega información nueva.
* **En varios países mide mal el malestar.** En Bolivia, Perú, Ecuador y
  Paraguay la informalidad es tan alta que el desempleo abierto se mantiene
  bajo (3-5%) aunque la economía empeore: la gente no queda desempleada, pasa
  a trabajos informales peor pagos.
* **La serie de la OIT es en parte estimada.** Sobre todo en los años 90 y en
  los países con pocas encuestas de empleo, los datos son en buena medida
  modelados (por ejemplo, Ecuador figura con 4,4% fijo entre 1991 y 1998).

### Hipótesis 4: pesa el escándalo que toca al presidente; el que toca a su gobierno, no

**Cómo se midió.** No hay una base pública de escándalos por elección, así que
se codificó a mano cada una de las 90 elecciones, con dos variables:
* **Escándalo del presidente:** una investigación formal (judicial, fiscal o
  parlamentaria), pública antes de la elección, que involucra al presidente o a
  su familia directa. Por ejemplo: Proceso 8000 (Samper), Caval (hijo de
  Bachelet), las denuncias de la Fiscalía contra Temer o las agendas de Nadine
  Heredia.
* **Escándalo en el gobierno:** lo anterior, o una investigación que involucra
  a ministros, al vicepresidente o a dirigentes del partido de gobierno. Por
  ejemplo: Mensalão, MOP-Gate, Sendic o el caso Astesiano.

Cada caso tiene una descripción y un grado de certeza en `data/escandalos.csv`,
para que se pueda revisar y corregir.

**Escándalo del presidente: efecto muy fuerte**

| | Con escándalo del presidente | Sin escándalo | ¿Significativo? |
|---|---|---|---|
| Todas | pierde el **93%** (14/15) | 52% (39/75) | **Sí** (p = 0,002) |
| Sin interinos ni anticipadas | **92%** (11/12) | 49% (31/63) | **Sí** (p = 0,006) |
| Sin presidente candidato | **92%** (12/13) | 67% (39/58) | Al límite (p = 0,06) |
| Sin casos de certeza baja | **93%** (14/15) | 58% (33/57) | **Sí** (p = 0,008) |

De 15 oficialismos con un escándalo que tocaba al presidente, 14 perdieron. La
única excepción fue Paraguay 2003: el Partido Colorado retuvo el gobierno pese
al escándalo de González Macchi.

**Escándalo en el gobierno (sin tocar al presidente): ningún efecto**

Cuando el escándalo involucra a ministros o dirigentes pero no al presidente,
el oficialismo pierde el 45% de las veces, menos que cuando no hay ningún
escándalo (57%). Desde 2000, el 70% de los gobiernos tuvo algún escándalo de
este tipo: es tan común que no distingue a los que pierden de los que ganan.

**Escándalo y umbral juntos**

| | Con escándalo del presidente | Sin escándalo |
|---|---|---|
| Debajo de ~3,7% | pierde el 92% (11/12) | 76% (28/37) |
| Encima de ~3,7% | **100%** (3/3) | 29% (11/38) |

La fila de abajo es la más interesante. Con la economía creciendo bien, el
oficialismo normalmente gana; los tres que perdieron igual tenían un escándalo
que tocaba al presidente: Brasil 1989 (Sarney), Colombia 1998 (Samper) y Perú
2016 (Humala). Son sólo tres casos, pero sugieren que **un escándalo del
presidente puede tumbar a un oficialismo que la economía estaba protegiendo**.

**Advertencias importantes:**
* **Escándalo y economía mala van juntos.** Los oficialismos con escándalo del
  presidente llegaron con un crecimiento promedio de 1,5%, contra 3,2% del
  resto. Al controlar por el crecimiento y la reelección, el escándalo sigue
  sumando unos 37 a 43 puntos de probabilidad de perder, pero queda al límite
  de la significancia (p = 0,08 a 0,11): con 15 casos no alcanza para separar
  bien los dos efectos.
* **La causalidad puede ir en los dos sentidos.** Un presidente que pierde
  popularidad por la economía queda más expuesto: la prensa, la oposición y los
  fiscales se animan más. Parte de los escándalos puede ser consecuencia de la
  debilidad, no su causa.
* **Riesgo de sesgo retrospectivo.** La codificación la hizo Claude, a partir de
  conocimiento general y sabiendo quién ganó cada elección. Los escándalos de
  los gobiernos que perdieron tienden a recordarse más. Conviene que alguien
  revise `data/escandalos.csv` sin mirar los resultados.

**Corrupción según V-Dem: ningún efecto**

Ni el nivel de corrupción del Poder Ejecutivo el año anterior a la elección
(p = 0,28) ni su aumento a lo largo del mandato (p = 0,36) se asocian con la
derrota del oficialismo. Esto es coherente con lo anterior: lo que castiga el
votante no es la corrupción en sí, que muchas veces no se ve, sino el escándalo
que la hace pública y llega hasta el presidente.

### En una frase

Debajo de un crecimiento promedio de 3-4% en los 4 años previos, el oficialismo
sudamericano pierde 8 de cada 10 elecciones. Una recesión fuerte cerca de la
elección empuja en la misma dirección, pero sobre todo porque hunde ese
promedio. Ni una simple desaceleración ni el desempleo agregan información.
Un escándalo judicial que toca al presidente en persona se asocia con la
derrota casi segura del oficialismo; los escándalos de su gobierno, no.

## Limitaciones

* **Pocas observaciones (90).** Todos los resultados son frágiles a la
  inclusión o exclusión de unos pocos casos. Por ejemplo, al pasar del PIB de
  Maddison al del Banco Mundial el umbral se movió de 4,5% a 3,7%, y la
  recesión "cualquier año negativo" dejó de ser significativa.
* **Codificación manual de los escándalos.** Ver las advertencias de la
  Hipótesis 4: es la variable más subjetiva de la base.
* **Codificación de la alternancia.** Hay casos discutibles (Argentina 2003,
  Brasil 1994, Colombia 2002, gobiernos interinos). Están señalados en las
  columnas `caso_especial` y `nota` de `elecciones.csv` para que se puedan
  revisar o recodificar.
* **El PIB no es lo único.** No se controla por inflación, escándalos de
  corrupción ni por el ciclo de las commodities, que mueve a la vez el
  crecimiento y la popularidad de toda la región.
* **Datos recientes.** Las cifras de 2024 y 2025 del Banco Mundial todavía
  pueden revisarse. Afectan a Uruguay 2024, Chile 2025, Bolivia 2025 y
  Ecuador 2025. Bolivia 2025 en particular queda apenas encima del umbral
  (3,8%) y el oficialismo perdió.
