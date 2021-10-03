from flask import Flask, request
from werkzeug.utils import redirect
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import json
import bcrypt
import mysql.connector
from mysql.connector.errors import Error
from soccerapi.api import ApiUnibet
import joblib
from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
import shutil
from apscheduler.schedulers.background import BackgroundScheduler
import os
import sys
from data_processing.receive_data import get_csv_files
from data_processing.ml import DataPreparation
from selenium import webdriver

targeted_competitions = {
    "Italy": "Serie A",
    "England": "Premier League",
    "Germany": "Bundesliga",
    "France": "Ligue 1",
    "Spain": "La Liga"
}

def is_empty(storage):
    return len(storage) == 0

def generate_random(num_of_digits):
    return ''.join(["{}".format(random.randint(0, 9))for _ in range(0, num_of_digits)])

def send_email(recipient_username, recipient_email):
    """
    Utilizes smtplib gmail authentication which
    is used for the confirmation of the email
    filled in by the user - only after clicking the link
    in the email sent, the user is registered in the database
    """
    data = {}
    with open("credentials/email.json", "r") as file:
        data = json.load(file)
    port = 465
    token = generate_random(10)
    sender_email = data["email"]
    password = data["email_password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = "Registration Confirmation"
    message["From"] = "Mock Football Bets"
    message["To"] = recipient_email

    email_body = get_email_body(recipient_username, token)
    content = MIMEText(email_body, "html")
    message.attach(content)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, recipient_email, message.as_string())
        except:
            return False
    return True

def get_email_body(username, token):
    return """<html><body>
        <p> Hello {},<br>
        in order to complete the registration to Mock Football Bets, click on the link below:<br>
        <a href="http://localhost:5000/confirmation/{}">Confirmation link</a>, no additional action required.<br><br>
        Thank you<br>
        Mock Football Bets <p></body></html>""".format(username, token)

def write_to_file(data, fname):
    with open(fname, 'w') as file:
        json.dump(data, file, indent=4, default=str)

