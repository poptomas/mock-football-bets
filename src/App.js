import Home from "./Pages/Home"
import Register from "./Pages/Register"
import Login from "./Pages/Login"
import Bets from "./Pages/Bets"
import Profile from "./Pages/Profile"
<<<<<<< HEAD
import {BrowserRouter as Router, Switch, Route, Link, withRouter} from "react-router-dom";
=======
import {BrowserRouter as Router, Switch, Route, Link} from "react-router-dom";
>>>>>>> api-flask-react

import React from "react";

export default function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/register">Register</Link>
            </li>
            <li>
              <Link to="/login">Login</Link>
            </li>
            <li>
              <Link to="/profile">Profile</Link>
            </li>
            <li>
              <Link to="/bets">Bets</Link>
            </li>
          </ul>
        </nav>

        {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Switch>
            <Route exact path="/">
                <Home />
            </Route>
            <Route path="/register">
                <Register/>
            </Route>
            <Route path="/login">
                <Login/>
            </Route>
            <Route path="/profile">
                <Profile />
            </Route>
            <Route path="/bets">
                <Bets />
            </Route>

        </Switch>
      </div>
    </Router>
  );
<<<<<<< HEAD
}

function About() {
  return <h2>About</h2>;
}

function Users() {
  return <h2>Users</h2>;
}


function NavBar(){
    return(
        <Router>
            <nav>
            <ul>
                <li> <Link to="/home">Home</Link> </li>
                <li> <Link to="/register">Register</Link> </li>
                <li> <Link to="/login">Login</Link> </li>
                <li> <Link to="/profile">Profile</Link> </li>
                <li> <Link to="/bets">Bets</Link> </li>
            </ul>
            </nav>

            {/* A <Switch> looks through its children <Route>s and
                renders the first one that matches the current URL. */}
            <Switch>
                <Route exact path="/" component = {withRouter(Home)}> </Route>
                <Route path="/register" component = {withRouter(Register)}> </Route>
                <Route path="/login" component = {withRouter(Login)}> </Route>
                <Route path="/profile" component = {withRouter(Profile)}> </Route>
                <Route path="/bets" component = {withRouter(Bets)}> </Route>
            </Switch>
        </Router>
    )
}

=======
}
>>>>>>> api-flask-react
