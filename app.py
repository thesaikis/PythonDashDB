import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd

from mysql_utils import MySQL
from mongodb_utils import MongoDB
from neo4j_utils import Neo4j
from neo4j import exceptions

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
)

# Create a simple style for each widget box container
widget_box_style = {
    "border": "2px solid white",
    "padding": "40px",
    "margin": "10px",
    "width": "30%",
    "box-sizing": "border-box",
    "display": "inline-block",
}

# Initialize our database connections
mysql = MySQL()
mysql.connect()

mongo = MongoDB()
mongo.connect()

neo = Neo4j()

# Query for the list of keywords that the user can select from
options = sorted([item[0] for item in mysql.execute_query("SELECT name FROM keyword")])

# Query for the list of faculty that the user can select from
faculty_options = sorted(
    [item[0] for item in mysql.execute_query("SELECT name FROM faculty")]
)

# Query for list of univeristy that the user can select from
university_options = sorted(
    [item[0] for item in mysql.execute_query("SELECT name FROM university")]
)

# Query for the min and max years of publications.
# Note that this is removing publications with a missing year.
min_year, max_year = mysql.execute_query(
    "SELECT MIN(year), MAX(year) FROM publication WHERE year > 0"
)[0]
min_year, max_year = int(min_year), int(max_year)

# This stores the selected faculty, so that we can access easily if the reviews are opened
selected_faculty = None

# Prepare a statement in MySQL
mysql.execute_query(
    "PREPARE stmt FROM "
    '"SELECT p.title, p.num_citations '
    "FROM publication p "
    "JOIN faculty_publication fp ON p.id = fp.publication_id "
    "JOIN faculty f ON f.id = fp.faculty_id "
    "WHERE f.name = ? "
    "AND p.title != 'A shape-based approach to the segmentation of medical imagery using level sets'"
    'ORDER BY p.num_citations DESC LIMIT 10"'
)


app.layout = html.Div(
    [
        html.Div(
            style={"textAlign": "center", "padding": "0 20%"},
            children=[
                html.H1("Matching Your Academic Interests With Universities"),
                dcc.Dropdown(
                    id="keywords-dropdown",
                    options=options,
                    multi=True,
                    placeholder="Search for keywords...",
                    style={"color": "blue"},
                ),
                dcc.RangeSlider(
                    min=(min_year),
                    max=(max_year),
                    value=[min_year, max_year],
                    id="year-range-slider",
                    marks=None,
                    tooltip={
                        "placement": "bottom",
                        "always_visible": True,
                        "style": {"color": "LightSteelBlue", "fontSize": "20px"},
                    },
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Top Universities"),
                        html.Div(
                            id="keyword-graph-container",
                            children=html.Div(  # This is an empty placeholder, since Dash gives an error for a nonexistent input without this.
                                dcc.Graph(
                                    figure=px.bar(),
                                    id="uni-keyword-graph",
                                    style={"display": "none"},
                                )
                            ),
                        ),
                    ],
                    style=widget_box_style,
                ),
                html.Div(
                    [
                        html.H1("Top Faculty"),
                        html.Div(
                            id="keyword-graph-faculty-container",
                            children=html.Div(  # This is an empty placeholder, since Dash gives an error for a nonexistent input without this.
                                dcc.Graph(
                                    figure=px.bar(),
                                    id="faculty-keyword-graph",
                                    style={"display": "none"},
                                )
                            ),
                        ),
                    ],
                    style=widget_box_style,
                ),
                html.Div(
                    [
                        html.H1("Highest Impact"),
                        html.Div(id="top-ranking-faculty-keyword-container"),
                    ],
                    style=widget_box_style,
                ),
            ],
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H1("University Information"),
                        dcc.Dropdown(
                            id="university-dropdown",
                            options=university_options,
                            multi=False,
                            placeholder="Search for universities...",
                            style={"color": "blue"},
                        ),
                        html.P(
                            id="selected-uni-info",
                            children="Select or search for a University for more information.",
                        ),
                    ],
                    style=widget_box_style,
                ),
                html.Div(
                    [
                        html.H1("Faculty Information"),
                        dcc.Dropdown(
                            id="faculty-dropdown",
                            options=faculty_options,
                            multi=False,
                            placeholder="Search for faculty...",
                            style={"color": "blue"},
                        ),
                        html.P(
                            id="selected-faculty-info",
                            children="Select or search for a Faculty Member for more information.",
                        ),
                    ],
                    style=widget_box_style,
                ),
            ],
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Add or Update Universities"),
                        dbc.Label("University Name"),
                        dbc.Input(
                            placeholder="Type name here...",
                            type="text",
                            id="update-uni-name",
                        ),
                        dbc.Label("Photo URL"),
                        dbc.Input(
                            placeholder="Enter Photo URL here...",
                            type="text",
                            id="update-uni-url",
                        ),
                        dbc.Button("Update", id="update-uni-button", n_clicks=0),
                        dbc.Button("Create New", id="create-uni-button", n_clicks=0),
                        html.Div(id="update-uni-result"),
                    ],
                    style=widget_box_style,
                ),
                html.Div(
                    [
                        html.H1("Total Research"),
                        dcc.Dropdown(
                            id="top-uni-dropdown",
                            options=university_options,
                            multi=True,
                            placeholder="Filter universities...",
                            style={"color": "blue"},
                        ),
                        html.Div(id="top-uni-container"),
                    ],
                    style=widget_box_style,
                ),
                html.Div(
                    [
                        html.H1("Most Cited Publications"),
                        html.Div(
                            id="faculty-most-cited-table",
                            style={"maxHeight": "350px", "overflow": "scroll"},
                        ),
                    ],
                    style=widget_box_style,
                ),
            ],
            style={"display": "flex", "justify-content": "center"},
        ),
        dbc.Modal(
            id="popup-modal",
            is_open=False,
            size="xl",
            children=[
                dbc.ModalHeader(dbc.ModalTitle("Faculty Reviews")),
            ],
            centered=True,
        ),
        # Dummy div used for testing
        html.Div(id="dummy", style={"display": "none"}),
    ]
)


