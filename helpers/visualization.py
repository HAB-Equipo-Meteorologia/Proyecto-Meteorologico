import math
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


def plot_counts(data, bins=30, cols=3):
    num_cols = len(data.columns)
    rows = math.ceil(num_cols / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5))
    axes = axes.flatten()

    for i, column in enumerate(data.columns):

        if data[column].nunique() < 10:

            # Count plot
            sns.countplot(data=data, x=column, color="blue", edgecolor="black", alpha=0.7, ax=axes[i])
            axes[i].set_title(f"Distribution of {column}", fontsize=14)
            axes[i].set_xlabel(column, fontsize=12)
            axes[i].set_ylabel("Count", fontsize=12)
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(axis="y", linestyle="--", alpha=0.6)
        else:

            # Histogram
            sns.histplot(data[column], bins=bins, kde=True, color="blue", edgecolor="black", alpha=0.7, ax=axes[i])
            axes[i].set_title(f"Distribution of {column}", fontsize=14)
            axes[i].set_xlabel(column, fontsize=12)
            axes[i].set_ylabel("Frequency", fontsize=12)
            axes[i].grid(axis="y", linestyle="--", alpha=0.6)

        for j in range(i + 1, len(axes)):
            axes[j].axis('off')

    plt.tight_layout()
    plt.show()


def plot_box_plots(data, cols=3):
    filtered_data = data[[column for column in data.columns if data[column].nunique() > 2]]

    num_cols = len(filtered_data.columns)
    rows = math.ceil(num_cols / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5))
    axes = axes.flatten()
    for i, column in enumerate(filtered_data.columns):
        axes[i].boxplot(filtered_data[column])
        axes[i].set_title(column)

        for j in range(i + 1, len(axes)):
            axes[j].axis('off')

    plt.tight_layout()
    plt.show()


def visualizar_columna(df, columna, target, palette="pastel", color='blue'):
    if df[columna].dtype == 'object' or df[columna].nunique() < 20:  # Categórica
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Gráfico de barras
        sns.countplot(data=df, x=columna, ax=axes[0], hue=columna, palette=palette)
        axes[0].set_title(f'Distribución de {columna}')
        axes[0].tick_params(axis='x', rotation=45)

        # Boxplot con target
        sns.boxplot(data=df, x=columna, y=target, ax=axes[1], hue=columna, palette=palette)
        axes[1].set_title(f'{columna} vs {target}')
        axes[1].tick_params(axis='x', rotation=45)

    else:  # Continua
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # Histograma
        sns.histplot(df[columna], bins=30, kde=True, ax=axes[0], color=color)
        axes[0].set_title(f'Histograma de {columna}')
        axes[0].set_xlabel('Valor')
        axes[0].set_ylabel('Frecuencia')

        # Boxplot
        sns.boxplot(data=df, x=columna, ax=axes[1], color=color)
        axes[1].set_title(f'Boxplot de {columna}')

        # Scatterplot
        sns.scatterplot(data=df, x=columna, y=target, ax=axes[2], color=color)
        axes[2].set_title(f'{columna} vs {target}')
        axes[2].set_xlabel(columna)
        axes[2].set_ylabel(target)

    plt.tight_layout()
    plt.show()


def histograma(df, title: str, col: str, x_label: str, y_label: str = "Frecuencia"):
    fig = px.histogram(
        df,
        x=col,
        title=title,
        labels={col: x_label},
        template="plotly_white"
    )
    fig.update_traces(
        marker_color='purple',
        marker_line_color='black',
        marker_line_width=1.5,
        opacity=0.85
    )
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label
    )
    return fig
