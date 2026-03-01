import pandas as pd
import matplotlib.pyplot as plt

def plot_visites_par_appareil_par_mois(path_csv: str, uai: str, annee: int) -> None:
    df = pd.read_csv(path_csv, sep=";", dtype={"UAI": "string"})
    df["debutSemaine"] = pd.to_datetime(df["debutSemaine"], errors="coerce")

    df = df[(df["UAI"] == uai) & (df["debutSemaine"].dt.year == int(annee))].copy()

    visit_cols = {
        "Ordinateur": "visites_ordinateur",
        "Smartphone": "visites_smartphone",
        "Tablette": "visites_tablette",
    }

    for c in visit_cols.values():
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    df["Mois"] = df["debutSemaine"].dt.to_period("M").dt.to_timestamp()
    agg = df.groupby("Mois", as_index=False)[list(visit_cols.values())].sum()

    plt.figure()
    for label, col in visit_cols.items():
        plt.plot(agg["Mois"], agg[col], label=label)

    plt.title(f"Évolution mensuelle des visites par appareil")
    plt.xlabel("Mois")
    plt.ylabel("Nombre de visites")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    chemin = "fr-en-dnma-par-uai-appareils.csv"
    UAI = "0010024W"
    ANNEE = 2025

    plot_visites_par_appareil_par_mois(chemin, UAI, ANNEE)