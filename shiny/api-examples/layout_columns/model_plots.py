import matplotlib.pyplot as plt
import numpy as np

from shiny import ui


def plot_loss_over_time():
    epochs = np.arange(1, 101)
    loss = 1000 / np.sqrt(epochs) + np.random.rand(100) * 25

    fig = plt.figure(figsize=(10, 6))
    plt.plot(epochs, loss)
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    return fig


def plot_accuracy_over_time():
    epochs = np.arange(1, 101)
    accuracy = np.sqrt(epochs) / 12 + np.random.rand(100) * 0.15
    accuracy = [np.min([np.max(accuracy[:i]), 1]) for i in range(1, 101)]

    fig = plt.figure(figsize=(10, 6))
    plt.plot(epochs, accuracy)
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    return fig


def plot_feature_importance():
    features = ["Product Category", "Price", "Brand", "Rating", "Number of Reviews"]
    importance = np.random.rand(5)

    fig = plt.figure(figsize=(10, 6))
    plt.barh(features, importance)
    plt.xlabel("Importance")
    return fig


card_loss = ui.card(
    ui.card_header("Loss Over Time"),
    ui.output_plot("loss_over_time"),
    full_screen=True,
)

card_acc = ui.card(
    ui.card_header("Accuracy Over Time"),
    ui.output_plot("accuracy_over_time"),
    full_screen=True,
)

card_feat = ui.card(
    ui.card_header("Feature Importance"),
    ui.output_plot("feature_importance"),
    full_screen=True,
)
