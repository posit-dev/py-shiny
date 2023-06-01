# Import Libraries
from shiny import App, render, ui
import pickle
import numpy as np


#Load the pretrain Model
my_model = pickle.load(open('model1.pkl','rb'))


app_ui = ui.page_fluid(
    ui.h2("Hello Shiny!"),
    ui.input_slider("area", "Area", 1500, 10000, 400),
    ui.input_slider("bedroom", "Bedroom", 1, 10, 0),
    ui.input_slider("age", "Age", 0, 50, 0),
    ui.input_slider("bathroom", "Bathroom", 1, 10, 0),


    ui.output_text_verbatim("txt"),
)



def server(input, output, session):
    @output
    @render.text
    def txt():
        area = input.area()
        bedroom =input.bedroom()
        age = input.age()
        bathroom = input.bathroom()
        mod_l = np.array([area,bedroom,age,bathroom]).reshape(1,-1)
        model = my_model.predict(mod_l)
        return f"The price of house is ${model[0]:.2f}"


app = App(app_ui, server)
