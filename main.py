import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


pd.set_option('display.max_columns', None)

players = pd.read_csv("players.csv")
appearances = pd.read_csv("appearances.csv")
games = pd.read_csv("games.csv")
competitions = pd.read_csv("competitions.csv")

print("Players:", players.shape)
print("Appearances:", appearances.shape)
print("Games:", games.shape)
print("Competitions:", competitions.shape)

games_2025 = games[games["season"] == 2025].copy()
print("2025 sezonundaki maç sayısı:", games_2025.shape[0])

appearances_2025 = appearances[appearances["game_id"].isin(games_2025["game_id"])].copy()

print("2025 sezonundaki oyuncu-maç kaydı:", appearances_2025.shape[0])
print("2025 sezonundaki farklı oyuncu sayısı:", appearances_2025["player_id"].nunique())

player_stats = (
    appearances_2025.groupby("player_id").agg(
        appearances =("game_id","count"),
        minutes_played = ("minutes_played","sum"),
        goals = ("goals","sum"),
        assists = ("assists","sum"),
        yellow_cards =  ("yellow_cards","sum"),
        red_cards = ("red_cards","sum"),
    )
    .reset_index()
)
print("Oyuncu bazlı tablo boyutu:", player_stats.shape)
print(player_stats.head())

player_stats = player_stats[
    player_stats["minutes_played"] >= 450
].copy()

print("450 dakika sonrası oyuncu sayısı:",player_stats.shape[0])


player_stats["goals_per_90"] = (
    player_stats["goals"] / player_stats["minutes_played"] * 90
)
player_stats["assists_per_90"] = (
    player_stats["assists"] / player_stats["minutes_played"] * 90
)

player_stats["goal_contributions"] = (
    player_stats["goals"] + player_stats["assists"]
)

player_stats["goal_contributions_per_90"] = (
    player_stats["goal_contributions"] / player_stats["minutes_played"] * 90
)

print(player_stats.head())

print(
    player_stats[
        [
            "player_id",
            "appearances",
            "minutes_played",
            "goals",
            "assists",
            "goals_per_90",
            "assists_per_90",
            "goal_contributions_per_90",
        ]
    ].head()
)

player_info = players[[
    "player_id",
    "name",
    "date_of_birth",
    "position",
    "sub_position",
    "foot",
    "height_in_cm",
    "current_club_name",
    "market_value_in_eur"
]].copy()

df= player_stats.merge(
    player_info,
    on ="player_id",
    how="left",
)

print(df.shape)
print(df.head())

df["date_of_birth"] = pd.to_datetime(df["date_of_birth"],
                                     errors = "coerce")

reference_date = pd.Timestamp("2026-06-30")
df["age"] = (
(reference_date - df["date_of_birth"]).dt.days / 365.25
).round(1)

print(
    df[[
        "name",
        "age",
        "position",
        "current_club_name",
        "minutes_played",
        "goals",
        "assists",
        "goal_contributions_per_90",
        "market_value_in_eur"
    ]].head(10)
)

missing_values = df.isnull().sum().sort_values(ascending = False)

print("Eksik değer sayıları:")
print(missing_values)

print("\nPozisyon dağılımı:")
print(df["position"].value_counts())

df = df[df["position"] != "Goalkeeper"].copy()


print("Kaleciler çıkarıldıktan sonra oyuncu sayısı:",df.shape[0])
print(df["position"].value_counts())

print(
    "Piyasa değeri eksik oyuncu sayısı:",
    df["market_value_in_eur"].isnull().sum()
)
print(
    "Piyasa değeri sıfır olan oyuncu sayısı:",
    (df["market_value_in_eur"]==0).sum()
)

df = df.dropna(subset=["market_value_in_eur"]).copy()
print("Target temizliği sonrası oyuncu sayısı:", df.shape[0])