class Fixtures:
    def __init__(self):
        """
        Retrieveal of the json file
        containing upcoming matches
        """
        self.fixtures_information = {}
        if os.path.exists("fixtures.json"):
            with open("fixtures.json", "r") as file:
                self.fixtures_information = json.load(file)

    def add_timezone(self, match_time_str, time_zone):
        """
        Unibet API leaves timezone to 0 GMT - needs to be manually added
        """
        time_format = "%H:%M"
        match_time_datetime_obj = datetime.strptime(match_time_str, time_format)
        match_time_datetime_obj = match_time_datetime_obj + timedelta(hours=time_zone)
        return match_time_datetime_obj.strftime(time_format)

    def filter_useful_data(self, unibet, url):
        """
        Picks important data for the rest of the application
        provided by the Unibet API e. g. home, away, odds, date and time
        """
        required = []
        datetime_length = 16 #yyyy-mm-ddTHH:MM
        dt_date = 10         #yyyy-mm-dd
        to_dec = 1000        #API provided odds are in thousands without a decimal - e.g. 2100 -> odds 2.1
        time_zone = 2
        all_matches = unibet.odds(url)
        for match in all_matches:
            odds = match["full_time_result"]
            odds['home_win'] = odds.pop('1')
            odds['draw'] = odds.pop('X')
            odds['away_win'] = odds.pop('2')
            # parse out from format yyyy-mm-ddTHH:MM:SSZ
            match["date"] = match["time"][0:dt_date]
            time_part = match["time"][dt_date + 1 :  datetime_length]
            match["time"] = self.add_timezone(time_part, time_zone)
            for result, multiplier in odds.items():
                odds[result] = multiplier / to_dec
            required.append({
                "date": match["date"], "time": match["time"],
                "home": match["home_team"], "away": match["away_team"], "odds": odds
            })
        return required

    def gather_unibet_league_sites(self, unibet):
        """
        Collect desired leagues in a dictionary
        - unibet.competitions() uses json hiercharchy for records {nation : { league : website }}
        e. g.
        {
            'Italy': {
                'Serie A': 'https://www.unibet.com/betting/sports/filter/football/italy/serie_a/',
                'Serie B': 'https://www.unibet.com/betting/sports/filter/football/italy/serie_b/',
                'Coppa Italia': 'https://www.unibet.com/betting/sports/filter/football/italy/coppa_italia/',
                ...
                ...
            }
        },
        {
            ...
        }
        """
        leagues = {}
        for state, competition in targeted_competitions.items():
            leagues[state] = unibet.competitions()[state][competition]
        return leagues

    def get_upcoming_matches(self):
        """
        Receives upcoming matches from leagues provided,
        filters and prepares their important data of upcoming matches
        for the front-end of the application
        """
        if not(os.path.exists("historic")) or not(os.path.exists("models")):
            get_csv_files(2010, 2022)
            data_preparation = DataPreparation()
            data_preparation.prepare_all_models()
        result_transform = { "H" : "home", "D" : "draw", "A" : "away"}
        todays_datetime = datetime.today()
        unibet = ApiUnibet()
        given_leagues = self.gather_unibet_league_sites(unibet)
        for nation, url in given_leagues.items():
            values = self.filter_useful_data(unibet, url)
            for match in values:
                match["nation"] = nation
                match_datetime = datetime.fromisoformat(match["date"] + " " + match["time"])
                filename = "models/logr{}.pkl".format(nation)
                home_team, away_team = normalize_team_names(
                    nation, match["home"], match["away"])
                game_info = [
                    [home_team, away_team, match["odds"]["home_win"],
                        match["odds"]["draw"], match["odds"]["away_win"]]
                ]
                #do not allow predictions which are on present matches (or on matches which have been finished already - should have been cleaned up)
                if match_datetime >= todays_datetime and os.path.exists(filename):
                    loaded_mlperc = joblib.load(filename)
                    pred = loaded_mlperc.predict(game_info)
                    match["prediction"] = result_transform[pred[0]]
            self.fixtures_information[nation] = values
        write_to_file(self.fixtures_information, 'fixtures.json')
        return self.fixtures_information

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.data = None
        self.fill_in_credentials()

    def fill_in_credentials(self):
        """
        Estabilish connection with the database
        """
        with open("credentials/db.json", "r") as file:
            self.data = json.load(file)
            try:
                self.connection = mysql.connector.connect(
                    host=self.data["host"],
                    user=self.data["username"],
                    password=self.data["password"],
                    database=self.data["database"]
                )
            except:
                raise Exception("Connection to database could not be estabilished, make sure MySQL is running")
            self.cursor = self.connection.cursor()

app = Flask(__name__)
fixtures = Fixtures()
database = Database()

@app.route("/confirmation/<token>", methods=["POST", "GET"])
def confirmation(token):
    """
    Confirms the registration and transfers the user to a login page
    """
    database.connection.commit()
    return redirect("http://localhost:3000/login")

def insert_into_users_table(user_details):
    """
    SQL query to accomplish the registration in the database
    """
    username = user_details.get("username")
    email = user_details.get("email")
    password = user_details.get("password").encode("utf-8")
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    sql_query = "INSERT INTO `users` (username, email, password) VALUES (%s, %s, %s)"
    values = (username, email, hashed_password)
    try:
        database.cursor.execute(sql_query, values)
    except mysql.connector.IntegrityError as err:
        return False
    return True

def insert_into_balance_table(user_details):
    """
    SQL query to include the user in the balance table
    where the user is provided with an initial balance
    """
    initial_balance = 1000
    username = user_details["username"]
    sql_query_set_balance = "INSERT INTO `balance` (coins, username) VALUES (%s, %s)"
    values_balance = (initial_balance, username)
    database.cursor.execute(sql_query_set_balance, values_balance)

def username_criteria(username):
    """
    Demand proper length and do not allow anything else than alphabetic characters and numbers
    """
    return len(username) >= 5 and len(username) <= 20 and username.isalnum()

