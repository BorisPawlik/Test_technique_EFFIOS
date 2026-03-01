import pandas as pd

def aggregate_dnma(path_csv: str, uai: str, granularite: str) -> pd.DataFrame:
    gran = granularite.strip().lower()
    if gran not in {"année", "annee", "mois"}:
        raise ValueError('granularite doit être "Année" ou "Mois".')

    df = pd.read_csv(path_csv, sep=";", dtype={"UAI": "string"})
    df["debutSemaine"] = pd.to_datetime(df["debutSemaine"], errors="coerce")
    df = df[df["UAI"] == uai].copy()

    visit_cols = ["visites_ordinateur", "visites_smartphone", "visites_tablette", "visites_autreappareil"]
    user_cols  = ["utilisateurs_ordinateur", "utilisateurs_smartphone", "utilisateurs_tablette", "utilisateurs_autreAppareil"]
    duree_cols = ["duree_ordinateur", "duree_smartphone", "duree_tablette", "duree_autreAppareil"]

    df[visit_cols + user_cols] = (
        df[visit_cols + user_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

    def to_seconds(series: pd.Series) -> pd.Series:
        s = series.fillna("00:00:00").astype(str).str.strip()
        s = s.str.replace(r"^(\d+:\d+:\d+):(\d+)$", r"\1.\2", regex=True)
        td = pd.to_timedelta(s, errors="coerce").fillna(pd.Timedelta(0))
        return td.dt.total_seconds()

    duree_sec = pd.DataFrame({c: to_seconds(df[c]) for c in duree_cols})

    df["visites_total"] = df[visit_cols].sum(axis=1)
    df["utilisateurs_total"] = df[user_cols].sum(axis=1)

    df["duree_num"] = (df[visit_cols].values * duree_sec[duree_cols].values).sum(axis=1)

    if gran in {"année", "annee"}:
        df["Periode"] = df["debutSemaine"].dt.year.astype(str)
    else:
        df["Periode"] = df["debutSemaine"].dt.to_period("M").astype(str)

    out = df.groupby("Periode", as_index=False).agg(
        nb_visites_total=("visites_total", "sum"),
        nb_utilisateurs_total=("utilisateurs_total", "sum"),
        duree_num=("duree_num", "sum"),
        duree_den=("visites_total", "sum"),
    )

    out["duree_moyenne_ponderee_sec"] = out["duree_num"].div(out["duree_den"]).fillna(0)
    out["duree_moyenne_ponderee"] = (
        pd.to_timedelta(out["duree_moyenne_ponderee_sec"].round(), unit="s")
        .astype(str)
        .str.split()
        .str[-1]
    )

    return (
        out.drop(columns=["duree_num", "duree_den", "duree_moyenne_ponderee_sec"])
           .sort_values("Periode")
    )


if __name__ == "__main__":
    chemin = "fr-en-dnma-par-uai-appareils.csv"
    UAI = "0010024W"
    GRANULARITE = "Mois"

    result = aggregate_dnma(chemin, UAI, GRANULARITE)
    print(result.to_string(index=False))