print("\nKalan eksik değerler:")
print(
    df.isnull()
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
df["foot"] = df["foot"].fillna("Unknown")

df["height_in_cm"] = df["height_in_cm"].fillna(
    df["height_in_cm"].median()
)

print("\nEksik değer kontrolü:")
print(df.isnull().sum().sort_values(ascending=False).head(10))

df.to_csv("clean_player_data.csv", index=False)

print("\nTemiz veri kaydedildi.")
print("Son oyuncu sayısı:", df.shape[0])
print("Son sütun sayısı:", df.shape[1])



plt.figure(figsize=(10, 6))

sns.histplot(
    df["market_value_in_eur"] / 1_000_000,
    bins=40,
    kde=True
)

plt.xlabel("Piyasa Değeri (Milyon €)")
plt.ylabel("Oyuncu Sayısı")
plt.title("Oyuncuların Piyasa Değeri Dağılımı")

plt.show()

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="age",
    y=df["market_value_in_eur"] / 1_000_000,
    alpha=0.5
)

plt.xlabel("Yaş")
plt.ylabel("Piyasa Değeri (Milyon €)")
plt.title("Yaş ve Piyasa Değeri İlişkisi")

plt.show()

age_value = (
    df.groupby("age")["market_value_in_eur"]
    .median()
    .reset_index()
)

plt.figure(figsize=(10, 6))

sns.lineplot(
    data=age_value,
    x="age",
    y="market_value_in_eur"
)

plt.xlabel("Yaş")
plt.ylabel("Medyan Piyasa Değeri (€)")
plt.title("Yaşa Göre Medyan Piyasa Değeri")

plt.show()

plt.figure(figsize=(9, 6))

sns.boxplot(
    data=df,
    x="position",
    y=df["market_value_in_eur"] / 1_000_000
)

plt.xlabel("Pozisyon")
plt.ylabel("Piyasa Değeri (Milyon €)")
plt.title("Pozisyonlara Göre Piyasa Değeri")

plt.show()

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="goal_contributions_per_90",
    y=df["market_value_in_eur"] / 1_000_000,
    hue="position",
    alpha=0.6
)

plt.xlabel("90 Dakika Başına Gol Katkısı")
plt.ylabel("Piyasa Değeri (Milyon €)")
plt.title("Gol Katkısı ve Piyasa Değeri İlişkisi")

plt.show()

df["log_market_value"] = np.log1p(df["market_value_in_eur"])

print(
    df[["market_value_in_eur", "log_market_value"]]
    .describe()
)

features = [
    "age",
    "position",
    "sub_position",
    "foot",
    "height_in_cm",
    "appearances",
    "minutes_played",
    "goals",
    "assists",
    "goals_per_90",
    "assists_per_90",
    "goal_contributions_per_90",
    "yellow_cards",
    "red_cards"
]

target = "log_market_value"

model_df = df[features + [target]].copy()

print("\nModel veri seti boyutu:", model_df.shape)
print("\nEksik değerler:")
print(model_df.isnull().sum())

numeric_features = [
    "age",
    "height_in_cm",
    "minutes_played",
    "goals_per_90",
    "assists_per_90",
    "yellow_cards",
    "red_cards"
]

categorical_features = [
    "position",
    "sub_position",
    "foot"
]

X = model_df[numeric_features + categorical_features]
y = model_df["log_market_value"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Train:", X_train.shape)
print("Test:", X_test.shape)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            StandardScaler(),
            numeric_features
        ),
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ]
)

models = {
    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        random_state=42
    )
}

results = []

for name, model in models.items():

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    pipeline.fit(X_train, y_train)

    pred_log = pipeline.predict(X_test)

    # Log değerlerini tekrar Euro'ya çeviriyoruz
    actual = np.expm1(y_test)
    predicted = np.expm1(pred_log)

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    # R²'yi log ölçekte hesaplıyoruz
    r2 = r2_score(y_test, pred_log)

    results.append({
        "Model": name,
        "MAE (€)": mae,
        "RMSE (€)": rmse,
        "R2 (log)": r2
    })

results_df = pd.DataFrame(results)

print("\nMODEL SONUÇLARI")
print(results_df.sort_values("MAE (€)"))

best_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

best_model.fit(X_train, y_train)

pred_log = best_model.predict(X_test)

