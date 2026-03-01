import pandas as pd

def appareil_dominant_par_mois(path_csv: str, uai: str, annee: int) -> pd.DataFrame:
    df = pd.read_csv(path_csv, sep=";", dtype={"UAI": "string"})
    df["debutSemaine"] = pd.to_datetime(df["debutSemaine"], errors="coerce")

    df = df[(df["UAI"] == uai) & (df["debutSemaine"].dt.year == int(annee))].copy()

    visit_cols = {
        "Ordinateur": "visites_ordinateur",
        "Smartphone": "visites_smartphone",
        "Tablette": "visites_tablette",
    }

    for col in visit_cols.values():
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Mois"] = df["debutSemaine"].dt.to_period("M").astype(str)
    agg = df.groupby("Mois")[list(visit_cols.values())].sum().reset_index()

    agg["Appareil_dominant"] = agg[list(visit_cols.values())].idxmax(axis=1)

    return agg.sort_values("Mois")


if __name__ == "__main__":
    chemin = "fr-en-dnma-par-uai-appareils.csv"
    UAI = "0010024W"
    ANNEE = 2025

    result = appareil_dominant_par_mois(chemin, UAI, ANNEE)
    print(result.to_string(index=False))