@app.callback(
    [
        Output("keyword-graph-container", "children"),
        Output("keyword-graph-faculty-container", "children"),
    ],
    [Input("keywords-dropdown", "value")],
    [State("year-range-slider", "value")],
)
def update_keyword_widgets(selection, slider_value):
    if selection:
        search_min, search_max = slider_value

        keyword_str = ", ".join([f'"{keyword}"' for keyword in selection])

        # Query for university publication count
        query_university = " ".join(
            [
                "SELECT u.name, COUNT(DISTINCT p.id) c",
                "FROM university u",
                "JOIN faculty f on f.university_id = u.id",
                "JOIN faculty_publication fp on f.id = fp.faculty_id",
                "JOIN publication p ON p.id = fp.publication_id",
                "JOIN publication_keyword pk ON pk.publication_id = p.id",
                "JOIN keyword k ON k.id = pk.keyword_id",
                f"WHERE k.name IN ({keyword_str})",
                f"AND p.year >= {search_min} AND p.year <= {search_max}",
                "GROUP BY u.id",
                "ORDER BY c DESC",
            ]
        )
        res_university = mysql.execute_query(query_university)

        df_university = pd.DataFrame(
            res_university, columns=["University", "Publication Count"]
        )
        fig_university = px.bar(
            df_university,
            x="University",
            y="Publication Count",
            labels={
                "Publication Count": "Publication Count",
                "University": "University",
            },
            template="plotly_dark",
        )
        fig_university.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="#222",
        )
        graph_university = dcc.Graph(figure=fig_university, id="uni-keyword-graph")

        # Query for faculty publication count
        query_faculty = " ".join(
            [
                "SELECT f.name, COUNT(DISTINCT p.id) c",
                "FROM faculty f",
                "JOIN faculty_publication fp ON f.id = fp.faculty_id",
                "JOIN publication p ON p.id = fp.publication_id",
                "JOIN publication_keyword pk ON pk.publication_id = p.id",
                "JOIN keyword k ON k.id = pk.keyword_id",
                f"WHERE k.name IN ({keyword_str})",
                f"AND p.year >= {search_min} AND p.year <= {search_max}",
                "GROUP BY f.id",
                "ORDER BY c DESC",
                "LIMIT 100",
            ]
        )
        res_faculty = mysql.execute_query(query_faculty)

        df_faculty = pd.DataFrame(res_faculty, columns=["Faculty", "Publication Count"])
        fig_faculty = px.bar(
            df_faculty,
            x="Faculty",
            y="Publication Count",
            labels={"Publication Count": "Publication Count", "Faculty": "Faculty"},
            template="plotly_dark",
        )
        fig_faculty.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="#222",
        )
        graph_faculty = dcc.Graph(figure=fig_faculty, id="faculty-keyword-graph")

        return graph_university, graph_faculty
    else:
        return dash.no_update