def password_criteria(password):
    """
    Demand proper length and at least one character capital
    """
    return len(password) >= 8 and len(password) <= 50 and any(character.isupper() for character in password)

def check_criteria(user_details):
    return username_criteria(user_details["username"]) and password_criteria(user_details["password"])

@app.route("/api/register", methods=["POST"])
def register():
    """
    After filling in the form, data provided by the user
    are checked whether they correspond with the rules provided
    (name/password length and complexity, existence of email)
    """
    if is_empty(request.data):
        return {}
    user_details = json.loads(request.data)
    if not(check_criteria(user_details)):
        return {
            "status": "issue",
            "message": "Criteria have not been satisfied"
        }
    elif not(insert_into_users_table(user_details)):
        return {
            "status": "issue",
            "message": "Username/email already used"
        }
    elif not(send_email(user_details["username"], user_details["email"])):
        return {
            "status" : "issue",
            "message": "Email could not be sent - recipient unknown"
        }
    insert_into_balance_table(user_details)
    database.connection.commit()
    return {
        "status": "complete",
        "message": "Email sent, confirm your registration clicking the link in the email"
    }

@app.route("/api/profile", methods=["GET", "POST"])
def profile_onclick_halt_button():
    """
    After clicking the termination button on the front end in the profile
    page, auto_mode_run function is triggered, however, with the purpose
    to be terminated and cleaned up afterwards
    """
    auto_mode_run(termination=True)
    return {}
    
def save_bets(fname, new_record):
    """
    Save bets made by the user
    - shown on the front-end - Profile page
    """
    if not(os.path.exists(fname)):
        first_record = { "bets" : [ new_record ]}
        write_to_file( first_record, fname)
    else:
        with open(fname, "r+") as file:
            data = json.load(file)
            data["bets"].append(new_record)
            file.seek(0)
            json.dump(data, file, indent=4, default=str)

def receive_hash_password(password):
    """
    Get hash password from the tuple representation (remained after SQL query)
    and return it encoded (required by bcrypt checkpw function)
    """
    if password == None:
        return None
    return "".join(password).encode("utf-8")

def receive_coins():
    """
    Result of a sql query where it is requested
    to get coins of a given user - therefore fetch only one
    """
    coins = None
    try:
        coins = database.cursor.fetchone()[0]
    except:
        return None
    return coins

@ app.route("/api/login", methods=["POST", "GET"])
def login():
    """
    After the user fills in the form credentials,
    the username and password are checked whether they conform
    to the specified combination filled in during the registration
    - the password stored in the db is hashed
    """
    if is_empty(request.data):
        return {}
    user_details = json.loads(request.data)
    username = user_details.get("username")
    password = user_details.get("password").encode("utf-8")
    sql_query_get_hashed_pwd = """SELECT password FROM users WHERE username = %s"""
    database.cursor.execute(sql_query_get_hashed_pwd, (username,))  # needs to be tuple
    h_password = receive_coins()
    result = receive_hash_password(h_password)
    if not(result) or not(bcrypt.checkpw(password, result)):
        return {
            "status": "invalid",
            "message": "Credentials are incorrect"
        }
    else:
        sql_query_get_coins = """SELECT coins FROM balance WHERE username = %s"""
        database.cursor.execute(sql_query_get_coins, (username,) )
        coins = receive_coins()
        return {
            "username": username,
            "balance": coins,
            "status": "valid",
            "message": "Welcome back"
        }


def send_bet_to_db(record, username, bet_cost, game_mode):
    """
    Add keyvalue pairs which are necessary
    for the insertion to the bets table
    """
    record["username"] = username
    record["cost"] = bet_cost
    record["mode"] = game_mode
    record["potential_win"] = record["cost"] * record["odds"]
    insert_bet_into_db(record)

