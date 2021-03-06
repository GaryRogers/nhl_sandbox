# NHL Sandbox

Playing with Python, Pandas, Nummy, and NHL data

Uses data pulled from NHL API, and normalizes down interesting aspects of the game for analysis.

## Scripts

### nhl_import.py

Pull data from NHL API to local json files.

### extract_faceoff_data.py

Take a game file and produce a faceoff extract

Example faceoff data:

```json
{
    "game_id": "2019020010",
    "season": "20192020",
    "game_start_time": "2019-10-04T00:30:00Z",
    "game_tz": "CST",
    "play_id": 3,
    "game_time": 0,
    "description": "Patrice Bergeron faceoff won against Tyler Seguin",
    "period": "1",
    "coordinates": "0.0,0.0",
    "player": "Tyler Seguin",
    "team": "DAL",
    "opponent": "Patrice Bergeron",
    "opposing_team": "BOS",
    "home_ice": true,
    "power_play": false,
    "penelty_kill": false,
    "zone": "NEUTRAL_ZONE",
    "score_diff": 0,
    "win": false
}
```

## Notes

Check out [iPython Interactive Widgets](https://ipywidgets.readthedocs.io/en/stable/)

Teams to Load:

'Tampa Bay Lightning'
'Ottawa Senators'
'Buffalo Sabres'
'Carolina Hurricanes'
--'Toronto Maple Leafs'
-- 'Boston Bruins'
'Detroit Red Wings'
'Montréal Canadiens'


'Columbus Blue Jackets'
'Arizona Coyotes'
'Florida Panthers'
'Chicago Blackhawks'
'New Jersey Devils'
'New York Islanders'
-- 'Pittsburgh Penguins'
'St. Louis Blues'
'Vancouver Canucks'
'Winnipeg Jets'
'Calgary Flames'
'Philadelphia Flyers'
'Dallas Stars'
'Vegas Golden Knights'
'Edmonton Oilers'
'Los Angeles Kings'
'Anaheim Ducks'
'Minnesota Wild'
'San Jose Sharks'
'Nashville Predators'
'New York Rangers'
'Colorado Avalanche'
--'Washington Capitals'