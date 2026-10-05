"""
Construye las series de crecimiento del PIB real y de desempleo para 10 países
de América del Sur y las cruza con la base de elecciones presidenciales.

Fuentes (indicadores del Banco Mundial, vía el espejo
datasets/world-development-indicators en GitHub)
-------
* Crecimiento del PIB real (% anual), 1978-2025: NY.GDP.MKTP.KD.ZG
  (PIB a precios constantes, cuentas nacionales oficiales).
* Desempleo (% de la fuerza laboral), 1991-2025: SL.UEM.TOTL.ZS
  (estimación modelada de la OIT).

Salida: data/pib_crecimiento.csv, data/desempleo.csv y data/base_analisis.csv
"""
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).parent
DATA = AQUI / "data"
URL_WDI = ("https://raw.githubusercontent.com/datasets/world-development-indicators/"
           "main/indicators/{}/data.csv")
ISO = {"ARG": "Argentina", "BOL": "Bolivia", "BRA": "Brasil", "CHL": "Chile",
       "COL": "Colombia", "ECU": "Ecuador", "PRY": "Paraguay", "PER": "Peru",
       "URY": "Uruguay", "VEN": "Venezuela"}


def serie_wdi(indicador, nombre):
    w = pd.read_csv(URL_WDI.format(indicador))
    w = w[w["Country Code"].isin(ISO)]
    w = w.assign(pais=w["Country Code"].map(ISO)).rename(columns={"Year": "anio", "Value": nombre})
    return w[["pais", "anio", nombre]].dropna().sort_values(["pais", "anio"]).reset_index(drop=True)


def serie_crecimiento():
    return serie_wdi("ny.gdp.mktp.kd.zg", "crecimiento")


def serie_desempleo():
    return serie_wdi("sl.uem.totl.zs", "desempleo")

def armar_base(elec, g, u):
    """Para una elección en el año t usa los años calendario t-4 ... t-1."""
    tasa = g.set_index(["pais", "anio"]).crecimiento
    des = u.set_index(["pais", "anio"]).desempleo
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
            # Recesión "de verdad": algún año con caída de más de 1%
            "recesion_fuerte": int(min(c[1], c[2]) < -1),
            "crec_t1": c[1], "crec_t2": c[2], "crec_t3": c[3], "crec_t4": c[4],
            # Robustez para elecciones del 2º semestre: incluye el año electoral
            "crec_t0": tasa.get((e.pais, t)),
            # Hipótesis 3: desempleo (sólo hay datos desde 1991)
            "desemp_t1": des.get((e.pais, t - 1)),
            # Cambio en puntos porcentuales en los 2 años previos
            "dif_desemp_2a": des.get((e.pais, t - 1)) - des.get((e.pais, t - 3))
            if (e.pais, t - 3) in des.index else None,
            # Cambio a lo largo del mandato (4 años)
            "dif_desemp_4a": des.get((e.pais, t - 1)) - des.get((e.pais, t - 5))
            if (e.pais, t - 5) in des.index else None,
            # Robustez para elecciones del 2º semestre: incluye el año electoral
            "dif_desemp_2a_t0": des.get((e.pais, t)) - des.get((e.pais, t - 2))
            if (e.pais, t - 2) in des.index and (e.pais, t) in des.index else None,
        })
    base = pd.concat([elec.reset_index(drop=True), pd.DataFrame(filas)], axis=1)
    base["desaceleracion"] = base.crec_ult2 - base.crec_prim2  # <0 = se frenó
    base["frenazo"] = (base.desaceleracion < 0).astype(int)
    return base


if __name__ == "__main__":
    g = serie_crecimiento()
    g.to_csv(DATA / "pib_crecimiento.csv", index=False, float_format="%.3f")
    u = serie_desempleo()
    u.to_csv(DATA / "desempleo.csv", index=False, float_format="%.3f")
    elec = pd.read_csv(DATA / "elecciones.csv")
    base = armar_base(elec, g, u)
    faltan = base[base.crec_4a.isna()]
    assert faltan.empty, f"Faltan datos de PIB para:\n{faltan[['pais', 'anio']]}"
    base.to_csv(DATA / "base_analisis.csv", index=False, float_format="%.3f")
    print(f"{len(base)} elecciones, {base.alternancia.mean():.0%} con alternancia; "
          f"{base.dif_desemp_2a.notna().sum()} con datos de desempleo")