@app.route("/api/bets", methods=["POST"])
@app.route("/api/bets/?mode=auto", methods=["POST"])
def send_bets_data():
    """
    After filling in the form on the page:
    - Mode: auto
    -- deletes possibly previously running machine
    -- subtracts coins from the user's current balance which were given for the new machine
    -- creates setup provided in the json format
    --- by the input values in the front end) for the given user in the auto directory
    --- e. g. auto/auto_tomas.json

    - Mode: normal/assist
    -- see register_accomplished_bet function
    """
    get_mode = request.args.get("mode")
    bet_details = json.loads(request.data)
    if get_mode == "auto":
        bet_details["mode"] = "auto"
        bet_details["current"] = bet_details["cost"]
        if not(os.path.exists("auto")):
            os.makedirs("auto")
        fname = "auto/auto_{}.json".format(bet_details["username"])
        update_users_balance(bet_details)
        if os.path.exists(fname):
            auto_mode_run(database.cursor, termination=True) # terminate the running machine
        write_to_file(bet_details, fname)
        return {}
    else: #normal/assist modes hold almost identical functionality
        return register_accomplished_bet(request.data)

@app.route("/api/bets", methods=["GET"])
def receive_incoming_bets():
    """
    Sends fixtures to the front-end
    """
    return fixtures.fixtures_information

def renew_data(from_year, to_year):
    """
    Once a day - regular renewal of data
    - csv data in the historic directory are formed again
      with (possibly) matches played from the previous day
    - ML models are formed again to (possibly) reflect changes in the historic data
    """
    shutil.rmtree("historic")
    shutil.rmtree("models")
    get_csv_files(from_year, to_year)
    data_prep = DataPreparation()
    data_prep.prepare_all_models()

def normalize_team_names(state, home, away):
    """
    Normalization of team names to numbers for the machine learning part
    of the application which needs to assign numbers to labels - team names provided
    - sklearn LabelEncoder did not work out well since
    multiple pages use different naming conventions for their teams (see directory teams)
    """
    current_line = 1
    line_num_home = line_num_away = 0
    with open("teams/" + state + ".txt", "r") as uniform_team_names:
        for line in uniform_team_names:
            if line_num_home != 0 and line_num_away != 0:
                break
            elif home in line:
                line_num_home = current_line
            elif away in line:
                line_num_away = current_line
            current_line += 1
    return (line_num_home, line_num_away)

def search_elements(url):
    """
    Loads content of the desired url via selenium,
    then desired elements are found in the page source,
    distinguishes between windows chromedriver and the linux one
    """
    path = "/selenium/chromedriver"
    if sys.platform == "win32":
        path += ".exe"
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--log-level=off") #suppress spamming in the console
    driver = webdriver.Chrome(os.getcwd() + path, options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, features="html.parser")
    spans = soup.findAll('span', {'class': 'team-name'})
    return spans

