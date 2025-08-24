import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd

db = {}
for sheet_name in ["Retter", "Ingredienser", "Forbrug"]:
    db[sheet_name] = pd.read_excel("recipes.xlsx", sheet_name=sheet_name)

recipe_options = []
for i in db["Retter"].index:
    option = {"label": db["Retter"].loc[i, "Navn"], "value": db["Retter"].loc[i, "ID"]}
    recipe_options.append(option)

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True
)

recipes = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("Opskrifter", className="card-title"),
                html.P(
                    "Vælg de opskrifter som du ønsker at generere indkøbslisten ud fra.",
                    className="card-text",
                ),
                dcc.Dropdown(id="recipes-dropdown", options=recipe_options, multi=True),
            ]
        )
    ]
)

chosen_recipes = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("Valgte opskrifter", className="card-title"),
                html.P("De valgte opskrifter kan ses herunder.", className="card-text"),
                dcc.Clipboard(
                    id="clipboard-chosen",
                    target_id="chosen-recipes",
                    style={"margin-bottom": "10px"},
                ),
                dbc.Table(id="chosen-recipes", children=[], bordered=True),
            ]
        )
    ]
)

groceries = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("Samlet indkøbsliste", className="card-title"),
                html.P(
                    "Den generede indkøbsliste kan ses herunder.", className="card-text"
                ),
                dcc.Clipboard(
                    id="clipboard",
                    target_id="groceries-table",
                    style={"margin-bottom": "10px"},
                ),
                dbc.Table(
                    id="groceries-table",
                    children=[],
                    bordered=True,
                ),
            ]
        )
    ]
)

app.layout = html.Div(
    [
        # Header
        dbc.Col(
            html.H1(
                "Madplanlægger",
                style={
                    "text-align": "center",
                    "padding-top": 20,
                    "padding-bottom": 20,
                },
            ),
            width={"size": 12},
        ),
        dbc.Container(
            [
                dbc.Row([recipes], style={"padding-bottom": 20}),
                dbc.Row([chosen_recipes], style={"padding-bottom": 20}),
                dbc.Row([groceries]),
            ]
        ),
    ],
    style={"padding-left": 20, "padding-right": 20, "padding-top": 20},
)


@app.callback(
    Output(component_id="chosen-recipes", component_property="children"),
    Input(component_id="recipes-dropdown", component_property="value"),
)
def update_chosen_recipes(input_value):
    if input_value is not None:
        chosen = db["Retter"][db["Retter"]["ID"].isin(input_value)]
        rows = []
        for i in chosen.index:
            rows.append(
                html.Tr(
                    [
                        html.Td(chosen.loc[i, "Navn"]),
                    ]
                )
            )
        return [html.Thead(html.Tr([html.Th("Opskrift")]))] + [html.Tbody(rows)]
    return [html.Thead(html.Tr([html.Th("Opskrift")]))] + [html.Tbody([])]


@app.callback(
    Output(component_id="groceries-table", component_property="children"),
    Input(component_id="recipes-dropdown", component_property="value"),
)
def update_grocery_list(input_value):
    table_header = [
        html.Thead(
            html.Tr([html.Th("Ingrediens"), html.Th("Antal"), html.Th("Kategori")])
        )
    ]
    if input_value is not None:
        groceries = (
            db["Forbrug"][db["Forbrug"]["RetID"].isin(input_value)]
            .groupby(["Ingrediens", "Enhed", "Kategori"])["Antal"]
            .sum()
            .reset_index(drop=False)
            .sort_values(by=["Kategori"])
        )
        print(groceries)

        rows = []
        for i in groceries.index:
            rows.append(
                html.Tr(
                    [
                        html.Td(groceries.loc[i, "Ingrediens"]),
                        html.Td(
                            str(groceries.loc[i, "Antal"])
                            + " "
                            + groceries.loc[i, "Enhed"]
                        ),
                        html.Td(groceries.loc[i, "Kategori"]),
                    ]
                )
            )
        return table_header + [html.Tbody(rows)]
    return table_header


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