@app.callback(
    Output("faculty-most-cited-table", "children"), Input("faculty-dropdown", "value")
)
def update_cited_table(value):
    if value:
        mysql.execute_query(f'SET @fac = "{value}"')
        result = mysql.execute_query("EXECUTE stmt USING @fac")
        df = pd.DataFrame(result, columns=["Publication", "Times Cited"])
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return dash.no_update


@app.callback(
    Output("top-uni-container", "children"), Input("top-uni-dropdown", "value")
)
def update_top_uni(selection):
    pipeline = [
        {"$unwind": "$keywords"},
        {
            "$group": {
                "_id": {"university": "$affiliation.name", "faculty_id": "$_id"},
                "uniqueKeywords": {"$addToSet": "$keywords.name"},
                "publications": {"$first": "$publications"},
            }
        },
        {
            "$group": {
                "_id": "$_id.university",
                "facultyCount": {"$sum": 1},
                "uniqueKeywordsCount": {"$sum": {"$size": "$uniqueKeywords"}},
                "distinctPublicationsCount": {"$sum": {"$size": "$publications"}},
            }
        },
        {
            "$project": {
                "_id": 0,
                "university": "$_id",
                "uniqueKeywordsCount": 1,
                "facultyCount": 1,
                "distinctPublicationsCount": 1,
            }
        },
        {"$sort": {"uniqueKeywordsCount": -1}},
    ]

    if selection:
        pipeline.insert(0, {"$match": {"affiliation.name": {"$in": selection}}})

    result = list(mongo.db["faculty"].aggregate(pipeline))
    df = pd.DataFrame(result)
    scatter = px.scatter(
        df,
        x="distinctPublicationsCount",
        y="facultyCount",
        size="uniqueKeywordsCount",
        hover_data=["university"],
        log_x=True,
        template="plotly_dark",
    )
    scatter.update_xaxes(title_text="Total Publications")
    scatter.update_yaxes(title_text="Faculty Members")
    scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="#222",
    )

    return dcc.Graph(figure=scatter)


@app.callback(
    Output("top-ranking-faculty-keyword-container", "children"),
    Input("keywords-dropdown", "value"),
    State("year-range-slider", "value"),
)
def update_top_faculty(selection, year_range):
    if selection:
        records, _, _ = neo.driver.execute_query(
            "WITH $selected_keywords AS keywords "
            "MATCH (f:FACULTY)--(p:PUBLICATION)-[l:LABEL_BY]-(k:KEYWORD) "
            "WHERE k.name IN keywords "
            "AND p.year >= $min_year AND p.year <= $max_year "
            "RETURN f.name, SUM(DISTINCT p.numCitations * l.score) as KRC "
            "ORDER BY KRC DESC "
            "LIMIT 10",
            selected_keywords=selection,
            min_year=year_range[0],
            max_year=year_range[1],
            database_="academicworld",
        )

        labels = []
        values = []

        for r in records:
            if r["KRC"] > 0:
                labels.append(r["f.name"])
                values.append(r["KRC"])

        fig = px.pie(names=labels, values=values, template="plotly_dark")
        fig.update_traces(
            textposition="inside", textinfo="percent+label", hoverinfo="value"
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="#222",
        )
        return dcc.Graph(figure=fig)

    return dash.no_update


