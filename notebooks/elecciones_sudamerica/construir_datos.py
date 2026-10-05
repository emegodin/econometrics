"""
Construye la serie de crecimiento del PIB real (% anual) para 10 países de
América del Sur y la cruza con la base de elecciones presidenciales.

Fuentes
-------
* 1975-2022: PIB del Maddison Project Database 2023 (Bolt y van Zanden),
  tal como lo publica Our World in Data en GitHub (columna `gdp`).
* 2023-2024: no están en Maddison. Se completan a mano con las tasas de
  crecimiento oficiales / FMI (WEO) y quedan marcadas en la columna `fuente`.

Salida: data/pib_crecimiento.csv y data/base_analisis.csv
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
DATA = AQUI / "data"
URL_OWID = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

PAISES = {  # nombre en OWID -> nombre en la base de elecciones
    "Argentina": "Argentina", "Bolivia": "Bolivia", "Brazil": "Brasil",
    "Chile": "Chile", "Colombia": "Colombia", "Ecuador": "Ecuador",
    "Paraguay": "Paraguay", "Peru": "Peru", "Uruguay": "Uruguay",
    "Venezuela": "Venezuela",
}

# Crecimiento del PIB real 2023 y 2024 (%), cifras oficiales / FMI aproximadas.
# Venezuela no se usa después de 2013, por eso no se completa.
COMPLEMENTO = {
    "Argentina": {2023: -1.6, 2024: -1.3},
    "Bolivia":   {2023: 3.1,  2024: 0.7},
    "Brasil":    {2023: 3.2,  2024: 3.4},
    "Chile":     {2023: 0.5,  2024: 2.6},
    "Colombia":  {2023: 0.7,  2024: 1.6},
    "Ecuador":   {2023: 2.4,  2024: -2.0},
    "Paraguay":  {2023: 5.0,  2024: 4.2},
    "Peru":      {2023: -0.4, 2024: 3.3},
    "Uruguay":   {2023: 0.7,  2024: 3.1},
}


# Saltos de serie en Maddison que no reflejan crecimiento real; se reemplazan
# por la tasa oficial (BCRP para Perú, BCP para Paraguay).
CORRECCIONES = {
    ("Peru", 1993): 4.8,      # Maddison: -16.6
    ("Paraguay", 2002): 0.0,  # Maddison: +15.4
}


def serie_crecimiento():
    owid = pd.read_csv(URL_OWID, usecols=["country", "year", "gdp"])
    owid = owid[owid.country.isin(PAISES) & (owid.year >= 1975)].dropna()
    owid["pais"] = owid.country.map(PAISES)
    owid = owid.sort_values(["pais", "year"])
    owid["crecimiento"] = owid.groupby("pais").gdp.pct_change() * 100
    owid["fuente"] = "Maddison 2023 (OWID)"
    for (pais, anio), valor in CORRECCIONES.items():
        fila = (owid.pais == pais) & (owid.year == anio)
        owid.loc[fila, "crecimiento"] = valor
        owid.loc[fila, "fuente"] = "Oficial (corrige salto de serie en Maddison)"
    g = owid.rename(columns={"year": "anio"})[["pais", "anio", "crecimiento", "fuente"]]

    extra = pd.DataFrame(
        [(p, a, v, "Oficial/FMI (cargado a mano)")
         for p, d in COMPLEMENTO.items() for a, v in d.items()],
        columns=["pais", "anio", "crecimiento", "fuente"],
    )
    return pd.concat([g.dropna(), extra]).sort_values(["pais", "anio"]).reset_index(drop=True)


def armar_base(elec, g):
    """Para una elección en el año t usa los años calendario t-4 ... t-1."""
    tasa = g.set_index(["pais", "anio"]).crecimiento
    filas = []
    for _, e in elec.iterrows():
        t = e.anio
        c = {k: tasa.get((e.pais, t - k)) for k in (1, 2, 3, 4)}
        filas.append({
            # Hipótesis 1: crecimiento promedio de los 4 años previos
            "crec_4a": (c[1] + c[2] + c[3] + c[4]) / 4,
            # Hipótesis 2: los dos años previos vs los dos anteriores
            "crec_ult2": (c[1] + c[2]) / 2,
            "crec_prim2": (c[3] + c[4]) / 2,
            "recesion_ult2": int(min(c[1], c[2]) < 0),
            "crec_t1": c[1], "crec_t2": c[2], "crec_t3": c[3], "crec_t4": c[4],
            # Robustez para elecciones del 2º semestre: incluye el año electoral
            "crec_t0": tasa.get((e.pais, t)),
        })
    base = pd.concat([elec.reset_index(drop=True), pd.DataFrame(filas)], axis=1)
    base["desaceleracion"] = base.crec_ult2 - base.crec_prim2  # <0 = se frenó
    base["frenazo"] = (base.desaceleracion < 0).astype(int)
    return base


if __name__ == "__main__":
    g = serie_crecimiento()
    g.to_csv(DATA / "pib_crecimiento.csv", index=False, float_format="%.3f")
    elec = pd.read_csv(DATA / "elecciones.csv")
    base = armar_base(elec, g)
    faltan = base[base.crec_4a.isna()]
    assert faltan.empty, f"Faltan datos de PIB para:\n{faltan[['pais', 'anio']]}"
    base.to_csv(DATA / "base_analisis.csv", index=False, float_format="%.3f")
    print(f"{len(base)} elecciones, {base.alternancia.mean():.0%} con alternancia")