def insert_bet_into_db(bet_details):
    """
    SQL query to register bet desired by the user
    """
    query_parameters = (
        bet_details["date"], bet_details["nation"], bet_details["team"],
        bet_details["home"], bet_details["away"], bet_details["odds"], 
        bet_details["cost"], bet_details["potential_win"],
        bet_details["username"], bet_details["mode"]
    )
    fname = "present/" + bet_details["username"] + ".json"
    sql_query_place_bet ="""INSERT INTO bet(date, nation,
    team, home, away, odds, cost, potential_win, username, mode) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    if not(os.path.exists("present")):
        os.mkdir("present")
    if bet_details["mode"] == "human":
        save_bets(fname, bet_details)
    database.cursor.execute(sql_query_place_bet, query_parameters)

def register_accomplished_bet(data):
    """
    Updates user's balance in the database,
    inserts the bet to the database
    """
    bet_details = json.loads(data)
    bet_details["mode"] = "human"
    if "odds" not in bet_details and "team" not in bet_details:
        return {
            "status": "invalid",
            "message": "Bet could not be processed"
        }
    current_balance = update_users_balance(bet_details)
    insert_bet_into_db(bet_details)
    database.connection.commit()
    return {
        "status": "valid",
        "message": "Bet registered",
        "balance" : current_balance
    }

def evaluate_bet_results(placed_bets):
    """
    Loads the goal.com results page for the matches whose result is already known,
    checks the result of the game and compares it with the
    team (or draw) picked by the user
    """
    results = []
    evaluated_bets = []
    win_pos = 7
    home_pos = 3
    for bet in placed_bets:
        potential_win = bet[win_pos]
        date = bet[0]
        nation = bet[1]
        bet_on_team = bet[2]
        home_team = bet[home_pos]
        url = "https://www.goal.com/en-in/results/{}".format(date)
        # bets with matches on the same day or later are not evaluated - the results are not published yet
        other = datetime(date.year, date.month, date.day).date()
        current = datetime.now().date()
        if other >= current:
            continue
        spans = search_elements(url)
        teams = []
        score = []
        for record in spans:
            home_team_eq_names = []
            with open("teams/" + nation + ".txt", "r", encoding="utf-8") as file:
                for line in file:
                    if home_team in line:
                        home_team_eq_names = line.rstrip("\n").split(",")
            if record.text in home_team_eq_names:
                parent = record.find_parent("div")
                grand_parent = parent.find_parent("div")
                team_elements = grand_parent.findAll(
                    'span', {'class': 'team-name'})
                score_elements = grand_parent.findAll(
                    'span', {'class': 'goals'})
                for team, goals in zip(team_elements, score_elements):
                    teams.append(team.text)
                    score.append(goals.text)
                evaluated_bets.append(bet)
        if is_empty(score):
            continue #not evaluated yet
        if((bet_on_team == "draw" and score[0] == score[1])
        or (bet_on_team == teams[0] and score[0] > score[1])
        or (bet_on_team == teams[1] and score[0] < score[1])):
            results.append(potential_win)
        else:
            results.append(0)
    return results, evaluated_bets

def update_users_balance(bet_details):
    """
    SQL query to change user's current balance
    (either subtracting money while betting or adding while getting paid back)
    """
    owner = bet_details["username"]
    cost = float(bet_details["cost"])
    balance = float(bet_details["balance"])
    current = balance - cost
    sql_query_subtract_coins = """UPDATE balance SET coins = %s WHERE username = %s"""
    database.cursor.execute(sql_query_subtract_coins, (current, owner))
    return current

def pay_wins(games_won, bets):
    """
    For each placed bet checks whether and how much money
    the user won, for the machine the amount of money is updated
    in its auto setup json file
    """
    profit = 0
    home_pos = 3
    odds_pos = 5
    if not(os.path.exists("bets")):
        os.makedirs("bets")
    #bet arr element - date nation team home away odds cost potential_win username
    for win, bet in zip(games_won, bets):
        date = bet[0]
        candidate = bet[home_pos - 1]
        home = bet[home_pos]; away = bet[home_pos + 1]
        odds = bet[odds_pos]; cost = bet[odds_pos + 1]
        mode = bet[len(bet) - 1]; username = bet[len(bet) - 2]
        past_games_fname = "bets/" + username + ".json"
        current_games_fname = "present/" + username + ".json"
        auto_fname = "auto/auto_" + username + ".json"
        new_record = {
            "home" : home, "away" : away, "candidate" : candidate,
            "username" : username, "date" : date, "profit" : win,
            "odds" : odds, "cost" : cost, "mode" : mode
        }
        if mode == "human":
            profit += win
        else:
            with open(auto_fname, "r") as r_file:
                change_data = json.load(r_file)
                change_data["cost"] += win
                with open(auto_fname, "w") as w_file:
                    json.dump(change_data, w_file)
        
        params = (date, candidate, home, away, username)
        sql_query_delete_placed_bet = """DELETE FROM bet WHERE date = %s
        and team = %s and home = %s and away = %s and username = %s"""
        database.cursor.execute(sql_query_delete_placed_bet, params)
        with open("present/" + current_games_fname) as file:
            data = json.load(file)
            for element in data:
                if element["bets"]["home"] == bet[home_pos] and element["bets"]["away"] == bet[home_pos + 1]:
                    del element
        save_bets(past_games_fname, new_record)
    #database.connection.commit()
    return profit

def update_balance_in_db():
    """
    Once a day
    - evaluates bets of matches which took place the day before (of each user), pays the wins
    - if the amount is lower than 10 coins, the user is provided with 10 coins as the minimal value
    -- in order to keep players involved in the game
    """
    minimum_amount = 10
    digits_after_decimal = 2
    sql_query_rec_coins_and_unames = """SELECT * from balance"""   
    sql_query_get_placed_bets = """SELECT * FROM bet WHERE username = %s"""
    sql_query_add_profit_to_user = """UPDATE balance SET coins = %s WHERE username = %s"""
    database.cursor.execute(sql_query_rec_coins_and_unames)
    for coins, username in database.cursor.fetchall():
        database.cursor.execute(sql_query_get_placed_bets, (username,))
        bets = []
        for record in database.cursor.fetchall():
            bets.append(record)
        games_won, evaluated_bets = evaluate_bet_results(bets)
        profit = pay_wins(games_won, evaluated_bets)
        coins += round(profit, digits_after_decimal)
        if coins < minimum_amount:
            coins = minimum_amount
        params = (coins, username)
        database.cursor.execute(sql_query_add_profit_to_user, params)
    database.connection.commit()

def change_mode_for_ongoing_auto_bets(username):
    """
    As soon as the user decides to halt the auto bets mode, all placed bets are
    overwritten as if the user placed them himself
    """
    parameters = ("human", username)
    sql_query_change_mode = """UPDATE bet SET mode = %s WHERE username = %s"""
    database.cursor.execute(sql_query_change_mode, parameters)

def auto_termination_cleanup(filename, username, coins):
    """
    Remaining balance which has been possessed by the machine is sent back
    to the user, automode file setup is deleted afterwards
    """
    sql_query_get_coins = """SELECT coins FROM balance WHERE username = %s"""
    database.cursor.execute(sql_query_get_coins, (username,))  # needs to be tuple
    balance = receive_coins()
    update_users_balance({"username" : username, "cost" : -coins, "balance" : balance})
    os.remove("auto/" + filename)
    change_mode_for_ongoing_auto_bets(username)
    database.connection.commit()
    
def filter_betting_on_same_match(bet_on_matches, home_team, away_team):
    """
    Reduce candidates which have had a bet placed already
    """
    for match in bet_on_matches:
        if home_team == match["home"] and away_team == match["away"]:
            bet_on_matches.remove(match)
    return bet_on_matches

def load_model(fname, method):
    """
    Load a pretrained ML model of a particular league and method used
    """
    model = joblib.load(
        "models/{}{}.pkl".format(method, fname.partition(".")[0])
    )
    return model

def auto_mode_run(termination=False):
    """
    With termination flag off:
    For each user who previously declared that he wants to use auto mode,
    the program goes through each upcoming match of specified leagues
    and loads ML models - compares results of each and upon constraints decides which matches
    are proper candidates and which should be filtered straightaway - see "How to decide which match should be chosen"
    The amount of money which was devoted to the bets are subtracted form the initial balance
    included in the json file

    How to decide which match should be chosen
    -- decides whether to bet based on the value of the odds multiplier times "confidence level"
    (majority of ML models on the vote for the result of the match)
    -- has limited number of bets
    -- it is not allowed to bet on previously accomplished bet (including human ones)
    -- economy "strategy" - leave 1/(#of matches + 1) aside, the rest is used equally on each match
    """
    data = {}
    if not os.path.exists("auto"):
        return
    for filename in os.listdir("auto"):
        with open ("auto/" + filename, "r") as file:
            data = json.load(file)

        username = data["username"]
        coins = float(data["cost"]);current_coins = float(data["current"])
        minimum_balance_perc = 0.1
        picked_leagues = data["leagues"]; risk = float(data["risk"]);
        risk_mode = int(data["risk_mode"]); game_mode = data["mode"]
        ml_models = ["logr", "svm", "dtree", "gradb", "randf", "sgd", "mlperc"]
        bet_on_matches = []; max_amount_of_bets = 5
        decimal_nums = 2; minimum_confidence_for_bet = 10
        fixtures = {}
        home_pos = 3 #index in the table

        todays_datetime = datetime.today()
        end_datetime =  datetime.fromisoformat(data["until"])
        
        if todays_datetime > end_datetime or termination:
            auto_termination_cleanup(filename, username, coins)
            continue
        elif current_coins < coins * minimum_balance_perc:
            """machine needs to wait to finish its own bets 
            or needs to wait until termination with insufficient funds"""
            continue
        with open('fixtures.json', 'r') as file:
            fixtures = json.load(file)
        for league in picked_leagues:
            league_matches = fixtures[league]
            for match in league_matches:
                stats = { "H" : 0, "D" : 0, "A" : 0}
                home_team, away_team = normalize_team_names(
                    league, match["home"], match["away"]
                )
                game_info = [[
                    home_team, away_team, match["odds"]["home_win"],
                        match["odds"]["draw"], match["odds"]["away_win"]
                ]]
                for model in ml_models:
                    loaded = load_model(league, model)
                    prediction = loaded.predict(game_info)[0]
                    stats[prediction] += 1
                maximum = max(stats, key=stats.get)
                if stats[maximum] >= risk_mode:
                    if maximum == "H" and match["odds"]["home_win"] <= risk:
                        match["odds"] = match["odds"]["home_win"]
                        match["team"] = match["home"]
                    elif maximum == "D" and match["odds"]["draw"] <= risk:
                        match["odds"] = match["odds"]["draw"]
                        match["team"] = "draw"
                    elif (maximum == "A" and match["odds"]["away_win"] <= risk):
                        match["odds"] = match["odds"]["away_win"]
                        match["team"] = match["away"]
                    else:
                        continue
                    match["value"] = float(match["odds"]) * stats[maximum]
                    if match["value"] < minimum_confidence_for_bet:
                        continue
                    match["certainty"] = stats[maximum]
                    match["nation"] = league
                    bet_on_matches.append(match)
        sql_query_get_placed_bets = """SELECT * FROM bet WHERE username = %s"""
        database.cursor.execute(sql_query_get_placed_bets, (data["username"],))
        for record in database.cursor.fetchall():
            bet_on_matches = filter_betting_on_same_match(bet_on_matches, record[home_pos], record[home_pos + 1])
        bet_on_matches.sort(key = lambda json: json["value"], reverse=True)
        best_candidates = {}
        if len(bet_on_matches) > max_amount_of_bets:
            best_candidates = bet_on_matches[0 : max_amount_of_bets]
        elif len(bet_on_matches) != 0:
            best_candidates = bet_on_matches
        else:
            return {}
        each_bet_cost = round(current_coins / (len(best_candidates) + 1), decimal_nums)
        for record in best_candidates:
            send_bet_to_db(record, username, each_bet_cost, game_mode)
        total_cost = each_bet_cost * len(best_candidates)
        with open("auto/" + filename, "r") as r_file:
            change_data = json.load(r_file)
            change_data["current"] = current_coins - total_cost
            with open("auto/" + filename, "w") as w_file:
                json.dump(change_data, w_file)
        database.connection.commit()

"""
Scheduled jobs of the functions above
"""
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=renew_data, args = [2010, 2022], trigger="cron",
    day_of_week ="mon-sun", hour=0, minute=00
)
scheduler.add_job(
    func=auto_mode_run, trigger="cron",
    day_of_week ="mon-sun", hour=0, minute=15
)
scheduler.add_job(
    func=update_balance_in_db,
    trigger="cron",
    day_of_week ="mon-sun", hour=2, minute=00
    #it needs to be at least 02:00 - the time when goal.com uploads their results website
)
scheduler.add_job(
    func=fixtures.get_upcoming_matches, trigger='interval', seconds=20
)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