actual_eur = np.expm1(y_test)
predicted_eur = np.expm1(pred_log)

comparison = pd.DataFrame({
    "Gercek_Deger": actual_eur,
    "Tahmin_Deger": predicted_eur
})

comparison["Mutlak_Hata"] = abs(
    comparison["Gercek_Deger"] - comparison["Tahmin_Deger"]
)

comparison["Yuzde_Hata"] = (
    comparison["Mutlak_Hata"] /
    comparison["Gercek_Deger"]
) * 100

print("\nTahmin örnekleri:")
print(comparison.head(10))

print("\nMedyan mutlak hata (€):")
print(comparison["Mutlak_Hata"].median())

print("\nMedyan yüzde hata:")
print(comparison["Yuzde_Hata"].median())

plt.figure(figsize=(8, 6))

plt.scatter(
    actual_eur / 1_000_000,
    predicted_eur / 1_000_000,
    alpha=0.5
)

max_value = max(
    actual_eur.max(),
    predicted_eur.max()
) / 1_000_000

plt.plot(
    [0, max_value],
    [0, max_value],
    linestyle="--"
)

plt.xlabel("Gerçek Piyasa Değeri (Milyon €)")
plt.ylabel("Tahmin Edilen Değer (Milyon €)")
plt.title("Gerçek ve Tahmin Edilen Piyasa Değerleri")

plt.show()

print(
    competitions[
        [
            "competition_id",
            "name",
            "type",
            "country_name"
        ]
    ].head(30)
)

print("\nCompetition type dağılımı:")
print(competitions["type"].value_counts())

print("\nGames_kolonları:")
print(games_2025.columns.tolist())

print("appearances_2025 kolonlari:")
print(appearances_2025.columns.tolist())

print("\ncompetitions kolonlari:")
print(competitions.columns.tolist())

best_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])


best_model.fit(X, y)


df["predicted_log_value"] = best_model.predict(X)


df["predicted_market_value"] = np.expm1(
    df["predicted_log_value"]
)

print("\nTahminler olusturuldu.")

df["value_difference"] = (
    df["predicted_market_value"]
    - df["market_value_in_eur"]
)

df["hidden_gem_score"] = (
    df["value_difference"]
    / df["market_value_in_eur"]
) * 100

hidden_gems = df[
    (df["age"] <= 23) &
    (df["market_value_in_eur"] <= 20_000_000) &
    (df["minutes_played"] >= 900) &
    (df["hidden_gem_score"] > 0)
].copy()

hidden_gems = hidden_gems.sort_values(
    "hidden_gem_score",
    ascending=False
)

print("\nTOP HIDDEN GEMS")

print(
    hidden_gems[
        [
            "name",
            "age",
            "position",
            "current_club_name",
            "market_value_in_eur",
            "predicted_market_value",
            "hidden_gem_score",
            "goals_per_90",
            "assists_per_90"
        ]
    ].head(20)
)

hidden_gems["market_value_m"] = (
    hidden_gems["market_value_in_eur"] / 1_000_000
).round(2)

hidden_gems["predicted_value_m"] = (
    hidden_gems["predicted_market_value"] / 1_000_000
).round(2)

hidden_gems["hidden_gem_score"] = (
    hidden_gems["hidden_gem_score"]
).round(1)

print("\nDAHA OKUNAKLI TOP 10")

print(
    hidden_gems[
        [
            "name",
            "age",
            "position",
            "current_club_name",
            "market_value_m",
            "predicted_value_m",
            "hidden_gem_score"
        ]
    ].head(10)
)

n8n_output = df[
    [
        "name",
        "age",
        "position",
        "sub_position",
        "current_club_name",
        "market_value_in_eur",
        "predicted_market_value",
        "hidden_gem_score",
        "minutes_played",
        "goals_per_90",
        "assists_per_90",
        "goal_contributions_per_90"
    ]
].copy()

n8n_output.to_csv(
    "football_scout_output.csv",
    index=False
)

print("football_scout_output.csv olusturuldu.")
print(n8n_output.head())