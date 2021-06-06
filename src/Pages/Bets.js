import React, {useState, useEffect} from 'react';
import {Header} from '../Components/Card/card';

import {getApiKey} from "../Private/Credentials"

export const Bets = () => {
    const url = "https://api.football-data.org/v2/matches";
    const [state, setState] = useState({})

    const request = {
        method : "GET",
        headers : {
            "X-Auth-Token": getApiKey(),
            "Content-Type" : "text/plain"
        }
    };

    useEffect( () => {
        fetch(url, request)
        .then(response => {
            return response.json()
        })
        .then(json => {
            setState({matches : json.matches})
            /*
            console.log(state.matches === undefined)
            state.matches !== undefined ?
                state.matches.map (
                    match => { 
                        return match
                    }
                )
                : console.log("failed")
            */
        })
    }, [url])

    return(
        <div>
            <Header />
            <h1>Bets</h1>
            <p>TBD</p>
            <table>
            <thead>
            <tr>
                <th>Home Team</th>
                <th>Away Team</th>
                <th>Date and time</th>
            </tr>
            </thead>
            <tbody>
            {
                state.matches !== undefined ?
                state.matches.map (
                    (match, idx) => { return (
                        <tr>
                            <td>{match.homeTeam.name}</td>
                            <td>{match.awayTeam.name}</td>
                            <td>{match.utcDate}</td>
                        </tr>
                    )
                }) : <tr><td></td></tr>
            }
            </tbody>
            </table>
        </div>

    );
};

export default Bets;