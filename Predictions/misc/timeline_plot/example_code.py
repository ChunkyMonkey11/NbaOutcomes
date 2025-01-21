
import pandas as pd
import plotly.express as px
from datetime import datetime
#A = (df['PM_thru3_prev']<0) & (df['pts_diff_prev']>0) & (df['rest_numeric'].isin([1]))
#data = df.loc[A,['matchup','date','season','hundred_spread_fade','pts_diff']]
data = pd.read_csv("plot_data.csv")
data['date'] = pd.to_datetime(data['date'])
# Adjust the dates to fit within the range 10-01-2023 to 6-01-2024
def adjust_to_season_range(date):
    if date.month >= 10:  # Treat as part of the previous year's season (2023)
        return date.replace(year=2023)
    else:  # Treat as part of the next year's season (2024)
        return date.replace(year=2024)
# Apply the adjustment
data['date_adjusted'] = data['date'].apply(adjust_to_season_range)
# Ensure dates are within the range 10-01-2023 to 6-01-2024
# Convert date_adjusted to a string for better handling in Plotly
data['date_adjusted_str'] = data['date_adjusted'].dt.strftime('%Y-%m-%d')
# Recalculate the cumulative sum
#data['cumsum_hundred_ml'] = data.groupby('season')['hundred_ml'].cumsum()
data['cumsum_hundred_spread_fade'] = data.groupby('season')['hundred_spread_fade'].cumsum()
# 
# Create an interactive line plot with Plotly
fig = px.line(
    data,
    x='date_adjusted_str',
    y='cumsum_hundred_spread_fade',
    color='season',
    title="Fading teams that had a comeback win the night prior; a 'Buy low sell high' strategy,
    labels={'date_adjusted_str': 'Date','cumsum_hundred_spread_fade': 'Cumulative hundred_spread_fade'},
    line_group='season',
    hover_data=['matchup','pts_diff']
)
# Improve layout and styling
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Cumulative Profit",
    legend_title="Season",
    xaxis_tickangle=45,
    template="plotly_white"
)
fig.show()
