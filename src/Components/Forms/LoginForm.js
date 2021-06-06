import React, {useState} from 'react'
import { useHistory } from "react-router-dom";

export const LoginForm = () => {
    const history = useHistory();
    const [state, setState] = useState({username : "", password : ""})
  
    const handleChange = event => {
        const value = event.target.value
         setState({
            ...state,
            [event.target.name] : value
        });
    }
  
    const handleSubmit = event => {
        event.preventDefault();
        const request = {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                username : state.username,
                password : state.password
            })
        };

        fetch("api/login", request)
            .then(response => 
                response.json())
            .then(json => {
                setState({ userData : json })
                console.log(json);
                if(json.status === "valid")
                    history.push("/bets")
            })
            .catch( () => {
                console.log("Error encountered")
            })
    }
  
    return (
            <form onSubmit={handleSubmit}>
            <label> Username: </label><br/>
            <input type="text" value={state.username || ""} name = "username" onChange={handleChange} autoComplete="on" required />
            
            <br/><label> Password: </label><br/>
            <input type="password" value={state.password || ""} name = "password" onChange={handleChange} autoComplete="off" required />
            <br/>
            <input type="submit" value="Submit" />
            </form>
    )
}