@app.callback(
    Output("selected-uni-info", "children"),
    [Input("uni-keyword-graph", "clickData"), Input("university-dropdown", "value")],
)
def uni_display_click_data(clickData, dropdown_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "uni-keyword-graph":
        if clickData:
            name = clickData["points"][0]["x"]
        else:
            return dash.no_update
    elif triggered_id == "university-dropdown":
        if not dropdown_val:
            return dash.no_update
        name = dropdown_val
    else:
        return dash.no_update

    records, _, _ = neo.driver.execute_query(
        "MATCH (i:INSTITUTE {name: $name}) RETURN i",
        name=name,
        database_="academicworld",
    )

    imgURL = records[0].data()["i"]["photoUrl"]

    records, _, _ = neo.driver.execute_query(
        "MATCH (f:FACULTY)--(i:INSTITUTE {name: $name}) RETURN count(f)",
        name=name,
        database_="academicworld",
    )

    total_fac = records[0].data()["count(f)"]

    return [
        html.H3(name),
        html.Img(src=imgURL, style={"max-width": "100%", "height": "auto"}),
        html.P(f"Total published faculty members: {total_fac}"),
    ]


@app.callback(
    [Output("update-uni-result", "children"), Output("university-dropdown", "options")],
    [Input("update-uni-button", "n_clicks"), Input("create-uni-button", "n_clicks")],
    [State("update-uni-name", "value"), State("update-uni-url", "value")],
)
def update_uni_button(n_clicks_1, n_clicks_2, name, url):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if n_clicks_1 and triggered_id == "update-uni-button":
        neo.driver.execute_query(
            "MATCH (i:INSTITUTE {name: $name}) " "SET i.photoUrl = $url " "RETURN i",
            name=name,
            url=url,
            database_="academicworld",
        )

        return [html.P(name), html.P(url)], dash.no_update
    elif n_clicks_2 and triggered_id == "create-uni-button":
        try:
            neo.driver.execute_query(
                "CREATE (i:INSTITUTE {name: $name, photoUrl: $url}) RETURN i",
                name=name,
                url=url,
                database_="academicworld",
            )
        except exceptions.ConstraintError as _:
            return [html.P("Creation failed, constraint violated.")], dash.no_update

        new_university_options = sorted(university_options + [name])

        return [html.P("Created")], new_university_options

    return [], dash.no_update


@app.callback(
    Output("selected-faculty-info", "children"),
    [Input("faculty-keyword-graph", "clickData"), Input("faculty-dropdown", "value")],
)
def faculty_display_click_data(clickData, dropdown_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "faculty-keyword-graph":
        if clickData:
            name = clickData["points"][0]["x"]
        else:
            return dash.no_update
    elif triggered_id == "faculty-dropdown":
        if not dropdown_val:
            return dash.no_update
        name = dropdown_val
    else:
        return dash.no_update

    result = mongo.execute_query("faculty", {"name": name})
    result = list(result)

    if not list(result):
        return html.P(
            "There was an error finding this faculty member. This is likely due to a discrepancy between the data in each database."
        )

    imgURL = result[0]["photoUrl"]
    position = result[0]["position"]
    interest = result[0]["researchInterest"]
    email = result[0]["email"]
    phone = result[0]["phone"]
    uni = result[0]["affiliation"]["name"]

    global selected_faculty
    selected_faculty = result[0]["_id"]

    return [
        html.H3(name),
        html.Img(src=imgURL, style={"max-width": "100%", "height": "auto"}),
        html.P(f"Position: {position}"),
        html.P(f"Interest: {interest}"),
        html.P(f"Email: {email}"),
        html.P(f"Phone: {phone}"),
        html.P(f"University: {uni}"),
        dbc.Button(
            "Open Popup",
            id="open-faculty-review",
            n_clicks=0,
            style={"display": "block", "margin": "auto"},
        ),
    ]


@app.callback(
    [
        Output("popup-modal", "is_open"),
        Output("popup-modal", "children"),
    ],
    [Input("open-faculty-review", "n_clicks")],
    [State("popup-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    default_children = [
        dbc.ModalHeader(dbc.ModalTitle("Faculty Reviews")),
        dbc.Button("Leave a review", id="collapse-review", n_clicks=0),
        dbc.Collapse(
            [
                dbc.Input(
                    placeholder="Type your review here!",
                    style={"max-width": "50%"},
                    id="review-text",
                ),
                html.Div(
                    dcc.Slider(
                        min=1,
                        max=5,
                        step=1,
                        value=5,
                        id="review-rating",
                    ),
                    style={"max-width": "50%"},
                ),
                dbc.Button("Submit Review", id="submit-review", n_clicks=0),
            ],
            id="review-input",
            is_open=False,
        ),
    ]

    update = {"$set": {"reviews": []}}

    if n1:
        global selected_faculty

        mongo.collection.update_one(
            {"_id": selected_faculty, "reviews": {"$exists": False}}, update
        )

        result = mongo.execute_query("faculty", {"_id": selected_faculty})

        if len(result[0]["reviews"]) == 0:
            default_children.append(dbc.ModalBody("No reviews!"))
        else:
            default_children.append(dbc.ModalBody(html.H5("Reviews:")))
            for r in result[0]["reviews"]:
                default_children.append(
                    dbc.ModalBody(f"{r['review-text']}, {r['review-rating']}/5")
                )

        return not is_open, default_children

    return is_open, default_children


@app.callback(
    Output("review-input", "is_open"),
    [Input("collapse-review", "n_clicks")],
    [State("review-input", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("dummy", "children"),
    [Input("submit-review", "n_clicks")],
    [
        State("review-text", "value"),
        State("review-rating", "value"),
    ],
)
def submit_review(n1, text, rating):
    if n1:
        mongo.collection.update_one(
            {"_id": selected_faculty},
            {"$push": {"reviews": {"review-text": text, "review-rating": rating}}},
        )


if __name__ == "__main__":
    app.run_server(debug=True)
