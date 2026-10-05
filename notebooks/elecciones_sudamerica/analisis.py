"""
Testea dos hipótesis sobre crecimiento económico y alternancia en América del Sur.

H1: existe un umbral de crecimiento promedio (4 años previos) por debajo del
    cual se dispara la alternancia del partido incumbente.
H2: una desaceleración o una recesión en los 2 años previos aumenta la
    probabilidad de que el incumbente pierda.
H3: un aumento del desempleo antes de la elección aumenta la probabilidad de
    que el incumbente pierda (sólo elecciones desde 1994, por los datos).

Correr primero construir_datos.py. Escribe resultados.txt y figuras en figuras/.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

AQUI = Path(__file__).parent
FIG = AQUI / "figuras"
FIG.mkdir(exist_ok=True)
RNG = np.random.default_rng(2026)
N_PERM = 5000

salida = []


def p(*txt):
    linea = " ".join(str(t) for t in txt)
    print(linea)
    salida.append(linea)


def logit_cluster(formula, d):
    """Logit con errores estándar agrupados por país."""
    grupos = pd.factorize(d.pais)[0]
    return smf.logit(formula, d).fit(disp=0, cov_type="cluster",
                                     cov_kwds={"groups": grupos})


def efecto_marginal(mod, var):
    m = mod.get_margeff(at="overall").summary_frame().loc[var]
    return m["dy/dx"], m["Pr(>|z|)"]


# ---------------------------------------------------------------- umbral (H1)
def loglik_escalon(x, y, c):
    """Log-verosimilitud de un modelo 'dos tasas': una debajo de c, otra encima."""
    ll = 0.0
    for grupo in (y[x < c], y[x >= c]):
        k, n = grupo.sum(), len(grupo)
        q = k / n if n else 0
        if 0 < q < 1:
            ll += k * np.log(q) + (n - k) * np.log(1 - q)
    return ll


def buscar_umbral(x, y, min_obs=10):
    """Recorre todos los cortes posibles dejando al menos min_obs de cada lado."""
    xs = np.sort(x)
    candidatos = np.unique((xs[min_obs - 1:-min_obs] + xs[min_obs:len(xs) - min_obs + 1]) / 2)
    lls = np.array([loglik_escalon(x, y, c) for c in candidatos])
    return candidatos[lls.argmax()], lls.max(), candidatos, lls


def test_umbral(d, etiqueta):
    x, y = d.crec_4a.to_numpy(), d.alternancia.to_numpy()
    c, ll, cands, lls = buscar_umbral(x, y)
    ll0 = loglik_escalon(x, y, -np.inf)
    lr = 2 * (ll - ll0)
    # Permutación: se barajan los resultados DENTRO de cada país y se repite
    # toda la búsqueda del umbral. Así el p-valor ya descuenta que "buscamos"
    # el mejor corte y que algunos países alternan más que otros.
    paises = d.pais.to_numpy()
    lr_perm = np.empty(N_PERM)
    for i in range(N_PERM):
        yp = y.copy()
        for pa in np.unique(paises):
            idx = np.where(paises == pa)[0]
            yp[idx] = RNG.permutation(yp[idx])
        lr_perm[i] = 2 * (buscar_umbral(x, yp)[1] - ll0)
    pval = (lr_perm >= lr).mean()
    deb, enc = y[x < c], y[x >= c]
    p(f"  [{etiqueta}] n={len(y)}  umbral estimado = {c:.2f}% anual")
    p(f"    alternancia debajo del umbral: {deb.mean():.0%} ({deb.sum()}/{len(deb)})")
    p(f"    alternancia encima del umbral: {enc.mean():.0%} ({enc.sum()}/{len(enc)})")
    p(f"    p-valor por permutación (corrige por búsqueda): {pval:.3f}")
    return c, cands, lls, pval


def h1(d, d_sin_esp):
    p("=" * 78)
    p("HIPÓTESIS 1: umbral de crecimiento promedio (4 años previos)")
    p("=" * 78)

    p("\n1.a) Tasa de alternancia por tramo de crecimiento promedio")
    tramos = pd.cut(d.crec_4a, [-np.inf, 1, 2, 3, 4, 5, np.inf],
                    labels=["< 1%", "1-2%", "2-3%", "3-4%", "4-5%", "> 5%"])
    t = d.groupby(tramos, observed=True).alternancia.agg(["mean", "sum", "count"])
    for k, r in t.iterrows():
        p(f"    {k:>6}: {r['mean']:5.0%}  ({int(r['sum'])}/{int(r['count'])})")

    p("\n1.b) Búsqueda del umbral que mejor separa alternancia / continuidad")
    c, cands, lls, _ = test_umbral(d, "todas")
    test_umbral(d_sin_esp, "sin interinos ni anticipadas")
    test_umbral(d[d.presidente_candidato == 0], "sólo sin presidente candidato")

    p("\n1.c) ¿Escalón o curva suave? Comparación de modelos (AIC: menor = mejor)")
    d = d.assign(debajo=(d.crec_4a < c).astype(int))
    m_lin = logit_cluster("alternancia ~ crec_4a", d)
    m_esc = logit_cluster("alternancia ~ debajo", d)
    m_amb = logit_cluster("alternancia ~ debajo + crec_4a", d)
    p(f"    curva suave (logit lineal)  AIC = {m_lin.aic:6.1f}")
    p(f"    escalón en {c:.2f}%          AIC = {m_esc.aic:6.1f}")
    p(f"    ambos juntos                AIC = {m_amb.aic:6.1f}  "
      f"(p escalón = {m_amb.pvalues['debajo']:.3f}, p lineal = {m_amb.pvalues['crec_4a']:.3f})")
    p("    Nota: el AIC del escalón está sesgado a favor porque el corte se eligió con los mismos datos.")
    em, pv = efecto_marginal(m_lin, "crec_4a")
    p(f"    Curva suave: cada punto más de crecimiento promedio cambia la prob. de "
      f"alternancia en {em*100:+.1f} pp (p = {pv:.3f})")

    p("\n1.d) Controlando por presidente candidato a la reelección (EE agrupados por país)")
    m = logit_cluster("alternancia ~ debajo + presidente_candidato", d)
    em, pv = efecto_marginal(m, "debajo")
    p(f"    Estar debajo del umbral: {em*100:+.1f} pp de prob. de alternancia (p = {pv:.3f})")
    em, pv = efecto_marginal(m, "presidente_candidato")
    p(f"    Presidente en ejercicio candidato: {em*100:+.1f} pp (p = {pv:.3f})")

    graf_h1(d, c, cands, lls, m_lin)
    return c


def graf_h1(d, c, cands, lls, m_lin):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    a = ax[0]
    jit = RNG.uniform(-0.04, 0.04, len(d))
    colores = np.where(d.alternancia == 1, "#c0392b", "#2471a3")
    a.scatter(d.crec_4a, d.alternancia + jit, c=colores, alpha=0.7, s=28)
    xx = np.linspace(d.crec_4a.min(), d.crec_4a.max(), 200)
    a.plot(xx, m_lin.predict(pd.DataFrame({"crec_4a": xx})), color="k", lw=1.5,
           label="Prob. estimada (logit)")
    a.axvline(c, ls="--", color="gray", label=f"Umbral estimado ({c:.1f}%)")
    for lado, q in ((d.crec_4a < c, None), (d.crec_4a >= c, None)):
        tasa = d.alternancia[lado].mean()
        lo, hi = (d.crec_4a[lado].min(), d.crec_4a[lado].max())
        a.hlines(tasa, lo, hi, color="#e67e22", lw=3, alpha=0.8)
    a.set_xlabel("Crecimiento promedio del PIB, 4 años previos (%)")
    a.set_ylabel("Alternancia (1) / Continuidad (0)")
    a.set_title("Crecimiento y alternancia (naranja = tasa por lado del umbral)")
    a.legend(loc="center right", fontsize=8)
    b = ax[1]
    b.plot(cands, lls, marker="o", ms=3)
    b.axvline(c, ls="--", color="gray")
    b.set_xlabel("Umbral candidato (%)")
    b.set_ylabel("Log-verosimilitud (más alto = separa mejor)")
    b.set_title("¿Qué tan nítido es el umbral?")
    fig.tight_layout()
    fig.savefig(FIG / "h1_umbral.png", dpi=130)
    plt.close(fig)


# ------------------------------------------------------- desaceleración (H2)
def tabla_2x2(d, var, nombre):
    si, no = d[d[var] == 1].alternancia, d[d[var] == 0].alternancia
    tabla = [[si.sum(), len(si) - si.sum()], [no.sum(), len(no) - no.sum()]]
    _, pf = stats.fisher_exact(tabla, alternative="greater")
    p(f"    Con {nombre}: {si.mean():.0%} alternancia ({si.sum()}/{len(si)})   "
      f"Sin {nombre}: {no.mean():.0%} ({no.sum()}/{len(no)})   "
      f"diferencia {(si.mean()-no.mean())*100:+.0f} pp, p Fisher (una cola) = {pf:.3f}")


def h2(d, d_sin_esp):
    p("\n" + "=" * 78)
    p("HIPÓTESIS 2: desaceleración o recesión en los 2 años previos")
    p("=" * 78)
    p("  Definiciones:")
    p("   - recesión  = al menos uno de los dos años previos con crecimiento negativo")
    p("   - frenazo   = crecimiento promedio de los 2 últimos años menor que el de los 2 anteriores")

    for etiqueta, dd in (("todas", d), ("sin interinos ni anticipadas", d_sin_esp)):
        p(f"\n2.a) Comparación simple [{etiqueta}, n={len(dd)}]")
        tabla_2x2(dd, "recesion_ult2", "recesión")
        tabla_2x2(dd, "frenazo", "frenazo")

    p("\n2.b) Modelos logit (efectos marginales en puntos porcentuales; EE agrupados por país)")
    especs = {
        "M1 recesión": "alternancia ~ recesion_ult2",
        "M2 frenazo": "alternancia ~ frenazo",
        "M3 ambos + crec. 4a + reelección":
            "alternancia ~ recesion_ult2 + frenazo + crec_4a + presidente_candidato",
        "M4 continuo: niveles últ.2 y prim.2 + reelección":
            "alternancia ~ crec_ult2 + crec_prim2 + presidente_candidato",
    }
    for etiqueta, dd in (("todas", d), ("sin interinos ni anticipadas", d_sin_esp)):
        p(f"   [{etiqueta}]")
        for nombre, f in especs.items():
            m = logit_cluster(f, dd)
            vars_ = [v for v in m.params.index if v != "Intercept"]
            txt = ", ".join(f"{v} {efecto_marginal(m, v)[0]*100:+.1f}pp (p={efecto_marginal(m, v)[1]:.2f})"
                            for v in vars_)
            p(f"    {nombre:<48} {txt}")
        m = logit_cluster(especs["M4 continuo: niveles últ.2 y prim.2 + reelección"], dd)
        w = m.wald_test("crec_ult2 = crec_prim2", scalar=True)
        p(f"    ¿Pesan más los 2 años recientes que los 2 anteriores? (M4, Wald) p = {float(w.pvalue):.3f}")

    p("\n2.c) Robustez: elecciones del 2º semestre usando también el año electoral")
    dd = d.copy()
    tarde = dd.mes >= 7
    dd.loc[tarde, "crec_ult2"] = (dd.crec_t0 + dd.crec_t1)[tarde] / 2
    dd.loc[tarde, "crec_prim2"] = (dd.crec_t2 + dd.crec_t3)[tarde] / 2
    dd.loc[tarde, "recesion_ult2"] = (np.minimum(dd.crec_t0, dd.crec_t1) < 0)[tarde].astype(int)
    dd["frenazo"] = (dd.crec_ult2 < dd.crec_prim2).astype(int)
    dd = dd.dropna(subset=["crec_ult2"])
    tabla_2x2(dd, "recesion_ult2", "recesión")
    tabla_2x2(dd, "frenazo", "frenazo")

    graf_h2(d)


def graf_h2(d):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    grupos = {
        "Sin recesión\nni frenazo": (d.recesion_ult2 == 0) & (d.frenazo == 0),
        "Sólo frenazo": (d.recesion_ult2 == 0) & (d.frenazo == 1),
        "Recesión": d.recesion_ult2 == 1,
    }
    tasas = [d.alternancia[g].mean() for g in grupos.values()]
    ns = [g.sum() for g in grupos.values()]
    barras = ax[0].bar(list(grupos), tasas, color=["#2471a3", "#e67e22", "#c0392b"])
    for b_, t, n in zip(barras, tasas, ns):
        ax[0].text(b_.get_x() + b_.get_width() / 2, t + 0.02, f"{t:.0%}\n(n={n})", ha="center")
    ax[0].axhline(d.alternancia.mean(), ls="--", color="gray", label="Promedio general")
    ax[0].set_ylim(0, 1.05)
    ax[0].set_ylabel("Proporción de elecciones con alternancia")
    ax[0].set_title("Alternancia según la economía de los 2 años previos")
    ax[0].legend(fontsize=8)

    a = ax[1]
    colores = np.where(d.alternancia == 1, "#c0392b", "#2471a3")
    a.scatter(d.crec_prim2, d.crec_ult2, c=colores, s=30, alpha=0.75)
    lim = [min(d.crec_prim2.min(), d.crec_ult2.min()) - 1, max(d.crec_prim2.max(), d.crec_ult2.max()) + 1]
    a.plot(lim, lim, color="gray", ls="--", lw=1)
    a.axhline(0, color="k", lw=0.5)
    a.set_xlabel("Crecimiento promedio años t-4 y t-3 (%)")
    a.set_ylabel("Crecimiento promedio años t-2 y t-1 (%)")
    a.set_title("Debajo de la diagonal = se frenó  (rojo = alternancia)")
    fig.tight_layout()
    fig.savefig(FIG / "h2_desaceleracion.png", dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------- desempleo (H3)
def h3(d):
    p("\n" + "=" * 78)
    p("HIPÓTESIS 3: aumento del desempleo antes de la elección")
    p("=" * 78)
    d = d.dropna(subset=["dif_desemp_2a"]).copy()
    p(f"  Elecciones con datos de desempleo (1994 en adelante): {len(d)}, "
      f"alternancia promedio {d.alternancia.mean():.0%}")
    p("  Variable principal: cambio en la tasa de desempleo entre t-3 y t-1 (puntos porcentuales)")

    p("\n3.a) Alternancia según cuánto subió el desempleo en los 2 años previos")
    tramos = pd.cut(d.dif_desemp_2a, [-np.inf, -1, 0, 1, 2, np.inf],
                    labels=["bajó > 1 pt", "bajó hasta 1 pt", "subió hasta 1 pt",
                            "subió 1-2 pts", "subió > 2 pts"])
    t = d.groupby(tramos, observed=True).alternancia.agg(["mean", "sum", "count"])
    for k, r in t.iterrows():
        p(f"    {k:>16}: {r['mean']:5.0%}  ({int(r['sum'])}/{int(r['count'])})")

    sin_esp = d[d.caso_especial.isna()]
    sin_cand = d[d.presidente_candidato == 0]
    for etiqueta, dd in (("todas", d), ("sin interinos ni anticipadas", sin_esp),
                         ("sin presidente candidato", sin_cand)):
        p(f"\n3.b) Comparación simple [{etiqueta}, n={len(dd)}]")
        for k in (0, 1, 2):
            dd = dd.assign(subio=(dd.dif_desemp_2a > k).astype(int))
            tabla_2x2(dd, "subio", f"suba > {k} pts")

    p("\n3.c) Modelos logit (efectos marginales; EE agrupados por país)")
    especs = [
        ("cambio 2 años", "alternancia ~ dif_desemp_2a", "dif_desemp_2a"),
        ("cambio 2 años + reelección", "alternancia ~ dif_desemp_2a + presidente_candidato", "dif_desemp_2a"),
        ("cambio 2 años + crec. 4a + reelección",
         "alternancia ~ dif_desemp_2a + crec_4a + presidente_candidato", "dif_desemp_2a"),
        ("cambio en el mandato (4 años) + reelección",
         "alternancia ~ dif_desemp_4a + presidente_candidato", "dif_desemp_4a"),
        ("nivel de desempleo en t-1 + reelección",
         "alternancia ~ desemp_t1 + presidente_candidato", "desemp_t1"),
        ("cambio incluyendo año electoral + reelección",
         "alternancia ~ dif_desemp_2a_t0 + presidente_candidato", "dif_desemp_2a_t0"),
    ]
    base = pd.read_csv(AQUI / "data" / "base_analisis.csv")
    for nombre, f, v in especs:
        dd = base.dropna(subset=[v])
        m = logit_cluster(f, dd)
        em, pv = efecto_marginal(m, v)
        p(f"    {nombre:<46} n={len(dd):3d}  {v}: {em*100:+.1f} pp por punto (p = {pv:.2f})")
    p(f"\n    Correlación entre cambio del desempleo y crecimiento de los 2 años previos: "
      f"{np.corrcoef(d.dif_desemp_2a, d.crec_ult2)[0, 1]:.2f}")

    p("\n3.d) Casos con suba del desempleo de más de 2 puntos")
    for _, r in d[d.dif_desemp_2a > 2].sort_values("anio").iterrows():
        p(f"    {r.pais} {r.anio}: +{r.dif_desemp_2a:.1f} pts -> "
          f"{'perdió' if r.alternancia else 'ganó'} el oficialismo"
          f"{' (presidente candidato)' if r.presidente_candidato else ''}"
          f"{' [' + r.caso_especial + ']' if isinstance(r.caso_especial, str) else ''}")

    graf_h3(d)


def graf_h3(d):
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    jit = RNG.uniform(-0.04, 0.04, len(d))
    colores = np.where(d.alternancia == 1, "#c0392b", "#2471a3")
    ax.scatter(d.dif_desemp_2a, d.alternancia + jit, c=colores, alpha=0.7, s=28)
    m = smf.logit("alternancia ~ dif_desemp_2a", d).fit(disp=0)
    xx = np.linspace(d.dif_desemp_2a.min(), d.dif_desemp_2a.max(), 200)
    ax.plot(xx, m.predict(pd.DataFrame({"dif_desemp_2a": xx})), color="k", lw=1.5,
            label="Prob. estimada (logit)")
    ax.axvline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("Cambio del desempleo en los 2 años previos (puntos porcentuales)")
    ax.set_ylabel("Alternancia (1) / Continuidad (0)")
    ax.set_title("Desempleo y alternancia (elecciones 1994-2025)")
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "h3_desempleo.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    d = pd.read_csv(AQUI / "data" / "base_analisis.csv")
    d_sin_esp = d[d.caso_especial.isna()].copy()
    p(f"Base: {len(d)} elecciones presidenciales, 10 países, {d.anio.min()}-{d.anio.max()}")
    p(f"Alternancia promedio: {d.alternancia.mean():.0%}. "
      f"Casos especiales (interinos/anticipadas): {d.caso_especial.notna().sum()}")
    h1(d, d_sin_esp)
    h2(d, d_sin_esp)
    h3(d)
    (AQUI / "resultados.txt").write_text("\n".join(salida) + "\n", encoding="utf-8")
