from recipe.models import Recipe  # you need to connect parameters from books model
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import numpy as np


# define a function that takes the ID
def get_recipe_from_title(val):
    # this ID is used to retrieve the name from the record
    recipe_title = Recipe.objects.get(title=val)
    # and the name is returned back
    return recipe_title


def get_graph():
    # create a BytesIO buffer for the image
    buffer = BytesIO()

    # create a plot with a bytesIO object as a file-like object. Set format to png
    plt.savefig(buffer, format="png")

    # set cursor to the beginning of the stream
    buffer.seek(0)

    # retrieve the content of the file
    image_png = buffer.getvalue()

    # encode the bytes-like object
    graph = base64.b64encode(image_png)

    # decode to get the string as output
    graph = graph.decode("utf-8")

    # free up the memory of buffer
    buffer.close()

    # return the image/graph
    return graph


# chart_type: user input o type of chart,
# data: pandas dataframe
def get_chart(chart_type, data, **kwargs):
    # switch plot backend to AGG (Anti-Grain Geometry) - to write to file
    # AGG is preferred solution to write PNG files
    plt.switch_backend("AGG")

    # Set the default style for the plot
    plt.rcParams["axes.facecolor"] = "lightgray"
    plt.rcParams["text.color"] = "#632623"

    # specify figure size
    fig = plt.figure(figsize=(12, 6), facecolor="#2ac549")

    # select chart_type based   on user input from the form
    if chart_type == "#1":
        plt.title("Calorie Content per Ingredient", pad=26)
        plt.bar(
            data.index, data["Calorie Content"], label="Calorie Content"
        )  # Add label
        plt.xlabel("Ingredient", color="#632623")
        plt.ylabel("Calories", color="#632623")
        plt.legend()  # This will now show the legend with the "Calorie Content" label.

    elif chart_type == "#2":
        plt.title("Grams per Ingredient", pad=26)
        plt.plot(data.index, data["Grams"], label="Grams")  # Add label
        plt.xlabel("Ingredient", color="#632623")
        plt.ylabel("Grams", color="#632623")
        plt.legend()  # This will now show the legend with the "Grams" label.

    elif chart_type == "#3":
        plt.title("Cost per Ingredient", pad=36)

        # Remove the dollar sign from the "Cost" string
        data["Cost"] = data["Cost"].str.replace("$", "")

        # Convert the "Cost" column to numeric values
        data["Cost"] = data["Cost"].astype(float)

        # Create the pie chart and store the patches (slices) and text labels
        patches, _, _ = plt.pie(data["Cost"], labels=None, autopct="%1.1f%%")

        # Add ingredient name and cost amount to each slice as text labels
        for patch, cost, ingredient in zip(patches, data["Cost"], data.index):
            label = (
                f"{ingredient}\n${cost:.2f}"  # Display ingredient name and cost amount
            )

            # Calculate the angle of the slice
            angle = (patch.theta2 - patch.theta1) / 2.0 + patch.theta1

            # Calculate the position of the label outside the pie chart
            x = patch.r * 1.4 * np.cos(np.deg2rad(angle))
            y = patch.r * 1.2 * np.sin(np.deg2rad(angle))

            plt.text(
                x,
                y,
                label,
                ha="center",
                va="center",
                fontsize=8,
            )

        plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
    else:
        print("unknown chart type")

    # specify layout details
    plt.tight_layout()

    # render the graph to file
    chart = get_graph()
    return chart
